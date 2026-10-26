# Campus Tycoon — business requirements (v1.0, 2026-09-29)

Copy of the course BRD, kept here so the agent can read it.
Source: week-05/02-campus-tycoon-brd.html

## Goal

A short simulation where prices affect demand, stock limits sales, and the
financial result is easy to understand. The first release is one business with
at least three products over a five-day run.

Starts with **EUR 100 cash and zero stock**. Each product has a fixed positive
unit purchase cost and a fixed positive reference selling price. Theme and
catalogue are the team's choice.

## User journey

Start a run, buy stock, set prices, open for one day. The app reports sales and
updates cash and stock. Repeat until day five, when the final result is shown.
The player can leave and resume between trading days.

## Requirements

- **CT01 Manage a run** — show current day, cash, stock by product, progress
  through the five-day run. Confirm before replacing a run.
- **CT02 Purchase stock** — accept positive whole-number quantities, show total
  cost, reject unaffordable purchases, update cash and stock together.
- **CT03 Set prices** — accept a positive selling price per product before
  trading. Show the demand rule.
- **CT04 Trade one day** — use current stock and prices. Show units sold,
  revenue, cost of goods sold and gross profit, by product and in total.
- **CT05 Review progress** — keep a history of completed days. After day five
  show final cash, remaining stock at purchase cost, and overall gain or loss.
  Buying and trading stop.

## Business rules

- **CT R1 Demand** — 10 units at or below the reference price, 5 units above
  reference up to twice it, 0 above twice it. There is no randomness in the
  first release.
- **CT R2 Sales and stock** — units sold are the smaller of demand and stock.
  Unsold stock carries forward. No running costs, spoilage, borrowing, returns.
- **CT R3 Money** — euro amounts with at most two decimals. A purchase costs
  quantity x unit cost. Trading adds units sold x price. Cash and stock never
  go negative.
- **CT R4 Results** — daily gross profit is revenue minus the purchase cost of
  the units sold. Overall gain or loss is final cash plus remaining stock at
  purchase cost, minus EUR 100. Stock purchases are not deducted from cash a
  second time.
- **CT R5 Day progression** — a completed day is recorded once, and reopening
  the app must not repeat its sales. Each trade action advances exactly one day.
  The run ends after day five.

## Acceptance scenarios

- **A1 Purchase within budget** — with EUR 100, buying 10 units at EUR 2 leaves
  EUR 80 and 10 units. A further EUR 82 purchase is rejected with no change.
- **A2 Demand boundaries** — at a EUR 4 reference price, prices of 4, 4.01, 8
  and 8.01 give demand 10, 5, 5 and 0. Zero or negative prices are rejected.
- **A3 Reconcile a trading day** — with EUR 80, 10 units at EUR 2 unit cost and
  a EUR 4 price (at reference), other products out of stock: revenue EUR 40,
  COGS EUR 20, gross profit EUR 20, cash EUR 120, stock zero.
- **A4 Stock limits sales** — with 3 units and demand 10, sell 3. With zero
  stock, sell zero. Stock never goes negative.
- **A5 Resume without replay** — after completing a day, restarting the app
  keeps cash, stock, prices and history unchanged, with one record for that day.
- **A6 Complete and restart** — after day five, buying and trading are disabled.
  A confirmed new run restores EUR 100, zero stock, day one, empty history.
  Cancelling keeps the previous run.

## Data to remember

Product catalogue with unit costs and reference prices. Run cash, stock, chosen
selling prices, current day, daily results. Accepted purchases and price changes
saved immediately. Each day's results saved together with the updated balances.

## Scope figures

3 products minimum, 5 trading days, EUR 100 starting cash, zero starting stock,
two decimal places for money.

## Constraints and release criteria

- Accepted changes survive app restarts.
- Rejected actions leave existing data unchanged.
- Works with supplied content, no paid service or live external integration.

## Out of scope

Random events, upgrades, competing businesses, more complex demand models.
Also excluded: running costs, spoilage, borrowing, stock returns.

## Theme and catalogue chosen for this build

**Nonna Goes Crazy** — a pasta restaurant on campus. Three dishes:

| Dish               | Unit cost | Reference price | Margin |
|--------------------|-----------|-----------------|--------|
| Iconic Pomodoro    | 7.00      | 11.90           | 4.90   |
| Drunken Arrabbiata | 9.00      | 12.90           | 3.90   |
| Carbobora          | 11.00     | 14.00           | 3.00   |

The brief allows this: "The theme and catalogue are the team's choice."

A note on scenario A3. It is written with a unit cost of 2.00 and a price of
4.00, which is not this catalogue, so its arithmetic cannot be reproduced
literally. The rule it demonstrates still holds, and check 3 in
`specs/first-feature.md` is the same reconciliation done with these dishes.

Demand boundaries that follow from CT R1 for this catalogue:

| Dish               | demand 10 | demand 5      | demand 0 |
|--------------------|-----------|---------------|----------|
| Iconic Pomodoro    | <= 11.90  | 11.91 - 23.80 | > 23.80  |
| Drunken Arrabbiata | <= 12.90  | 12.91 - 25.80 | > 25.80  |
| Carbobora          | <= 14.00  | 14.01 - 28.00 | > 28.00  |
