# Record 18 - the second half of the engine, and a check that can redden

**Site:** `devops-kubernetes`. **Date:** 27.10.2026. **Host:** dev0.
**Work order:** `lessons/step-18.md`. **Authorization:** «принято - действуем».
**Diffs measured from** `25f3a9b`.

## What was taken

Seven items, copied from `seed/swa` and verified **byte for byte** by `diff -q`:

| Item | Lines of diff | What it brings |
| :-- | --: | :-- |
| `check.sh` | 3 | the thirteenth and fourteenth run lines |
| `tools/check-struct.py` | 147 | the stub contract - this site's own finding 10, come home |
| `tools/check-pages.mjs` | 64 | «no browser» told apart from «browser present, libraries missing» |
| `tools/build-meta.py` | 7 | `<math>` stripped before the word count |
| `tools/check-diagrams.mjs` | 2 | diagrams counted against the pages that carry them |
| `tools/build-math.py` | new | prints MathML from a TeX source |
| `tools/vendor/latex2mathml/` | new, 14 files, 356K | the converter imported at module load |

`tools/new-site.py` was deliberately left in the seed: the stamp has no work on a stamped site.

**Everything else now matches the seed.** The complete list of remaining differences across
`assets/`, `tools/` and `check.sh`, printed by machine rather than counted:

- `tools/check-examples.sh` and `tools/claims.tsv` - the site's own files by §1;
- `assets/search-{ru,en,uk,de}.js` - this site's generated indexes, which exist nowhere else;
- `tools/new-site.py` - present in the seed, absent here, as predicate 1.3 requires.

`tools/check-claims.sh` is also the site's own file by §1, and it happens to be identical to the
seed's skeleton: this site has never needed to change it.

## Fourteen lines

`./check.sh` is ЗЕЛЁНОЕ with every line ДА. The two new ones report:

- **перевод и заглушки:** `страниц сверено: 54 (переводов 3, заглушек 51), расходятся: 0`, and
  each page prints which of the two contracts applied, so the day a language stops being a stub
  is visible in the output;
- **формулы:** `формул на сайте: 0`.

The run rewrote nothing: `git status` over `ru/ en/ uk/ de/` was empty after it, and
`build-meta.py` reported `страниц в порядке: 72` without touching a page.

## Both new lines proved by corruption

Per `AGENTS.md` §6.8в - the rule this site wrote and seeded as finding 11 - each corruption went
into a **copy** and the restore came from the copy. `git checkout` was not used.

**The stub contract.** The `<h1>` of `de/15.html` was put back to the Russian original's
(`Вопросы · IGL` in place of `Fragen · IGL`). The check went КРАСНОЕ and named the page and
both reasons at once:

```
[ НЕТ ] de/15.html             · заглушка
      -> заголовок не переведён, совпадает с оригиналом: «Вопросы · IGL»
      -> осталась кириллица: 7 символов
страниц сверено: 54 (переводов 3, заглушек 51), расходятся: 1
```

**The formula check.** One box `<span class="math" data-tex="\frac{n(n+1)}{2}">ЭТО НЕ ТА
ФОРМУЛА</span>` was spliced into `ru/01.html`. КРАСНОЕ, naming the page and the source:

```
[ НЕТ ] ru/01.html
      -> формула разошлась с источником: \frac{n(n+1)}{2}
формул на сайте: 1
```

Both pages were restored from their copies and `git status` over the four language folders came
back empty. All 45 claims stayed green throughout.

## Finding 12 recorded, after the first version of it was wrong

The first run of `./check.sh` this shift was КРАСНОЕ on «утверждения сайта» and «примеры
запускаются» - 19 of 45 claims - because the symlink `node_modules -> ../../node_modules` was
absent. It is in `.gitignore`, so it never travels with the repository.

**What I said in chat first, and it was wrong:** that nothing creates the symlink. `bootstrap.sh`
does, at line 55, and it even refuses to create a dangling one, explaining in a comment that a
dangling link fails worse than a missing one. Measured before the finding was written, which is
why the finding says something else and something true: the symlink is created **once, at stamp
time, and only if the target existed then**, and nothing ever restores it. Four of the eleven
sites of the series are without it today - `bash` (stamped 17.10), `docker`, `helm`,
`linux-containers` (all three stamped 25.10 on dev1). The cost is not the missing module but the
shape of the complaint: 19 Node stack traces of fifteen lines each, where the browser check in
the same harness prints one sentence and the repair command.

The proposal to the seed is one guard at the top of `check.sh`: if `node_modules/js-yaml` does
not resolve, print the one-line repair instead of letting 19 claims accuse themselves.

## Records closed

Two lines of `lessons/backlog.md` read «уходит в росток отдельным заданием» although findings 10
and 11 were seeded on 25.10 as commit `334c8f9` of the monorepo. Both now say so, and both say
the rule came back here by this step.

## The predicates

| Predicate | Verdict | Proved by |
| :-- | :-- | :-- |
| 1. The engine is identical to the seed | **ДА** | `diff -q` on seven items; the full difference list printed above |
| 2. Fourteen lines green, both new ones can redden | **ДА** | `./check.sh` ЗЕЛЁНОЕ 14/14; two corruptions with distinct messages |
| 3. Records say what was learned, diff stays inside the harness | **ДА** | finding 12, two backlog lines, diff touches only `check.sh`, `tools/`, `lessons/` |

## Deviations reported

1. **A false statement in chat, corrected before it reached a file.** See above: «nothing
   creates the symlink». The habit that caught it is the one this site already wrote down - a
   recorded finding is a claim, so its numbers get measured before they are written. The cost
   was two commands.
2. **Harness language.** `AGENTS.md` line 4 says the harness is English. `lessons/step-18.md`
   and this record are. `lessons/notes-1.md` and the body lines of `lessons/backlog.md` are
   Russian and were already Russian before this step; I matched each file rather than converting
   two documents inside an engine-sync step. The drift is older than this step and is not
   repaired by it.

## Boundaries held

No `git push`. No merge into `main` or `prod`. No `site.conf`, no `version` bump. Nothing under
`ru/ en/ uk/ de/` or `assets/`. The symlink was not committed and was not turned into a file.
The six sibling sites were not touched; the seed's repair for finding 12 is a proposal, not work
done here.
