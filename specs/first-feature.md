# First feature — order ingredients, open for a day, come back to it

One workflow, clickable from start to finish. The smallest slice of **Nonna
Goes Crazy** that still proves the app can take money off the owner, refuse an
action, and remember what happened after it is closed.

Brief: `docs/product-brief.md`. Rule ids below refer to it.

## The menu

| Dish               | Unit cost | Reference price | Margin |
|--------------------|-----------|-----------------|--------|
| Iconic Pomodoro    | 7.00      | 11.90           | 4.90   |
| Drunken Arrabbiata | 9.00      | 12.90           | 3.90   |
| Carbobora          | 11.00     | 14.00           | 3.00   |

Fixed, and the same on every machine. The menu lives **in the code**
(`logic.py`), not in the database: it is a rule, not a saved game. The database
file is local and not in the repository, so anything kept only there would
differ from laptop to laptop.

## Why

As the owner of Nonna Goes Crazy, I want to order ingredients, open the
restaurant for one day and see what I sold, so that I can tell whether my
buying decision made money — and I want to find the same numbers when I come
back, instead of starting over.

## What

### Starting state

On first use the app creates its own opening position (CT01): **day 1, EUR
100.00 cash, nothing in the kitchen**, empty history. The database file does
not ship with the repository, so the app must be able to build this from
nothing — a fresh clone has to start.

The database holds what changes: **cash, stock per dish, the current day, and
the history of completed days.** Nothing else.

### Ordering ingredients (CT02)

One screen, three quantity boxes side by side — one per dish — with a running
total:

```
Order ingredients                        Cash: EUR 100.00

  Iconic Pomodoro      [ 0 ]  x  7.00  =    0.00
  Drunken Arrabbiata   [ 0 ]  x  9.00  =    0.00
  Carbobora            [ 1 ]  x 11.00  =   11.00
                                          -------
                                  Total    11.00

              [ Order ingredients ]
```

- Each box takes a **whole number from 0 upwards**. Zero is fine: there is no
  obligation to buy every dish.
- There is **no upper limit on the boxes**. The money is the limit.
- The total is `sum(quantity x unit cost)`, to two decimals (CT R3).
- The **button is disabled** when the total is 0.00 (nothing to order) or when
  the total is greater than the cash on hand. An order that cannot be paid for
  can never be submitted.

When an order goes through, **cash goes down and stock goes up in the same
step** — never one without the other (CT02). The day does not advance and no
history entry is written: shopping costs money, not time.

### Opening for the day (CT04)

One button, no input. The selling price of every dish is its reference price;
letting the owner set prices is CT03 and is out of scope here.

Per dish:

```
demand     from CT R1, against that dish's reference price
sold       = the smaller of demand and stock on hand        (CT R2, A4)
revenue    = sold x price
cogs       = sold x unit cost
profit     = revenue - cogs                                  (CT R4)
```

Then, at the level of the run:

```
cash      +=  total revenue
stock     -=  portions sold, per dish
day       +=  1
history   +=  exactly one entry for this day                 (CT R5)
```

Cash and stock never go negative (CT R3).

Because prices stay at the reference price in this first feature, demand is
always 10 for every dish. That is a consequence of leaving CT03 out, not an
accident.

### The rule

There is exactly one:

> **The restaurant cannot open with an empty kitchen.**

Pressing *Open the restaurant* with no stock at all shows an error and
**changes nothing** — no cash movement, no day advance, no history entry.

The rule is about **stock, not about shopping**. On day 3, with portions left
over from day 2, the owner opens without ordering anything. Unsold stock
carries forward (CT R2); it is inventory, not waste.

### What the owner sees

| Situation | Tone | Text |
|---|---|---|
| Empty kitchen, empty order | grey hint | *The kitchen is empty — order something to open today.* |
| Order costs more than the cash | red total, button off | *EUR 112.00 — you only have EUR 100.00.* |
| *Open the restaurant* with an empty kitchen | red error, after the click | *The kitchen is empty. Order some ingredients first.* |
| Stock in the kitchen, empty order | nothing at all | — |

An empty order on a full kitchen is a perfectly good choice and is not
commented on. At startup an empty order is the normal state, so the hint is
grey, not an error: it says what is missing without blaming anyone.

### Saving

There is no save button and no save point. **Every accepted action writes to
the database immediately** (CT R5, "saved immediately"), and there are only two
of them: an accepted order, and a completed day. Nothing else changes the game.

The screen **always reads its numbers from the database**, never from memory.
Streamlit re-runs the whole script on every interaction, so a day that is
calculated while the page is drawn would be charged again on every click. A
day is an action that writes once; the page only reads back what was stored.

### Coming back

Stopping the app and starting it again shows the same cash, the same stock, the
same day and the same history. The completed day is **not traded a second time**
and appears **once** (CT R5, A5).

## Out of scope

Deliberately left out of this task, to be built after it works:

- Setting selling prices (CT03) — prices stay at the reference price.
- The day-five ending, the final result and disabling further play (CT05).
- Starting a new run over an existing one, and its confirmation (CT01, A6).
- Any presentation beyond plain numbers: charts, styling, per-day drill-downs.

## Done when

Every expected value below was worked out from the menu **before** any test was
written. Each check is done by hand in the running app, and is also covered by
a test, except where noted.

1. **An accepted order.** A fresh run has EUR 100.00 and an empty kitchen.
   Ordering **10 Iconic Pomodoro, 0, 0** costs EUR 70.00 and leaves
   **EUR 30.00 cash and 10 portions of Pomodoro**.

2. **An order that costs too much cannot be placed.** From that state
   (EUR 30.00), typing **5 Pomodoro** shows a total of EUR 35.00 in red and the
   button is **disabled**. Typing **4** instead shows EUR 28.00 and the button
   is active. The boundary sits between them.

3. **The refused action.** With an empty kitchen, pressing *Open the
   restaurant* shows *"The kitchen is empty."* Cash, stock, day and history
   are **exactly as they were** — nothing is written.

4. **A trading day reconciles.** From EUR 30.00 with 10 Pomodoro at its
   EUR 11.90 reference price, the other two dishes out of stock, opening gives
   **10 portions sold, EUR 119.00 revenue, EUR 70.00 cost of goods sold,
   EUR 49.00 gross profit, EUR 149.00 cash, 0 portions left, day 2, and one
   history entry**.

5. **Stock limits sales.** With 3 Pomodoro in stock and demand 10, exactly
   **3 are sold**. With zero stock, **zero** are sold and stock stays at zero,
   never below (A4).

6. **No order is needed when stock remains.** With portions left from the day
   before, *Open the restaurant* works **without ordering anything**, and the
   leftover stock is what gets sold.

7. **Demand sits on the right side of every boundary.** For Iconic Pomodoro,
   with its EUR 11.90 reference price, prices of **11.90, 11.91, 23.80 and
   23.81** give demand **10, 5, 5 and 0** (A2). *Logic test only* — with CT03
   out of scope the app never charges anything but the reference price, so this
   cannot be reached by clicking.

8. **A restart changes nothing.** After check 4, stopping the process with
   Ctrl+C and starting it again shows **EUR 149.00 cash, 0 Pomodoro, day 2 and
   exactly one history entry** for day 1. Opening the app does not trade again
   (A5, CT R5). Reloading the browser does not count: Streamlit re-runs the
   script anyway, so only stopping the process proves the numbers came from the
   database.
