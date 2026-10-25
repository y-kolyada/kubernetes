# Record 17 - the first other site under the new engine

**Order:** `lessons/step-17.md`. **Site:** `devops-kubernetes`. **Date:** 25.10.2026.
**Pilot:** Claude Code (Opus 5). **Architect:** Conductor (`ik`).

## How this site was chosen

By measurement, not by guess. The seed's `tools/check-terms.py` was run against all nine sites
of the series without touching a file. My prediction had been `bash`, as the site with the most
releases; the prediction was wrong. The red was distributed differently:

- four sites are red **today, on their own checks**: `bash` (17 glossary terms with no card),
  `git` (24), `observability` (1 term + 2 broken anchors), `terraform` (navigation not rebuilt);
- five sites go red only under the seed's acronym side, which arrived on 23.10 and is not mine;
- `kubernetes` was the only site red on the **third side** - the one I seeded - and on two cards.

So the pilot is the site with the smallest honest delta and a defect of exactly the new kind.

## What was found and healed

1. **Spliced card description** (`#term-pod` on `ru/03.html` and `ru/index.html`): the whole
   nested card - title, close button, link label - sat inside the description, and the sentence
   was said twice. `tools/build-terms.py` does not generate descriptions, so this was written
   once by a hand and nothing would re-create it. Third instance of findings 9 and 16: blind tag
   stripping where markup is nested, and the first one found by a machine rather than an eye.
2. **A card that fell inside another word.** Found by the Conductor reading the page, not by any
   check: in «Под не поднимается, вы удаляете его и создаёте заново» the card for «под» had been
   placed on the first three letters of «поднимается». The term is Pod; the word is «rises».
   A substring match with no word boundary.
3. **Five more splices of the same family**, where the card covered the stem and the ending stayed
   outside: «подов», «автомасштабирования», «разброса», «метках», «сервиса». The dashed underline
   broke off mid-word. Endings pulled inside the buttons.
4. **A defect of mine in the engine.** `find()` in `assets/search.js` returns `{total, shown}`,
   but its early return on a query shorter than two characters still returned a bare `[]`. So
   `render` threw `Cannot read properties of undefined (reading 'length')` **every time the search
   panel opened**. It was invisible: the panel still opens, and I had only ever tested it with a
   query already typed. Fixed in the seed and in both sites that carry the engine.

## Engine sync

`tools/check-terms.py` (142 -> 320 lines), `tools/build-search.py`, `assets/search.js`,
`assets/style.css` taken from the seed. Checked by machine that no selector the site had was
lost: 0 lost, 19 new. Search index rebuilt: 152 records, six kinds, five fields per record.

## Facets, verified in the site's own browser

At 390px, light and dark, through a real click on `.find-btn`:

- six facets lit by default: Темы, Примеры, Вопросы, Навигатор, Словарь, Витрина;
- the counter is true, not capped: `Найдено: 131, показаны первые 40`, and switching Вопросы off
  gives `Найдено: 116` - fifteen question pages gone, which is the real number;
- the top-level section badge is amber: `rgba(252, 189, 74, 0.28)` light, `0.22` dark;
- the reset button is present; no JavaScript errors after the fix above.

## The predicates

| Predicate | Verdict | Proved by |
| :-- | :-- | :-- |
| 1. Seed's terms check prints ЗЕЛЁНОЕ, 60 cards, 0 debris | **ДА** | `python3 tools/check-terms.py` |
| 2. `#term-pod` description is one clean sentence on both pages | **ДА** | no `&times;`, no nested tag, no «В словарь понятий», no repeated clause |
| 3. Site's terms check identical to the seed, `./check.sh` ЗЕЛЁНОЕ | **ДА** | `diff` clean, full check green |
| 4. Facets live at 390px in both themes | **ДА** | the browser run above |

## Deviation reported

I wrote `lessons/step-10.md` with `cat >` without checking the file existed, and overwrote the
accepted work order for the Navigator, dated 24.10.2026. Restored from `HEAD` with no loss and
rewritten as `step-17.md`. **Root cause:** I read `ls lessons/ | tail` as the highest number,
but that listing is alphabetical, and `step-9` sorts after `step-16`. A free number is found by
sorting numerically, never by the tail of a listing.
