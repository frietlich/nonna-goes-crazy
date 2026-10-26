"""Nonna Goes Crazy: the screens. Start it with:  uv run streamlit run app.py"""

import time

import streamlit as st

import logic

st.set_page_config(page_title="Nonna Goes Crazy", page_icon="🍝", layout="wide")

# Build the database on first use. Safe to call on every run.
logic.start_up()

INK = "#2B2E7E"       # the blue of the sign
PINK = "#D7446B"      # the accent
CREAM = "#F6EEDC"     # the wall behind the tiles

# How long the kitchen takes. Long enough to feel like a service, short enough
# that nobody goes and makes a coffee.
COOKING_SECONDS = 6.0
COOKING_LINES = [
    "Water is boiling…",
    "Nonna is cooking…",
    "The room is filling up…",
    "Plates are going out…",
]


def paint_the_room():
    """Cream tiles on the floor, ink blue lettering, pink for anything that acts."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: """ + CREAM + """;
            background-image:
                linear-gradient(45deg, rgba(43,46,126,.045) 25%, transparent 25%,
                                transparent 75%, rgba(43,46,126,.045) 75%),
                linear-gradient(45deg, rgba(43,46,126,.045) 25%, transparent 25%,
                                transparent 75%, rgba(43,46,126,.045) 75%);
            background-size: 54px 54px;
            background-position: 0 0, 27px 27px;
        }
        h1, h2, h3 { color: """ + INK + """ !important; letter-spacing: .02em; }
        .stApp, .stApp p, .stApp label, .stApp td, .stApp th { color: """ + INK + """; }

        .sign {
            text-align: center;
            margin: 3.5rem 0 1rem 0;
            line-height: .92;
        }
        .sign .big {
            font-family: Georgia, "Times New Roman", serif;
            font-weight: 700;
            font-size: 4.6rem;
            color: """ + INK + """;
            letter-spacing: .04em;
        }
        .sign .small {
            font-family: Georgia, serif;
            letter-spacing: .42em;
            font-size: .78rem;
            color: """ + PINK + """;
            margin-top: 1.1rem;
        }
        .rule {
            height: 3px;
            background: """ + PINK + """;
            width: 160px;
            margin: 1.6rem auto;
            opacity: .75;
        }
        .cooking {
            text-align: center;
            font-family: Georgia, serif;
            font-style: italic;
            font-size: 1.15rem;
            color: """ + PINK + """ !important;
            margin-bottom: .6rem;
        }
        /* Streamlit's own bar sits on top of the page and swallows the sign.
           A game does not need it. */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stToolbar"] { display: none; }

        /* Streamlit's default padding alone is taller than a phone. */
        [data-testid="stMainBlockContainer"] {
            padding-top: 4.2rem; padding-bottom: 3rem;
            padding-left: 3.5rem; padding-right: 3.5rem;
            max-width: 100%;
        }
        [data-testid="stVerticalBlock"] { gap: 1.45rem; }

        .topsign {
            font-family: Georgia, serif; font-weight: 700;
            font-size: 2.6rem; color: """ + INK + """;
            letter-spacing: .05em; line-height: 1;
        }
        .topsign small {
            display: block; font-size: .62rem; font-weight: 400;
            letter-spacing: .34em; color: """ + PINK + """; margin-top: .5rem;
        }
        .stat { text-align: right; line-height: 1.1; }
        .stat span { font-size: .7rem; letter-spacing: .14em; color: """ + PINK + """; }
        .stat b { display: block; font-family: Georgia, serif; font-size: 2.1rem; color: """ + INK + """; }

        .head { font-family: Georgia, serif; font-size: 1.5rem; color: """ + INK + """;
                border-bottom: 2px solid """ + PINK + """; padding-bottom: .5rem;
                margin: 1.9rem 0 1.3rem 0; }
        .th { font-size: .68rem; letter-spacing: .14em; color: """ + PINK + """;
              text-transform: uppercase; padding-bottom: .5rem; }
        /* Natural height on purpose. Forcing these cells to the height of the
           number box pushed them out of the centring Streamlit had already
           worked out, which is what put the rows 8px out of line. */
        /* Every cell is exactly as tall as a Streamlit number box and centres
           its own content. Streamlit's vertical_alignment does not reach these
           rows, which is what left the boxes sitting 8px above their text. */
        .td {
            min-height: 40px; display: flex; align-items: center;
            font-size: 1.05rem; color: """ + INK + """;
        }
        .td.name { font-family: Georgia, serif; font-size: 1.15rem; }
        .td.name { flex-direction: column; align-items: flex-start; justify-content: center; }
        .ref {
            font-family: -apple-system, system-ui, sans-serif;
            font-size: .62rem; letter-spacing: .1em; text-transform: uppercase;
            color: """ + PINK + """; opacity: .85; margin-top: .1rem;
        }
        .rule-note {
            font-size: .82rem; color: """ + INK + """; opacity: .8;
            border-left: 3px solid """ + PINK + """; padding: .35rem .7rem;
            margin: 1rem 0 .2rem 0;
        }
        .td, .th { white-space: nowrap; }
        .num { justify-content: flex-end; text-align: right; }
        .total { font-family: Georgia, serif; font-size: 1.5rem; color: """ + INK + """;
                 text-align: right; padding: 1.2rem 0 .4rem 0;
                 border-top: 1px solid rgba(43,46,126,.18); margin-top: .6rem; }
        .warn { color: """ + PINK + """ !important; }
        .quiet { font-size: .8rem; opacity: .75; }

        .closed {
            text-align: center; font-family: Georgia, serif;
            letter-spacing: .3em; font-size: .8rem;
            color: """ + PINK + """; margin-top: .4rem;
        }
        .verdict {
            text-align: center; font-family: Georgia, serif;
            font-size: 3.4rem; color: """ + INK + """;
            line-height: 1; margin: .8rem 0 .3rem 0;
        }
        .ledger {
            text-align: center; font-size: .98rem;
            color: """ + INK + """; opacity: .85; margin-bottom: .6rem;
        }
        .ledger b { color: """ + PINK + """; }
        .leftover {
            text-align: center; font-size: .92rem; color: """ + INK + """;
            margin: -.2rem 0 .7rem 0;
        }
        .leftover .tag {
            font-size: .64rem; letter-spacing: .18em; color: """ + PINK + """;
            display: block; margin-bottom: .35rem;
        }
        .leftover b { color: """ + PINK + """; }
        .foot { border-top: 1px solid rgba(43,46,126,.2); margin-top: .3rem; }

        div[data-testid="stNumberInput"] input { padding: .5rem .6rem; font-size: 1rem; }
        .stButton > button { padding: .95rem 1rem; font-size: 1.05rem; }
        .quiet { margin-top: .8rem; }
        div[data-testid="stMetricValue"] { color: """ + INK + """; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def euro(amount):
    """Money on screen always has two decimals: 8.20 and not 8.2."""
    return "€" + format(amount, ".2f")


def fresh_boxes():
    """Give the quantity boxes new keys, so they go back to 0 after an action.

    Streamlit keeps a widget's value for as long as its key stays the same.
    Bumping this number hands out new keys, and new boxes start empty.
    """
    st.session_state["round"] = st.session_state.get("round", 0) + 1


# ---------------------------------------------------------------- screens

def show_sign():
    """The sign over the door. Used by the start screen and by the kitchen."""
    st.markdown(
        """
        <div class="sign">
            <div class="big">NONNA</div>
            <div class="big">GOES</div>
            <div class="big">CRAZY</div>
            <div class="small">PASTA FRESCA ITALIANA</div>
        </div>
        <div class="rule"></div>
        """,
        unsafe_allow_html=True,
    )


def show_cooking_screen():
    """The service, on a page of its own.

    A fixed layer over the whole window, so nothing of the kitchen shows
    through: Streamlit leaves the previous screen standing while a script is
    still running, and this one deliberately takes a few seconds.

    The day is already written by the time this runs. It is theatre, not work --
    closing the tab here loses nothing.
    """
    windows = []
    share = 100.0 / len(COOKING_LINES)
    for number, line in enumerate(COOKING_LINES):
        start = number * share
        end = start + share
        windows.append(
            "@keyframes line%d { 0%%,%.1f%% {opacity:0} %.1f%%,%.1f%% {opacity:1} "
            "%.1f%%,100%% {opacity:0} }" % (number, max(start - 0.1, 0), start, end - 0.1, end)
        )
        windows.append(
            ".line%d { animation: line%d %.2fs linear forwards; }" % (number, number, COOKING_SECONDS)
        )

    lines = "".join(
        '<span class="line line%d">%s</span>' % (number, line)
        for number, line in enumerate(COOKING_LINES)
    )

    st.markdown(
        """
        <style>
        .curtain {
            position: fixed; inset: 0; z-index: 9999;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            background-color: """ + CREAM + """;
            background-image:
                linear-gradient(45deg, rgba(43,46,126,.045) 25%, transparent 25%,
                                transparent 75%, rgba(43,46,126,.045) 75%),
                linear-gradient(45deg, rgba(43,46,126,.045) 25%, transparent 25%,
                                transparent 75%, rgba(43,46,126,.045) 75%);
            background-size: 54px 54px;
            background-position: 0 0, 27px 27px;
        }
        .curtain .big {
            font-family: Georgia, "Times New Roman", serif; font-weight: 700;
            font-size: 4.2rem; color: """ + INK + """;
            letter-spacing: .04em; line-height: .95;
        }
        .curtain .small {
            font-family: Georgia, serif; letter-spacing: .42em;
            font-size: .72rem; color: """ + PINK + """; margin-top: 1rem;
        }
        .stage { position: relative; height: 2rem; width: 340px; margin-top: 2.6rem; }
        .line {
            position: absolute; inset: 0; text-align: center; opacity: 0;
            font-family: Georgia, serif; font-style: italic;
            font-size: 1.1rem; color: """ + PINK + """;
        }
        """ + "".join(windows) + """
        .bar {
            width: 340px; height: 9px; border-radius: 999px;
            background: rgba(43,46,126,.14); overflow: hidden; margin-top: .4rem;
        }
        .fill {
            height: 100%; width: 0; background: """ + PINK + """;
            animation: fill """ + format(COOKING_SECONDS, ".2f") + """s linear forwards;
        }
        @keyframes fill { to { width: 100%; } }
        </style>

        <div class="curtain">
            <div style="text-align:center">
                <div class="big">NONNA</div>
                <div class="big">GOES</div>
                <div class="big">CRAZY</div>
                <div class="small">PASTA FRESCA ITALIANA</div>
            </div>
            <div class="stage">""" + lines + """</div>
            <div class="bar"><div class="fill"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    time.sleep(COOKING_SECONDS)

    st.session_state["report"] = st.session_state.pop("cooking")
    fresh_boxes()
    st.rerun()


def show_start_screen():
    """The sign over the door. One way in."""
    show_sign()

    left, middle, right = st.columns([1, 2, 1])
    with middle:
        if logic.current_day() == 1 and logic.kitchen_is_empty():
            st.markdown(
                "<p style='text-align:center'>Five days. "
                + euro(logic.STARTING_CASH)
                + " to start. Buy well.</p>",
                unsafe_allow_html=True,
            )
            label = "Start Game"
        else:
            st.markdown(
                "<p style='text-align:center'>Day "
                + str(logic.current_day())
                + " · "
                + euro(logic.current_cash())
                + " in the till.</p>",
                unsafe_allow_html=True,
            )
            label = "Back to the kitchen"

        if st.button(label, use_container_width=True, type="primary"):
            st.session_state["playing"] = True
            st.rerun()


def show_header():
    """The sign and the two numbers that matter, on one line."""
    sign, day, cash = st.columns([4, 1, 1.4], vertical_alignment="center")
    sign.markdown(
        "<div class='topsign'>NONNA GOES CRAZY"
        "<small>PASTA FRESCA ITALIANA</small></div>",
        unsafe_allow_html=True,
    )
    day.markdown(
        "<div class='stat'><span>DAY</span><b>" + str(logic.current_day()) + "</b></div>",
        unsafe_allow_html=True,
    )
    cash.markdown(
        "<div class='stat'><span>CASH</span><b>" + euro(logic.current_cash()) + "</b></div>",
        unsafe_allow_html=True,
    )


def cell(column, text, extra=""):
    column.markdown("<div class='td " + extra + "'>" + text + "</div>", unsafe_allow_html=True)


def show_plan_screen():
    """Plan the day: what to charge, what to buy, and what the room will want."""
    show_header()
    st.markdown("<div class='head'>Tonight&rsquo;s menu</div>", unsafe_allow_html=True)

    widths = [2.9, 0.85, 0.95, 1.5, 1.05, 1.35, 1.15]
    titles = ["Dish", "Stock", "Cost", "Your price", "Demand", "Order", "Spend"]
    header = st.columns(widths)
    for column, title in zip(header, titles):
        column.markdown(
            "<div class='th" + ("" if title == "Dish" else " num") + "'>" + title + "</div>",
            unsafe_allow_html=True,
        )

    round_number = st.session_state.get("round", 0)
    stock = logic.current_stock()
    saved_prices = logic.current_prices()
    quantities = {}
    prices = {}

    for dish in logic.MENU:
        name = dish["name"]
        row = st.columns(widths)

        row[0].markdown(
            "<div class='td name'>" + name
            + "<span class='ref'>reference " + euro(dish["price"]) + "</span></div>",
            unsafe_allow_html=True,
        )
        cell(row[1], str(stock[name]), "num")
        cell(row[2], euro(dish["cost"]), "num")

        asking = row[3].number_input(
            name + " price",
            min_value=0.01,
            step=0.10,
            value=float(saved_prices[name]),
            format="%.2f",
            key="price-" + name + "-" + str(round_number),
            label_visibility="collapsed",
        )
        prices[name] = asking

        # The rule, doing its work in front of you: this number moves as you type.
        wanted = logic.demand_for(dish, asking)
        cell(row[4], "<b>" + str(wanted) + "</b>", "num")

        typed = row[5].number_input(
            name,
            min_value=0,
            step=1,
            value=None,
            placeholder="0",
            key="qty-" + name + "-" + str(round_number),
            label_visibility="collapsed",
        )
        quantities[name] = typed if typed is not None else 0
        cell(row[6], euro(quantities[name] * dish["cost"]), "num")

    st.markdown(
        "<div class='rule-note'>" + logic.DEMAND_RULE + "</div>", unsafe_allow_html=True
    )

    total = logic.order_total(quantities)
    cash = logic.current_cash()
    affordable = total <= cash

    st.markdown(
        "<div class='total" + ("" if affordable else " warn") + "'>Total &nbsp;"
        + euro(total)
        + ("" if affordable else "  &mdash; you only have " + euro(cash))
        + "</div>",
        unsafe_allow_html=True,
    )

    label = (
        "Buy " + euro(total) + " and open the restaurant"
        if total > 0
        else "Open the restaurant"
    )
    if st.button(label, disabled=not affordable, type="primary", use_container_width=True):
        result = logic.buy_and_open(quantities, prices)
        if result["ok"]:
            st.session_state["cooking"] = result
            fresh_boxes()
            st.rerun()
        else:
            st.error(result["error"])

    if total == 0 and logic.kitchen_is_empty():
        st.markdown(
            "<div class='quiet'>The kitchen is empty &mdash; order something to open today.</div>",
            unsafe_allow_html=True,
        )


def show_report_screen():
    """How the day went, and how it compares with the ones before it."""
    day = st.session_state["report"]
    gain = day["cash_delta"]

    st.markdown(
        "<div class='topsign' style='text-align:center'>NONNA GOES CRAZY"
        "<small>PASTA FRESCA ITALIANA</small></div>"
        "<div class='closed'>DAY " + str(day["day"]) + " IS DONE</div>"
        "<div class='verdict'>+" + euro(gain) + "</div>"
        "<div class='ledger'><b>" + euro(day["cash_after"]) + "</b> in the till</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 2.6], gap="large")

    with left:
        st.markdown("<div class='head'>Tonight</div>", unsafe_allow_html=True)
        widths = [2.4, 1.1, 0.8, 0.8, 1.2]
        for column, title in zip(
            st.columns(widths), ["Dish", "Price", "Had", "Sold", "Profit"]
        ):
            column.markdown(
                "<div class='th" + ("" if title == "Dish" else " num") + "'>" + title + "</div>",
                unsafe_allow_html=True,
            )
        for dish in logic.MENU:
            line = day["dishes"][dish["name"]]
            row = st.columns(widths)
            cell(row[0], dish["name"], "name")
            cell(row[1], euro(line["price"]), "num")
            cell(row[2], str(line["stock_before"]), "num")
            cell(row[3], str(line["sold"]), "num")
            cell(row[4], euro(line["profit"]), "num")

    with right:
        st.markdown("<div class='head'>Compared</div>", unsafe_allow_html=True)
        widths = [0.7, 0.9, 1.2, 1.2, 1.3]
        for column, title in zip(
            st.columns(widths), ["Day", "Sold", "Revenue", "Profit", "Cash"]
        ):
            column.markdown(
                "<div class='th" + ("" if title == "Day" else " num") + "'>" + title + "</div>",
                unsafe_allow_html=True,
            )
        for past in logic.final_result()["days"]:
            row = st.columns(widths)
            cell(row[0], str(past["day"]))
            cell(row[1], str(past["sold"]), "num")
            cell(row[2], euro(past["revenue"]), "num")
            cell(row[3], euro(past["profit"]), "num")
            cell(row[4], euro(past["cash_after"]), "num")

    left_over = logic.leftovers()
    if left_over:
        parts = [
            str(item["portions"]) + " &times; " + item["name"] for item in left_over
        ]
        st.markdown(
            "<div class='leftover'><span class='tag'>STAYED IN THE KITCHEN</span>"
            + " &nbsp;&middot;&nbsp; ".join(parts)
            + " &nbsp;&nbsp;&mdash;&nbsp;&nbsp; <b>" + euro(logic.stock_value())
            + "</b>, and they keep</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    spacer_left, middle, spacer_right = st.columns([2, 2, 2])
    if middle.button(
        "Plan day " + str(logic.current_day()), type="primary", use_container_width=True
    ):
        st.session_state.pop("report", None)
        st.rerun()


def show_end_screen():
    """The scoreboard after the fifth day (CT05).

    Leftover stock is counted at what it cost to buy: it is money that simply
    has not been turned back into cash yet (CT R4).
    """
    result = logic.final_result()
    gain = result["gain"]

    st.markdown(
        "<div class='topsign' style='text-align:center'>NONNA GOES CRAZY"
        "<small>PASTA FRESCA ITALIANA</small></div>"
        "<div class='closed'>FIVE DAYS DONE</div>"
        "<div class='verdict'>" + ("+" if gain >= 0 else "\u2212") + euro(abs(gain)) + "</div>"
        "<div class='ledger'><b>" + euro(result["cash"]) + "</b> in the till &nbsp;&middot;&nbsp; "
        "<b>" + euro(result["stock_value"]) + "</b> still in the kitchen &nbsp;&middot;&nbsp; "
        "started with " + euro(logic.STARTING_CASH) + "</div>",
        unsafe_allow_html=True,
    )

    # Only worth a line when something actually went unsold.
    if result["leftovers"]:
        parts = [
            str(item["portions"]) + " &times; " + item["name"] + " " + euro(item["value"])
            for item in result["leftovers"]
        ]
        st.markdown(
            "<div class='leftover'><span class='tag'>STILL IN THE KITCHEN</span>"
            + " &nbsp;&middot;&nbsp; ".join(parts)
            + " &nbsp;&nbsp;&mdash;&nbsp;&nbsp; <b>" + euro(result["stock_value"]) + " in all</b></div>",
            unsafe_allow_html=True,
        )

    left, right = st.columns([3, 2.4], gap="large")

    with left:
        st.markdown("<div class='head'>The five days</div>", unsafe_allow_html=True)
        widths = [0.8, 1, 1.3, 1.3, 1.5]
        header = st.columns(widths)
        for column, title in zip(header, ["Day", "Sold", "Revenue", "Profit", "Cash after"]):
            column.markdown(
                "<div class='th" + ("" if title == "Day" else " num") + "'>" + title + "</div>",
                unsafe_allow_html=True,
            )
        for day in result["days"]:
            row = st.columns(widths)
            cell(row[0], str(day["day"]))
            cell(row[1], str(day["sold"]), "num")
            cell(row[2], euro(day["revenue"]), "num")
            cell(row[3], euro(day["profit"]), "num")
            cell(row[4], euro(day["cash_after"]), "num")

    with right:
        st.markdown("<div class='head'>What sold</div>", unsafe_allow_html=True)
        widths = [2.4, 1, 1.4, 1.4]
        header = st.columns(widths)
        for column, title in zip(header, ["Dish", "Sold", "Revenue", "Profit"]):
            column.markdown(
                "<div class='th" + ("" if title == "Dish" else " num") + "'>" + title + "</div>",
                unsafe_allow_html=True,
            )
        for dish in logic.MENU:
            line = result["dishes"][dish["name"]]
            row = st.columns(widths)
            cell(row[0], dish["name"], "name")
            cell(row[1], str(line["sold"]), "num")
            cell(row[2], euro(line["revenue"]), "num")
            cell(row[3], euro(line["profit"]), "num")

        total = st.columns(widths)
        cell(total[0], "<b>Total</b>", "name foot")
        cell(total[1], "<b>" + str(result["sold"]) + "</b>", "num foot")
        cell(total[2], "<b>" + euro(result["revenue"]) + "</b>", "num foot")
        cell(total[3], "<b>" + euro(result["profit"]) + "</b>", "num foot")

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    spacer_left, middle, spacer_right = st.columns([2, 2, 2])
    if middle.button("Back to start", type="primary", use_container_width=True):
        logic.start_new_run()
        st.session_state["playing"] = False
        st.session_state.pop("report", None)
        fresh_boxes()
        st.rerun()


def main():
    """One screen at a time: the sign, the plan, the service, the report, the end."""
    paint_the_room()

    if "cooking" in st.session_state:
        show_cooking_screen()
        return

    if not st.session_state.get("playing", False):
        show_start_screen()
        return

    if logic.run_is_over():
        show_end_screen()
        return

    if "report" in st.session_state:
        show_report_screen()
        return

    show_plan_screen()


main()
