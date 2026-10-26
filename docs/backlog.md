# What is still open

Written down on 26.10.2026, nothing acted on yet.

## Bugs and things to check

**The dish icons are still out of line.** Fixed once by pinning the name cell
to 40px, and they still sit crooked against each other. Needs looking at per
row and per screen, not a global rule.

**Is the demand rule right?** Observed: however far the price drops, demand
never goes above 10; one cent above the reference and it halves to 5.

That is what the brief says, word for word:

> CT R1 — 10 units at or below the reference price, 5 units above reference
> up to twice it, 0 above twice it. There is no randomness.

So the behaviour looks correct and the rule itself is simply a hard step.
Worth re-reading the brief before changing anything: a smooth curve would be
more fun, but it would no longer be CT R1.

## Design

**Real brickwork instead of a chessboard.** The background is a checker
pattern. It should read as laid tile or brick: offset rows, a visible joint,
maybe a slight tone difference per tile.

**The Nonna Goes Crazy logo** exists as a file and could replace the typeset
sign on the start screen, the cooking screen and the scoreboard.

## Working fine, leave alone

Continue run, Start new game, the confirmation, Back to menu.

## Animation and sound — what is actually possible

**Can be built here, no other tool needed**

- Movement in CSS or SVG: steam rising off a pot, a sign swinging, numbers
  counting up, the cooking bar filling, screens fading into each other.
  Perhaps one to two hours for a handful of these.
- A sprite sheet, animated. Hand over one PNG with the frames side by side
  (say 6 frames of a grandma stirring) and CSS plays it with `steps()`.
  That is the classic pixel-art way and it suits the look. Under an hour.
- A GIF or a short video: dropping one in is a single line.

**Cannot be made here**

- The drawing itself. A grandma stirring a pot has to be drawn or generated
  elsewhere -- Aseprite, Piskel, an image generator -- and handed over as a
  GIF or a sprite sheet. Then building it in is quick.
- Real music or a recorded voice. Those are files to be found or made.

**In between: sound**

Simple tones can be generated here with Python's `wave` module -- a click, a
till, a short jingle. It would come out chiptune-ish, which fits pixel art
rather well, but it is maths rather than music and the result is uncertain.
One to two hours with an open end.

For proper music, a royalty-free file is the better route; playing it is
easy. Note that browsers block sound that starts on its own, so it has to
begin on a click -- Start game is the natural place.
