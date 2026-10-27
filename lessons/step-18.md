# Step 18 - take the second half of the engine from the seed

**Site:** `devops-kubernetes`, published at `/kubernetes/`.
**Date:** 27.10.2026.
**Pilot:** Claude Code (Opus 5), host dev0.
**Architect:** Conductor (`ik`). Authorization: «принято - действуем», on the fork offered in chat.

**State before the work.** `./check.sh` is ЗЕЛЁНОЕ on twelve lines, 45 claims green, the tree
clean, `dev` at `25f3a9b` and level with `origin/dev`.

## Where this came from

Not a complaint and not a defect of the site: a measurement. Every engine file of the site was
compared with the seed, and the previous sync (`faef561`, step 17, host dev1) turns out to have
taken four files - `tools/check-terms.py`, `tools/build-search.py`, `assets/search.js`,
`assets/style.css` - and left the rest behind. Among what it left is this site's own seeding:
the stub contract of `tools/check-struct.py`, written here from finding 10 and seeded into the
seed as commit `334c8f9` of the monorepo. The site that paid for the rule does not hold it.

Seven files are behind:

| File | What the site is missing |
| :-- | :-- |
| `check.sh` | twelve run lines instead of fourteen |
| `tools/check-struct.py` | the stub contract - the answer to finding 10 |
| `tools/check-pages.mjs` | telling «no browser» apart from «browser present, libraries missing» |
| `tools/build-meta.py` | stripping `<math>` before the word count |
| `tools/check-diagrams.mjs` | the count of diagrams against the pages that carry them |
| `tools/build-math.py` | new: prints MathML from a TeX source |
| `tools/vendor/latex2mathml/` | new: the converter `build-math.py` imports at load |

**Why `tools/vendor/` comes too, on a site with no formulas.** `build-math.py` runs
`from latex2mathml.converter import convert` at module load, so without the library the
fourteenth line of `check.sh` raises instead of printing zero. 488K and fourteen files are the
price of one engine for the whole series, and the alternative - a `check.sh` that differs from
the seed's by one line - makes the next sync a negotiation instead of a copy.

**Measured before this step was written, with no file touched:** the seed's own copies, run from
the site's directory, print `страниц сверено: 54 (переводов 3, заглушек 51), расходятся: 0` and
`формул на сайте: 0`, both ЗЕЛЁНОЕ. The site passes the two new lines as it stands.

## Predicates

Exactly three.

### 1. The engine is identical to the seed

1. Each of the seven files above is **byte for byte** the seed's copy.
2. Across all of `assets/`, `tools/` and `check.sh`, the only remaining differences from the
   seed are the three files §1 declares the site's own (`tools/check-examples.sh`,
   `tools/check-claims.sh`, `tools/claims.tsv`) and the four generated search indexes
   (`assets/search-{ru,en,uk,de}.js`). Checked by machine, printed as a list, not as a count.
3. `tools/new-site.py` stays out: the stamp belongs to the seed and has no work on a stamped
   site.

### 2. Fourteen lines green, and the new ones can redden

1. `./check.sh` prints ЗЕЛЁНОЕ with **fourteen** result lines, every one ДА.
2. The line «перевод и заглушки» reports `страниц сверено: 54 (переводов 3, заглушек 51),
   расходятся: 0`; the line «формулы» reports `формул на сайте: 0`.
3. **Each new line is proved by corruption**, so that neither is a check with nothing to redden:
   the stub contract reddens on a stub whose title is put back to Russian, and it names the
   page and the reason. Per `AGENTS.md` §6.8в the corruption goes into a **copy** and the
   restore comes from the copy - `git checkout` is not the way back before the commit.
4. The claims keep passing: `tools/check-claims.sh` green on all 45.

### 3. The records say what was learned, and the diff stays inside the harness

1. The two lines of `lessons/backlog.md` for findings 10 and 11 are closed: each states it was
   seeded by step 16, commit `334c8f9`, and arrived back here by this step.
2. `lessons/notes-1.md` carries a new finding with its measurement: the site's checks depend on
   a `node_modules` symlink that `.gitignore` documents and nothing creates, and when it is
   absent the claims print a Node stack trace instead of naming the missing dependency - 19 red
   claims for a reason that has nothing to do with knowledge, on a fresh clone of any site of
   the series.
3. The diff touches only `check.sh`, `tools/`, `lessons/`. **Nothing under `ru/ en/ uk/ de/`**,
   nothing under `assets/`, no `site.conf`, no `version` bump.

## Boundaries

1. **No `git push`, no merge into `main` or `prod`.** The work stops at a local commit on `dev`.
2. **The symlink is not committed** and is not made into a file: it is ignored by design. The
   repair of the class belongs to the seed, as the finding says, and is a line in the backlog,
   not work in this step.
3. **The six sibling sites** stay untouched. The harness reaches them with their own shifts, by
   the Architect's decision of 25.10.2026.
4. **Formulas are not written.** The math machinery arrives dormant and prints zero.
