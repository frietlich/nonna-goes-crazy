"""The rules of Nonna Goes Crazy: demand, sales and money.

The menu lives here and not in the database on purpose. Prices are rules, not a
saved game: they have to be the same on every machine, and the database file
never leaves the laptop it was made on.
"""

from decimal import Decimal, ROUND_HALF_UP

import db

# The menu. Fixed, and the same everywhere. See docs/product-brief.md.
MENU = [
    {"name": "Iconic Pomodoro", "cost": 7.00, "price": 11.90,
     "picture": "iconic-pomodoro.png"},
    {"name": "Drunken Arrabbiata", "cost": 9.00, "price": 12.90,
     "picture": "drunken-arrabbiata.png"},
    {"name": "Carbobora", "cost": 11.00, "price": 14.00,
     "picture": "carbobora.png"},
]

STARTING_CASH = 100.00
TOTAL_DAYS = 5

KITCHEN_IS_EMPTY = "The kitchen is empty. Order some ingredients first."
RUN_IS_OVER = "Five days are done. The kitchen is closed."
CANNOT_AFFORD = "That order costs more than the till holds."
BAD_PRICE = "Every price has to be more than zero."

# The demand rule in words, for the screen to show (CT03).
DEMAND_RULE = (
    "At or below the reference price people want 10 portions \u00b7 "
    "up to twice it, 5 \u00b7 above that, none."
)


def money(amount):
    """Round to the cent, the way money is rounded: half goes up (CT R3).

    Every money result goes through here. Rounding once at the end would not be
    enough: plain floating point drifts as the days add up, and cash would show
    135.39999999999998 on day three.

    Python's own round() rounds a half to the nearest even number, so 2.675
    would become 2.67. Nobody hands back 2.67 for two euros sixty-seven and a
    half, so Decimal does it properly instead.
    """
    return float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


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
    db.set_up({dish["name"]: dish["price"] for dish in MENU}, STARTING_CASH)


# ---------------------------------------------------------------- reading

def current_cash():
    return money(db.get_cash())


def current_day():
    return db.get_day()


def current_stock():
    return db.get_stock()


def history():
    return db.get_history()


def current_prices():
    """What the owner is charging today, dish by dish.

    A new run opens at the reference price and the owner moves it from there.
    Yesterday's price stays until it is changed: it was chosen on purpose, and
    retyping it every morning would be busywork.
    """
    return db.get_prices()


def set_prices(prices):
    """Store the chosen selling prices. Every one has to be above zero (A2).

    Returns False and writes nothing when any price is wrong, so a bad entry
    cannot leave half the menu changed.
    """
    for price in prices.values():
        if price is None or price <= 0:
            return False
    db.save_prices({name: money(price) for name, price in prices.items()})
    return True


def kitchen_is_empty():
    """True when there is not a single portion of anything."""
    return sum(current_stock().values()) == 0


def run_is_over():
    """True once the fifth day has been served. Buying and trading stop (CT05)."""
    return current_day() > TOTAL_DAYS


def is_bankrupt():
    """Nothing in the kitchen, and not enough left to buy even the cheapest dish.

    Without this the run would sit on the same day for ever: opening is refused
    because the kitchen is empty, shopping is refused because the till is
    short, and the scoreboard -- with it the only way to start again -- would
    never be reached.
    """
    if run_is_over():
        return False
    cheapest = min(dish["cost"] for dish in MENU)
    return kitchen_is_empty() and current_cash() < cheapest


def run_has_started():
    """True once anything has happened: a day played, food bought, money spent.

    A brand new run has none of those, so the menu can offer "start" rather
    than "continue" and never ask to confirm deleting nothing.
    """
    return (
        current_day() > 1
        or not kitchen_is_empty()
        or current_cash() != STARTING_CASH
        or len(history()) > 0
    )


def run_has_ended():
    """True when there is nothing left to play: five days served, or broke."""
    return run_is_over() or is_bankrupt()


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
        "bankrupt": is_bankrupt(),
        "days_played": current_day() - 1,
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

def buy_and_open(quantities, prices=None):
    """Set the prices, buy what the owner typed, then serve the day (CT02-CT04).

    One handle instead of three: pricing, ordering and opening were never
    separate decisions. Whatever is bought here is in the kitchen for this very
    day, and sold at the price set here.

    Nothing happens by halves. A price that is not allowed or an order that
    cannot be paid for stops everything, and not a cent moves -- no stock
    bought for a day that then never opens.
    """
    if run_is_over():
        return {"ok": False, "error": RUN_IS_OVER}

    if prices is not None and not set_prices(prices):
        return {"ok": False, "error": BAD_PRICE}

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
    prices = current_prices()
    lines = {}
    revenue_total = 0.0
    cogs_total = 0.0
    sold_total = 0

    for dish in MENU:
        name = dish["name"]
        price = prices[name]           # what the owner is charging (CT03)
        stock_before = stock[name]
        sold = min(demand_for(dish, price), stock_before)
        revenue = money(sold * price)
        cogs = money(sold * dish["cost"])

        lines[name] = {
            "price": price,
            "stock_before": stock_before,
            "sold": sold,
            "revenue": revenue,
            "cogs": cogs,
            "profit": money(revenue - cogs),
            "stock_after": stock_before - sold,
        }
        stock[name] = stock_before - sold
        revenue_total = money(revenue_total + revenue)
        cogs_total = money(cogs_total + cogs)
        sold_total = sold_total + sold

    cash_after = money(current_cash() + revenue_total)
    db.save_day(day, lines, cash_after, revenue_total, stock)

    return {
        "ok": True,
        "day": day,
        "dishes": lines,
        # CT04 asks for the day in total as well as dish by dish.
        "sold": sold_total,
        "revenue": revenue_total,
        "cogs": cogs_total,
        "profit": money(revenue_total - cogs_total),
        "cash_after": cash_after,
        "cash_delta": revenue_total,
    }
