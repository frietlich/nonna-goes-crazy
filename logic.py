"""The rules of Nonna Goes Crazy: demand, sales and money.

The menu lives here and not in the database on purpose. Prices are rules, not a
saved game: they have to be the same on every machine, and the database file
never leaves the laptop it was made on.
"""

import db

# The menu. Fixed, and the same everywhere. See docs/product-brief.md.
MENU = [
    {"name": "Iconic Pomodoro", "cost": 7.00, "price": 11.90},
    {"name": "Drunken Arrabbiata", "cost": 9.00, "price": 12.90},
    {"name": "Carbobora", "cost": 11.00, "price": 14.00},
]

STARTING_CASH = 100.00
TOTAL_DAYS = 5

KITCHEN_IS_EMPTY = "The kitchen is empty. Order some ingredients first."
RUN_IS_OVER = "Five days are done. The kitchen is closed."
CANNOT_AFFORD = "That order costs more than the till holds."


def money(amount):
    """Round to the cent (CT R3).

    Every money result goes through here. Rounding once at the end would not be
    enough: plain floating point drifts as the days add up, and cash would show
    135.39999999999998 on day three.
    """
    return round(amount, 2)


def dish_names():
    """The names on the menu, in menu order."""
    return [dish["name"] for dish in MENU]


def find_dish(name):
    """Return one dish from the menu, or None if there is no such dish."""
    for dish in MENU:
        if dish["name"] == name:
            return dish
    return None


def start_up():
    """Make sure there is a game to play. Safe to call on every page load."""
    db.set_up(dish_names(), STARTING_CASH)


# ---------------------------------------------------------------- reading

def current_cash():
    return money(db.get_cash())


def current_day():
    return db.get_day()


def current_stock():
    return db.get_stock()


def history():
    return db.get_history()


def kitchen_is_empty():
    """True when there is not a single portion of anything."""
    return sum(current_stock().values()) == 0


def run_is_over():
    """True once the fifth day has been served. Buying and trading stop (CT05)."""
    return current_day() > TOTAL_DAYS


def stock_value():
    """What is left in the kitchen, valued at what it cost to buy (CT R4).

    Unsold stock is not waste: it is money that has not been turned back into
    cash yet, and the final result counts it.
    """
    stock = current_stock()
    total = 0.0
    for dish in MENU:
        total = total + stock[dish["name"]] * dish["cost"]
    return money(total)


def leftovers():
    """What is still in the kitchen, dish by dish, with what each lot cost.

    Only dishes that actually have portions left. An empty list means the
    kitchen is clean and the end screen says nothing about it.
    """
    stock = current_stock()
    left = []
    for dish in MENU:
        portions = stock[dish["name"]]
        if portions > 0:
            left.append(
                {
                    "name": dish["name"],
                    "portions": portions,
                    "value": money(portions * dish["cost"]),
                }
            )
    return left


def final_result():
    """The scoreboard after the fifth day (CT05).

    Overall gain or loss is the final cash plus the stock still in the kitchen
    at purchase cost, minus the EUR 100 the run started with (CT R4).
    """
    days = []
    per_dish = {dish["name"]: {"sold": 0, "revenue": 0.0, "profit": 0.0} for dish in MENU}
    sold_total = 0
    revenue_total = 0.0
    profit_total = 0.0

    for day in history():
        day_sold = 0
        day_profit = 0.0
        for name, line in day["dishes"].items():
            per_dish[name]["sold"] = per_dish[name]["sold"] + line["sold"]
            per_dish[name]["revenue"] = money(per_dish[name]["revenue"] + line["revenue"])
            per_dish[name]["profit"] = money(per_dish[name]["profit"] + line["profit"])
            day_sold = day_sold + line["sold"]
            day_profit = money(day_profit + line["profit"])
        days.append(
            {
                "day": day["day"],
                "sold": day_sold,
                "revenue": day["cash_delta"],
                "profit": day_profit,
                "cash_after": day["cash_after"],
            }
        )
        sold_total = sold_total + day_sold
        revenue_total = money(revenue_total + day["cash_delta"])
        profit_total = money(profit_total + day_profit)

    cash = current_cash()
    left = stock_value()
    return {
        "days": days,
        "dishes": per_dish,
        "sold": sold_total,
        "revenue": revenue_total,
        "profit": profit_total,
        "cash": cash,
        "stock_value": left,
        "leftovers": leftovers(),
        "gain": money(cash + left - STARTING_CASH),
    }


def start_new_run():
    """Throw the finished run away and open again on day one with EUR 100."""
    db.wipe()
    start_up()


# ---------------------------------------------------------------- ordering

def order_total(quantities):
    """What an order costs: sum of quantity x unit cost (CT R3)."""
    total = 0.0
    for name, quantity in quantities.items():
        dish = find_dish(name)
        if dish is not None:
            total = total + quantity * dish["cost"]
    return money(total)


def can_afford(quantities):
    """True when the whole order fits in the cash on hand (CT02)."""
    return order_total(quantities) <= current_cash()


def place_order(quantities):
    """Buy ingredients: cash down and stock up, in the same step (CT02).

    Returns the amount spent, or None when the order cannot be paid for. An
    order that is refused writes nothing at all.
    """
    if run_is_over():
        return None
    total = order_total(quantities)
    if total > current_cash():
        return None

    stock = current_stock()
    for name, quantity in quantities.items():
        if name in stock:
            stock[name] = stock[name] + quantity

    db.save_order(money(current_cash() - total), stock)
    return total


# ---------------------------------------------------------------- trading

def buy_and_open(quantities):
    """Buy what the owner typed, then serve the day (CT02, CT04).

    One handle instead of two: ordering and opening were never separate
    decisions. Whatever is bought here is in the kitchen for this very day.

    Nothing happens by halves. If the order cannot be paid for, the day is not
    served either and not a cent moves -- no stock bought for a day that then
    never opens.
    """
    if run_is_over():
        return {"ok": False, "error": RUN_IS_OVER}

    if order_total(quantities) > 0:
        if not can_afford(quantities):
            return {"ok": False, "error": CANNOT_AFFORD}
        place_order(quantities)

    return open_the_restaurant()


def demand_for(dish, price):
    """How many portions people want at this price (CT R1). No randomness.

    Ten at or below the reference price, five above it up to twice the
    reference, none above that.
    """
    if price <= dish["price"]:
        return 10
    if price <= 2 * dish["price"]:
        return 5
    return 0


def open_the_restaurant():
    """Trade one day (CT04), or refuse when the kitchen is empty.

    Returns a dict. On a refusal it carries ok=False and the message the screen
    shows in red, and nothing is written. On a completed day it carries the
    per-dish result, the new cash and the change in cash.
    """
    if run_is_over():
        return {"ok": False, "error": RUN_IS_OVER}
    if kitchen_is_empty():
        return {"ok": False, "error": KITCHEN_IS_EMPTY}

    day = current_day()
    stock = current_stock()
    lines = {}
    revenue_total = 0.0

    for dish in MENU:
        name = dish["name"]
        price = dish["price"]          # CT03 is out of scope: always the reference
        stock_before = stock[name]
        sold = min(demand_for(dish, price), stock_before)
        revenue = money(sold * price)
        cogs = money(sold * dish["cost"])

        lines[name] = {
            "stock_before": stock_before,
            "sold": sold,
            "revenue": revenue,
            "cogs": cogs,
            "profit": money(revenue - cogs),
            "stock_after": stock_before - sold,
        }
        stock[name] = stock_before - sold
        revenue_total = money(revenue_total + revenue)

    cash_after = money(current_cash() + revenue_total)
    db.save_day(day, lines, cash_after, revenue_total, stock)

    return {
        "ok": True,
        "day": day,
        "dishes": lines,
        "cash_after": cash_after,
        "cash_delta": revenue_total,
    }
