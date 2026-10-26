# First feature — buy stock, trade one day, and come back to it

One workflow, clickable from start to finish. It is the smallest slice of
**Nonna Goes Crazy** that still proves the app can take money off a player,
refuse an action, and remember what happened after it is closed.

Brief: `docs/product-brief.md`. Rule ids below refer to it.

## The catalogue

| Dish               | Unit cost | Reference price |
|--------------------|-----------|-----------------|
| Iconic Pomodoro    | 7.00      | 11.90           |
| Drunken Arrabbiata | 9.00      | 12.90           |
| Carbobora          | 11.00     | 14.00           |

Fixed. The player never changes these.

## Why

As the owner of Nonna Goes Crazy, I want to buy ingredients, open the
restaurant for one day and see what I sold, so that I can tell whether my
buying decision made money — and I want to find the same numbers when I come
back, instead of starting over.

## What

**Start a run.** On first use the app has a run at day 1 with EUR 100 cash,
zero stock, and the three dishes above with their fixed unit cost and reference
price (CT01). The catalogue never changes.

**Buy stock** (CT02). The player picks a dish and a quantity.

- The quantity must be a positive whole number.
- Total cost is quantity x unit cost (CT R3).
- If the total cost is greater than the cash on hand, the purchase is
  **rejected**: an error is shown and cash, stock and history are left exactly
  as they were (A1). Nothing is written.
- If it is accepted, cash goes down and stock goes up **in the same step** —
  never one without the other (CT02).

**Trade one day** (CT04). The player opens the restaurant for the current day.
For each dish:

- Demand follows CT R1 against that dish's reference price: 10 portions at or
  below the reference price, 5 above it up to twice the reference, 0 above
  twice the reference. There is no randomness.
- Portions sold are the smaller of demand and stock on hand (CT R2, A4).
- Revenue is portions sold x selling price. Cost of goods sold is portions sold
  x unit cost. Gross profit is revenue minus cost of goods sold (CT R4).
- Cash increases by the total revenue. Stock falls by the portions sold.
  Neither ever goes negative (CT R3).
- The day is recorded once in the history, and the current day advances by
  exactly one (CT R5).

For this first feature the selling price of every dish is its reference price.
Letting the player set prices is CT03 and comes later.

**Come back to it** (CT R5, A5). Stopping the app and starting it again shows
the same cash, the same stock and the same history. The completed day is not
traded a second time and does not appear twice.

## Out of scope

Deliberately left out of this task, to be built after it works:

- Setting selling prices (CT03) — prices stay at the reference price.
- The day-five ending, the final result, and disabling further play (CT05).
- Starting a new run over an existing one, and its confirmation (CT01, A6).
- Any presentation beyond plain numbers: charts, styling, per-day drill-downs.

## Done when

Each check is performed by hand in the running app, and is also covered by a
test. Expected results are written here **before** any test is written.

1. **An accepted purchase.** A fresh run has EUR 100.00 and zero stock. Buying
   **10 Iconic Pomodoro** at EUR 7.00 costs EUR 70.00 and leaves
   **EUR 30.00 cash and 10 portions in stock** (A1).

2. **A rejected purchase leaves everything unchanged.** From that state
   (EUR 30.00, 10 Pomodoro), buying **5 more** would cost EUR 35.00. The
   purchase is **refused with a message**, and cash is still **EUR 30.00**,
   stock is still **10**, and the history is still empty (A1).
   Buying 4 instead would cost EUR 28.00 and must be accepted — the boundary
   sits between them.
   A quantity of 0 or less is refused the same way.

3. **A trading day reconciles.** From EUR 30.00 with 10 Pomodoro at its
   EUR 11.90 reference price, the other two dishes out of stock, opening for
   the day gives **10 portions sold, EUR 119.00 revenue, EUR 70.00 cost of
   goods sold, EUR 49.00 gross profit, EUR 149.00 cash, 0 portions left**
   (A3 applied to this catalogue).

4. **Stock limits sales.** With 3 Pomodoro in stock and demand 10, exactly
   **3 are sold**. With zero stock, **zero** are sold and stock stays at zero,
   never below (A4).

5. **Demand sits on the right side of every boundary.** For Iconic Pomodoro,
   with its EUR 11.90 reference price, selling prices of **11.90, 11.91, 23.80
   and 23.81** give demand **10, 5, 5 and 0** (A2). The same shape holds for
   Drunken Arrabbiata around 12.90 / 25.80 and for Carbobora around
   14.00 / 28.00.

6. **A restart changes nothing.** After check 3, stopping the app and starting
   it again shows **EUR 149.00 cash, 0 Pomodoro, day 2, and exactly one entry
   in the history** for day 1. Opening the app does not trade again (A5,
   CT R5). Reloading the browser does not count as a restart; the process is
   stopped.
