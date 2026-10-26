"""Nonna Goes Crazy: the screens. Start it with:  uv run streamlit run app.py"""

import base64
import time
from pathlib import Path

import streamlit as st

import logic

st.set_page_config(page_title="Nonna Goes Crazy", page_icon="🍝", layout="wide")

# Build the database on first use. Safe to call on every run.
logic.start_up()

INK = "#2B2E7E"       # the blue of the sign
PINK = "#D7446B"      # the accent
CREAM = "#F6EEDC"     # the wall behind the tiles
ALARM = "#A3182B"     # for things that went wrong; pink is for things you press

# The wall behind everything: brick, laid in a bond, with a joint and a
# little light on the top edge. Drawn rather than guessed at with
# gradients, which could only ever manage a chessboard.
TILES = (
    'url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22120%22%20height%3D%2260%22%20viewBox%3D%220%200%20120%2060%22%3E%3Crect%20width%3D%22120%22%20height%3D%2260%22%20fill%3D%22%23F6EEDC%22%2F%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%2260%22%20height%3D%2230%22%20fill%3D%22%232B2E7E%22%20opacity%3D%220.022%22%2F%3E%3Crect%20x%3D%2260%22%20y%3D%2230%22%20width%3D%2260%22%20height%3D%2230%22%20fill%3D%22%232B2E7E%22%20opacity%3D%220.030%22%2F%3E%3Crect%20x%3D%220%22%20y%3D%2230%22%20width%3D%2230%22%20height%3D%2230%22%20fill%3D%22%232B2E7E%22%20opacity%3D%220.012%22%2F%3E%3Cg%20stroke%3D%22%232B2E7E%22%20stroke-opacity%3D%220.13%22%20stroke-width%3D%222%22%20fill%3D%22none%22%3E%3Cpath%20d%3D%22M0%2030%20H120%20M0%2060%20H120%22%2F%3E%3Cpath%20d%3D%22M60%200%20V30%22%2F%3E%3Cpath%20d%3D%22M30%2030%20V60%20M90%2030%20V60%22%2F%3E%3C%2Fg%3E%3Cg%20stroke%3D%22%23FFFFFF%22%20stroke-opacity%3D%220.5%22%20stroke-width%3D%221%22%20fill%3D%22none%22%3E%3Cpath%20d%3D%22M0%2031.5%20H120%20M0%201.5%20H120%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E")'
)

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
            background-image: """ + TILES + """;
            background-size: 120px 60px;
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
        /* "Press Enter to apply" under every box. The value applies on its
           own, so the hint only crowds the row. */
        [data-testid="InputInstructions"] { display: none !important; }
        [data-testid="stToolbar"] { display: none; }

        /* Streamlit's default padding alone is taller than a phone. */
        [data-testid="stMainBlockContainer"] {
            padding-top: 2.2rem; padding-bottom: 1.6rem;
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
        .dots { display: flex; gap: .34rem; justify-content: flex-end; margin-top: .5rem; }
        .dot {
            width: 13px; height: 13px; border-radius: 50%;
            border: 2px solid """ + INK + """; opacity: .3;
        }
        .dot.done { background: """ + INK + """; opacity: 1; }
        .dot.now  {
            background: """ + PINK + """; border-color: """ + PINK + """; opacity: 1;
            animation: breathe 2.4s ease-in-out infinite;
        }
        @keyframes breathe {
            0%, 100% { transform: scale(1);    box-shadow: 0 0 0 0 rgba(215,68,107,.45); }
            50%      { transform: scale(1.18); box-shadow: 0 0 0 5px rgba(215,68,107,0); }
        }
        .dish-pic {
            width: 44px; height: 44px; image-rendering: pixelated;
            margin-right: .8rem; vertical-align: middle; flex-shrink: 0;
        }
        /* Exactly the height of a number box, or the row sits 7px out of line. */
        .td.name.with-pic {
            height: 48px; flex-direction: row; align-items: center;
            /* .td.name centres on the main axis, which is what you want in a
               column. Turning the row sideways made that centre horizontally,
               so each picture started wherever its name left room. */
            justify-content: flex-start;
        }
        .td.name.with-pic .names {
            display: flex; flex-direction: column; justify-content: center;
            line-height: 1.15;
        }

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
            font-size: 1.1rem; color: """ + INK + """;
        }
        .td.name { font-family: Georgia, serif; font-size: 1.42rem; }
        /* The scoreboard splits the width in two, so its names run at the size
           the column can actually hold. */
        .td.name.plain { font-size: 1.04rem; }
        .td.name { flex-direction: column; align-items: flex-start; justify-content: center; }
        .ref {
            font-family: -apple-system, system-ui, sans-serif;
            font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
            color: """ + PINK + """; opacity: .85; margin-top: .1rem;
        }
        /* The wall is lovely but it swallows a table. This lifts the menu
           off it, like a card laid on the counter. */
        .plaque { text-align: center; line-height: 0; }
        .plaque img {
            border-radius: 10px;
            box-shadow: 0 6px 20px rgba(43,46,126,.28);
            image-rendering: auto;
        }
        .st-key-menu-panel,
        .st-key-report-panel,
        .st-key-days-panel,
        .st-key-sold-panel {
            background: rgba(255,252,245,.93);
            border: 1px solid rgba(43,46,126,.16);
            border-top: 3px solid """ + PINK + """;
            border-radius: 12px;
            padding: 1.2rem 1.7rem 1.4rem 1.7rem;
            box-shadow: 0 4px 18px rgba(43,46,126,.11);
        }
        .st-key-days-panel .head,
        .st-key-sold-panel .head { margin-top: .2rem; }
        .brand { display: flex; align-items: center; gap: 1.3rem; }
        .brand .plaque { line-height: 0; flex-shrink: 0; }
        .brand-title {
            font-family: Georgia, serif; font-size: 1.9rem;
            color: """ + INK + """; line-height: 1.1;
        }
        .rule-note {
            font-size: .98rem; color: """ + INK + """; opacity: .9;
            border-left: 3px solid """ + PINK + """; padding: .35rem .7rem;
            margin: 1rem 0 .2rem 0;
        }
        .td, .th { white-space: nowrap; }

        /* Each row arrives a beat after the one above it, so the menu is laid
           out in front of you rather than appearing all at once. */
        @keyframes arrive {
            from { opacity: 0; transform: translateY(9px); }
            to   { opacity: 1; transform: none; }
        }
        .arrive-1 { animation: arrive .42s ease-out .02s both; }
        .arrive-2 { animation: arrive .42s ease-out .10s both; }
        .arrive-3 { animation: arrive .42s ease-out .18s both; }
        .num { justify-content: flex-end; text-align: right; }
        .total { font-family: Georgia, serif; font-size: 1.5rem; color: """ + INK + """;
                 text-align: right; padding: 1.2rem 0 .4rem 0;
                 border-top: 1px solid rgba(43,46,126,.18); margin-top: .6rem; }
        .warn { color: """ + ALARM + """ !important; }
        .quiet { font-size: .8rem; opacity: .75; }

        .closed {
            text-align: center; font-family: Georgia, serif;
            letter-spacing: .22em; font-size: 1.45rem;
            color: """ + PINK + """; margin-top: .7rem;
        }
        .closed.bad { color: """ + ALARM + """; letter-spacing: .14em; font-size: 1.8rem; }
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

        /* CSS cannot count on its own; a registered property can be animated
           and read back by a counter. The euros climb, the cents stay put --
           counter() has no way to show a decimal. */
        @property --tally {
            syntax: "<integer>"; initial-value: 0; inherits: false;
        }
        .tally { counter-reset: tally var(--tally); }
        .tally i { font-style: normal; }
        .tally i::after { content: counter(tally); }
        .tally.run { animation: tally 1.9s cubic-bezier(.15,.85,.25,1) forwards; }
        @keyframes tally {
            from { --tally: var(--from); }
            to   { --tally: var(--to); }
        }
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

        div[data-testid="stNumberInput"] input {
            padding: .5rem .6rem; font-size: 1rem;
            text-align: right;      /* numbers line up with the columns around them */
        }
        .stButton > button { padding: .95rem 1rem; font-size: 1.05rem; }

        /* The one button that matters. Ink blue on pink was too close a pair
           to read at a glance, so it is white, and it looks like a sign. */
        .stButton > button[kind="primary"] {
            font-family: Georgia, "Times New Roman", serif;
            /* Georgia has nothing heavier than bold, so the letters are
               thickened by stroking them in their own colour. */
            font-weight: 900;
            -webkit-text-stroke: .7px currentColor;
            font-size: 1.42rem;
            letter-spacing: .09em;
            text-transform: uppercase;
            color: #FFF8EC !important;
            padding: 1.05rem 1rem;
            border: none;
            box-shadow: 0 3px 0 rgba(43,46,126,.22);
        }
        .stButton > button[kind="primary"] div,
        .stButton > button[kind="primary"] p {
            font-weight: 900;
            -webkit-text-stroke: .7px currentColor;
        }
        .stButton > button[kind="primary"]:hover {
            color: #FFFFFF !important;
            box-shadow: 0 2px 0 rgba(43,46,126,.3);
            transform: translateY(1px);
        }

        /* The way out should be findable, not loud. Streamlit gives a keyed
           widget its own class, so this reaches that one button only. */
        .st-key-exit-to-menu { margin-top: -2.9rem; }
        .st-key-exit-to-menu button {
            background: rgba(255,252,246,.75) !important;
            border: 1px solid rgba(43,46,126,.25) !important;
            box-shadow: none !important;
            color: """ + INK + """ !important;
            opacity: .9;
            font-size: .92rem !important;
            font-weight: 600;
            padding: .45rem .4rem !important;
            letter-spacing: .04em;
        }
        .st-key-exit-to-menu button:hover {
            opacity: 1; color: """ + PINK + """ !important;
        }
        .quiet { margin-top: .8rem; }
        div[data-testid="stMetricValue"] { color: """ + INK + """; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def dish_picture(filename):
    """Read a dish picture once and hand back something an <img> tag can use.

    The pictures are small enough to travel inside the page, which keeps the
    rows as one piece of markup instead of a column of their own.
    """
    data = (Path(__file__).parent / "assets" / filename).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


LOGO_FILE = "logo.png"


@st.cache_data
def logo_source():
    """The logo as something an <img> can use, or None if it is not there yet.

    Kept optional on purpose: the app has to run from a fresh clone, and a
    missing picture should fall back to the lettering rather than break a
    screen.
    """
    path = Path(__file__).parent / "assets" / LOGO_FILE
    if not path.exists():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def sign_html(height, small_caption=True):
    """The name over the door, at whatever size the screen needs.

    The logo is white on a dark square, so it is treated as a plaque hanging
    on the wall rather than stripped out -- the lettering would be unreadable
    on cream.
    """
    source = logo_source()
    if source:
        return (
            "<div class='plaque'>"
            "<img src='" + source + "' alt='Nonna Goes Crazy' "
            "style='width:" + str(height) + "px;height:" + str(height) + "px'>"
            "</div>"
        )
    caption = "<small>PASTA FRESCA ITALIANA</small>" if small_caption else ""
    return "<div class='topsign' style='text-align:center'>NONNA GOES CRAZY" + caption + "</div>"


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
    """The sign over the door. Used by the start screen."""
    source = logo_source()
    if source:
        st.markdown(
            "<div class='plaque' style='margin:2.6rem 0 1.4rem 0'>"
            "<img src='" + source + "' alt='Nonna Goes Crazy' "
            "style='width:300px;height:300px'></div>",
            unsafe_allow_html=True,
        )
        return
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
            background-image: """ + TILES + """;
            background-size: 120px 60px;
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
            """ + (
                "<div class='plaque'><img src='" + (logo_source() or "") + "' "
                "alt='Nonna Goes Crazy' style='width:230px;height:230px'></div>"
                if logo_source() else
                '<div style="text-align:center">'
                '<div class="big">NONNA</div><div class="big">GOES</div>'
                '<div class="big">CRAZY</div>'
                '<div class="small">PASTA FRESCA ITALIANA</div></div>'
            ) + """
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


def show_back_to_menu():
    """A quiet way out, bottom right. The run stays exactly where it is."""
    spacer, corner = st.columns([6, 1])
    if corner.button("Back to menu", key="exit-to-menu", use_container_width=True):
        st.session_state["playing"] = False
        # Otherwise walking out of a report and back in shows it all over again.
        st.session_state.pop("report", None)
        st.rerun()


def start_a_new_game():
    logic.start_new_run()
    st.session_state["playing"] = True
    st.session_state.pop("report", None)
    st.session_state.pop("confirming", None)
    fresh_boxes()
    st.rerun()


def show_start_screen():
    """The sign over the door, and the way in.

    Three states: nothing played yet, a run waiting to be picked up, or a run
    that has finished. Only replacing a run asks first (CT01, A6) -- leaving
    one alone and walking out of the menu loses nothing, so it does not.
    """
    show_sign()

    left, middle, right = st.columns([1, 2, 1])
    with middle:
        if st.session_state.get("confirming"):
            st.markdown(
                "<p style='text-align:center'>This will delete your current run.</p>",
                unsafe_allow_html=True,
            )
            yes, no = st.columns(2)
            if yes.button("Start new game", use_container_width=True, type="primary"):
                start_a_new_game()
            if no.button("Cancel", use_container_width=True):
                st.session_state.pop("confirming", None)
                st.rerun()
            return

        if not logic.run_has_started():
            st.markdown(
                "<p style='text-align:center'>Five days. "
                + euro(logic.STARTING_CASH)
                + " to start. Buy well.</p>",
                unsafe_allow_html=True,
            )
            if st.button("Start game", use_container_width=True, type="primary"):
                st.session_state["playing"] = True
                st.rerun()
            return

        if logic.run_has_ended():
            # A finished run has nothing left to protect, so it does not ask.
            # The confirmation is for replacing a run that is still going.
            st.markdown(
                "<p style='text-align:center'>Your last run is finished.</p>",
                unsafe_allow_html=True,
            )
            if st.button("Start new game", use_container_width=True, type="primary"):
                start_a_new_game()
            return

        st.markdown(
            "<p style='text-align:center'>Day "
            + str(logic.current_day()) + " of " + str(logic.TOTAL_DAYS)
            + " &nbsp;&middot;&nbsp; " + euro(logic.current_cash())
            + " in the till.</p>",
            unsafe_allow_html=True,
        )
        if st.button("Continue run", use_container_width=True, type="primary"):
            st.session_state["playing"] = True
            st.rerun()
        if st.button("Start new game", use_container_width=True):
            st.session_state["confirming"] = True
            st.rerun()


def show_header():
    """The sign and the two numbers that matter, on one line."""
    sign, day, cash = st.columns([4, 1, 1.4], vertical_alignment="center")
    source = logo_source()
    mark = (
        ("<div class='plaque'><img src='" + source + "' alt='Nonna Goes Crazy' "
         "style='width:124px;height:124px'></div>")
        if source else
        ("<div class='topsign'>NONNA GOES CRAZY"
         "<small>PASTA FRESCA ITALIANA</small></div>")
    )
    sign.markdown(
        "<div class='brand'>" + mark
        + "<div class='brand-title'>Tonight&rsquo;s menu</div></div>",
        unsafe_allow_html=True,
    )
    today = logic.current_day()
    dots = "".join(
        "<i class='dot" + (" done" if number < today else (" now" if number == today else "")) + "'></i>"
        for number in range(1, logic.TOTAL_DAYS + 1)
    )
    day.markdown(
        "<div class='stat'><span>DAY " + str(today) + " OF " + str(logic.TOTAL_DAYS)
        + "</span><div class='dots'>" + dots + "</div></div>",
        unsafe_allow_html=True,
    )
    cash.markdown(
        "<div class='stat'><span>CASH</span><b>" + euro(logic.current_cash()) + "</b></div>",
        unsafe_allow_html=True,
    )


def cell(column, text, extra=""):
    column.markdown("<div class='td " + extra + "'>" + text + "</div>", unsafe_allow_html=True)


def arrival(number):
    """Which beat this row arrives on. Anything past the third shares the last."""
    return " arrive-" + str(min(number, 3))


def show_plan_screen():
    """Plan the day: what to charge, what to buy, and what the room will want."""
    show_header()

    panel = st.container(key="menu-panel")
    with panel:
        quantities, prices, total, affordable = show_menu_table()

    show_the_doors(quantities, prices, total, affordable)


def show_menu_table():
    """The menu itself, on its card: prices, demand, quantities and the total.

    The heading sits up in the header beside the logo, so the card can start
    with its own rule rather than repeating a title.
    """
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

    for number, dish in enumerate(logic.MENU, start=1):
        name = dish["name"]
        beat = arrival(number)
        row = st.columns(widths)

        row[0].markdown(
            "<div class='td name with-pic" + beat + "'>"
            "<img class='dish-pic' src='" + dish_picture(dish["picture"]) + "' alt=''>"
            "<span class='names'>" + name
            + "<span class='ref'>reference " + euro(dish["price"]) + "</span></span></div>",
            unsafe_allow_html=True,
        )
        cell(row[1], str(stock[name]), "num" + beat)
        cell(row[2], euro(dish["cost"]), "num" + beat)

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
        cell(row[4], "<b>" + str(wanted) + "</b>", "num" + beat)

        # A real zero, not an empty box. An empty number_input has nothing to
        # count up from, so its - and + do nothing, and Streamlit shows a
        # "clear the field" cross where the steppers would be.
        quantities[name] = row[5].number_input(
            name,
            min_value=0,
            step=1,
            value=0,
            key="qty-" + name + "-" + str(round_number),
            label_visibility="collapsed",
        )
        cell(row[6], euro(quantities[name] * dish["cost"]), "num" + beat)

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

    return quantities, prices, total, affordable


def show_the_doors(quantities, prices, total, affordable):
    """The button, below the card rather than on it."""
    left_gap, middle, right_gap = st.columns([2, 2, 2])
    if middle.button(
        "Open the restaurant",
        disabled=not affordable,
        type="primary",
        use_container_width=True,
    ):
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

    show_back_to_menu()


def counting_up(amount, start=0.0):
    """An amount that climbs to itself instead of simply appearing.

    Only the euros move: a CSS counter has no way to show a decimal point, so
    the cents are written in beside them. If a browser will not animate a
    registered property the number starts where it ends, which is still right.
    """
    cents = format(amount, ".2f").split(".")[1]
    return (
        "<span class='tally run' style='--from:" + str(int(start))
        + ";--to:" + str(int(amount)) + ";--tally:" + str(int(amount)) + "'>"
        "\u20ac<i></i>." + cents + "</span>"
    )


def show_report_table(day):
    """What each dish did, and the four totals CT04 asks for."""
    widths = [3.2, 1.1, 0.8, 0.9, 1.3, 1.3, 1.3]
    titles = ["Dish", "Price", "Had", "Sold", "Revenue", "Cost of goods", "Profit"]
    for column, title in zip(st.columns(widths), titles):
        column.markdown(
            "<div class='th" + ("" if title == "Dish" else " num") + "'>" + title + "</div>",
            unsafe_allow_html=True,
        )

    for number, dish in enumerate(logic.MENU, start=1):
        line = day["dishes"][dish["name"]]
        beat = arrival(number)
        row = st.columns(widths)
        row[0].markdown(
            "<div class='td name with-pic" + beat + "'>"
            "<img class='dish-pic' src='" + dish_picture(dish["picture"]) + "' alt=''>"
            "<span class='names'>" + dish["name"] + "</span></div>",
            unsafe_allow_html=True,
        )
        cell(row[1], euro(line["price"]), "num" + beat)
        cell(row[2], str(line["stock_before"]), "num" + beat)
        cell(row[3], str(line["sold"]), "num" + beat)
        cell(row[4], euro(line["revenue"]), "num" + beat)
        cell(row[5], euro(line["cogs"]), "num" + beat)
        cell(row[6], euro(line["profit"]), "num" + beat)

    total = st.columns(widths)
    cell(total[0], "<b>Total</b>", "name foot")
    cell(total[1], "", "num foot")
    cell(total[2], "", "num foot")
    cell(total[3], "<b>" + str(day["sold"]) + "</b>", "num foot")
    cell(total[4], "<b>" + euro(day["revenue"]) + "</b>", "num foot")
    cell(total[5], "<b>" + euro(day["cogs"]) + "</b>", "num foot")
    cell(total[6], "<b>" + euro(day["profit"]) + "</b>", "num foot")


def show_report_screen():
    """How the day went: sold, taken, spent and kept, dish by dish and in total.

    CT04 asks for all four, by product and in total, so the table runs the
    full width. The comparison with earlier days lives on the scoreboard,
    where it belongs; repeating it here said the same thing twice.
    """
    day = st.session_state["report"]

    st.markdown(
        sign_html(150)
        + "<div class='closed'>DAY " + str(day["day"]) + " OF "
        + str(logic.TOTAL_DAYS) + " IS DONE</div>"
        # The number of the moment, so it is the one that climbs.
        "<div class='verdict'>+" + counting_up(day["cash_delta"]) + "</div>"
        "<div class='ledger'><b>" + euro(day["cash_after"]) + "</b> in the till</div>",
        unsafe_allow_html=True,
    )

    with st.container(key="report-panel"):
        show_report_table(day)

    left_over = logic.leftovers()
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

    show_back_to_menu()


def show_end_screen():
    """The scoreboard after the fifth day (CT05).

    Leftover stock is counted at what it cost to buy: it is money that simply
    has not been turned back into cash yet (CT R4).
    """
    result = logic.final_result()
    gain = result["gain"]

    st.markdown(
        sign_html(150)
        + ("<div class='closed bad'>OUT OF MONEY</div>"
           "<div class='ledger'>on day " + str(result["days_played"] + 1)
           + " of " + str(logic.TOTAL_DAYS) + "</div>"
           if result["bankrupt"] else
           "<div class='closed'>FIVE DAYS DONE</div>")
        +
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

    with left, st.container(key="days-panel"):
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

    with right, st.container(key="sold-panel"):
        st.markdown("<div class='head'>What sold</div>", unsafe_allow_html=True)
        widths = [3.3, 0.85, 1.2, 1.2]
        header = st.columns(widths)
        for column, title in zip(header, ["Dish", "Sold", "Revenue", "Profit"]):
            column.markdown(
                "<div class='th" + ("" if title == "Dish" else " num") + "'>" + title + "</div>",
                unsafe_allow_html=True,
            )
        for dish in logic.MENU:
            line = result["dishes"][dish["name"]]
            row = st.columns(widths)
            cell(row[0], dish["name"], "name plain")
            cell(row[1], str(line["sold"]), "num")
            cell(row[2], euro(line["revenue"]), "num")
            cell(row[3], euro(line["profit"]), "num")

        total = st.columns(widths)
        cell(total[0], "<b>Total</b>", "name plain foot")
        cell(total[1], "<b>" + str(result["sold"]) + "</b>", "num foot")
        cell(total[2], "<b>" + euro(result["revenue"]) + "</b>", "num foot")
        cell(total[3], "<b>" + euro(result["profit"]) + "</b>", "num foot")

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    spacer_left, middle, spacer_right = st.columns([2, 2, 2])
    if middle.button("Back to menu", type="primary", use_container_width=True):
        st.session_state["playing"] = False
        st.session_state.pop("report", None)
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

    if logic.run_has_ended():
        show_end_screen()
        return

    if "report" in st.session_state:
        show_report_screen()
        return

    show_plan_screen()


main()
