# First feature — price it, stock it, open for a day, come back to it

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
Tonight's menu                    Day 1          EUR 100.00

  DISH              STOCK  COST  YOUR PRICE  DEMAND  ORDER   SPEND
  Iconic Pomodoro       0  7.00  [ 11.90 ]      10   [   ]    0.00
    reference 11.90
  Drunken Arrabbiata    0  9.00  [ 19.00 ]       5   [   ]    0.00
    reference 12.90
  Carbobora             0 11.00  [ 30.00 ]       0   [ 1 ]   11.00
    reference 14.00
                                                   ---------------
                                                    Total    11.00

  At or below the reference price people want 10 portions
  · up to twice it, 5 · above that, none.

      [   Buy EUR 11.00 and open the restaurant   ]
```

- Each box takes a **whole number from 0 upwards**. Zero is fine: there is no
  obligation to buy every dish.
- There is **no upper limit on the boxes**. The money is the limit.
- The total is `sum(quantity x unit cost)`, to two decimals (CT R3).
- The **button is disabled** when the total is greater than the cash on hand.
  An order that cannot be paid for can never be submitted.

When an order goes through, **cash goes down and stock goes up in the same
step** — never one without the other (CT02).

### Setting the price (CT03)

Each dish has a price box next to it, starting at the reference price on a new
run. **Yesterday's price stays until it is changed** — it was chosen on
purpose, and retyping it every morning would be busywork. Prices are stored
and survive a restart, which A5 names alongside cash, stock and history.

Every price has to be **above zero** (A2). One bad entry stops the whole set,
so the menu can never end up half changed.

**The rule is shown by doing, not by a footnote.** A *Demand* column next to
each price says how many portions the room will want at that price, and it
moves as the price is typed: ask 24.00 for a dish whose reference is 11.90 and
it drops to 0 while you watch. A line under the table says the rule in words
as well, for the first glance.

### Opening for the day (CT04)

**There is one button, not two.** Ordering and opening were never separate
decisions: you choose what to cook with, then you open. The same click buys
what is typed in the boxes and serves the day, so whatever is bought is in the
kitchen for that very day.

The label says what the click will cost — *Buy €70.00 and open the restaurant*
— so no money leaves unannounced. With empty boxes it reads *Open the
restaurant* and simply serves what is already in the kitchen.

**Nothing happens by halves.** If the order cannot be paid for, the day is not
served either and not a cent moves. There is never stock bought for a day that
then does not open.

Each dish sells at whatever the owner asked for it in the price box above
(CT03), and the demand rule is applied against that price.

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

Demand is decided by the price the owner asked, nothing else: there is no
randomness in this release (CT R1). Charge the reference price and the room is
full at 10; charge more than twice it and nobody comes.

### The day's report (CT04)

After the service, a page of its own shows what the day did: for each dish the
price charged, what was in the kitchen, how many went, the revenue, the cost of
the goods sold and the profit — **and the same four in total** underneath
(CT04). Anything that stayed in the kitchen is named below it.

### Finding your way around (CT01)

The header carries the day, the cash, and **five dots** that fill as the run
goes on, so the five-day frame is visible from the first screen rather than
arriving as a surprise at the end.

Every screen has a quiet *Back to menu* in the bottom right. It changes
nothing: the run is in the database, and walking away from it loses nothing.

The menu knows three states. Nothing played yet gives *Start game*. A run under
way gives *Continue run* beside *Start new game*. A finished run gives only
*Start new game*.

**Replacing a run asks first** (CT01, A6): *This will delete your current run.*
Cancelling keeps it exactly as it was. Leaving for the menu does not ask,
because nothing is lost by it.

### The end of the run (CT05)

After the fifth day has been served the kitchen closes: **neither buying nor
opening is possible any more**, and the group page gives way to a scoreboard —
the five days, what each dish sold, and the result.

The result counts the stock still in the kitchen at what it cost to buy
(CT R4): **final cash + leftover stock at cost − €100**. Unsold stock is not
waste, it is money that has not been turned back into cash yet. When something
is left, the scoreboard names it dish by dish.

The run also ends early when the owner is **out of money**: an empty kitchen
and less in the till than the cheapest dish costs. There is no way forward
from there — opening is refused for want of food, shopping for want of money —
so the kitchen closes and the scoreboard says *out of money on day N*. Without
it the day would stand still for ever and the scoreboard, with it the only way
to start again, would be out of reach.

*Back to start* throws the finished run away and opens again on day one with
€100 and an empty kitchen (A6).

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

- Abandoning a run that is still going. Starting over is offered only once the
  five days are done, where there is nothing left to protect (CT01, A6).
- Anything the brief puts out of scope itself: random events, upgrades,
  competing businesses, running costs, spoilage, borrowing, stock returns.

## Done when

Every expected value below was worked out from the menu **before** any test was
written. Each check is done by hand in the running app, and is also covered by
a test, except where noted.

1. **One click buys and serves.** A fresh run has EUR 100.00 and an empty
   kitchen. Typing **10 Iconic Pomodoro** makes the button read *Buy EUR 70.00
   and open the restaurant*. Pressing it gives **10 portions sold, EUR 119.00
   revenue, EUR 70.00 cost of goods sold, EUR 49.00 gross profit, EUR 149.00
   cash** (100.00 − 70.00 + 119.00), **0 portions left, day 2, and one history
   entry** (A3 applied to this menu).

2. **An order that costs too much cannot be placed.** On a fresh run, typing
   **20 Pomodoro** shows a total of EUR 140.00 in red and the button is
   **disabled**. Typing **14** instead shows EUR 98.00 and the button is
   active. The boundary sits between them (A1).

3. **The refused action.** With an empty kitchen and empty boxes, pressing
   *Open the restaurant* shows *"The kitchen is empty."* Cash, stock, day and
   history are **exactly as they were** — nothing is written.

4. **An order that cannot be paid for stops the whole thing.** Asked to buy
   20 Pomodoro on a fresh run, nothing is bought, **no day is served**, and the
   till still holds EUR 100.00. The screen cannot reach this state because the
   button is disabled — the rule sits in the logic so that it holds anyway.

5. **Stock limits sales.** With 3 Pomodoro in stock and demand 10, exactly
   **3 are sold**. With zero stock, **zero** are sold and stock stays at zero,
   never below (A4).

6. **No order is needed when stock remains.** Buying **14 Pomodoro** sells 10
   and leaves 4 (CT R2). The next day, pressing the button with **empty boxes**
   serves those 4 — leftovers are stock, not waste.

7. **Demand sits on the right side of every boundary.** For Iconic Pomodoro,
   with its EUR 11.90 reference price, prices of **11.90, 11.91, 23.80 and
   23.81** give demand **10, 5, 5 and 0** (A2). Typing each of them into the
   price box moves the *Demand* column to that number before anything is
   bought.

8. **A restart changes nothing.** After check 1, stopping the process with
   Ctrl+C and starting it again shows **EUR 149.00 cash, 0 Pomodoro, day 2 and
   exactly one history entry** for day 1. Opening the app does not trade again
   (A5, CT R5). Reloading the browser does not count: Streamlit re-runs the
   script anyway, so only stopping the process proves the numbers came from the
   database.

9. **The day's report adds up.** Ordering 10 Pomodoro and 3 Arrabbiata on a
   fresh run (EUR 97.00, which fits) sells 13 portions for **EUR 157.70
   revenue, EUR 97.00 cost of goods and EUR 60.70 profit**, and the totals
   equal the dish rows added together (CT04).

10. **Replacing a run asks first.** *Start new game* on a run under way shows
   *This will delete your current run.* Cancelling leaves the day, the till
   and the history exactly as they were (A6).

11. **The run ends after five days.** Once the fifth day is served the day
   counter stands at 6, **buying and opening are both refused**, and the
   scoreboard appears instead of the kitchen (CT05).

12. **The price decides the room.** On a fresh run, buying 10 Pomodoro and
   asking **15.00** instead of the 11.90 reference sells **5, not 10**:
   EUR 75.00 revenue, EUR 35.00 cost of goods sold, EUR 40.00 profit,
   EUR 105.00 cash and **5 portions left** (CT R1, CT R2). Asking **24.00**,
   above twice the reference, sells **nothing at all** and the food stays.

13. **A price of zero or less is refused.** Nothing is written: the prices
   stay as they were, no stock is bought and no day is served (A2). One wrong
   price among three stops all three.

14. **Yesterday's price is still there today.** A price set on day one is what
   the next day opens with, until it is changed, and it survives a restart of
   the process (A5).

15. **Going broke ends the run.** Selling 14 Pomodoro at 0.01 leaves EUR 2.14
   and an empty kitchen on day 3. Shopping is refused (the cheapest dish is
   EUR 7.00) and opening is refused (no food), so the scoreboard appears
   instead, headed *out of money on day 3*, with the result
   2.14 + 0.00 − 100.00 = **−EUR 97.86**.

16. **An empty kitchen on its own is not the end.** With money left to
   restock, the run carries on as normal.

17. **Leftover stock still counts.** Buying **14 Pomodoro** on the last day
   sells 10 and leaves 4. Those 4 are worth **EUR 28.00** at purchase cost,
   the scoreboard names them, and they go into the result:
   final cash + 28.00 − 100.00 (CT R4).
