# Step 17 - heal the spliced card, sync the engine, and bring the facets

**Where this came from.** A measurement, not a complaint. The seed's `tools/check-terms.py`
was run against all nine sites of the series without touching a file. Eight were green on the
third side of the term contract; `kubernetes` was the one red, and it is red on two cards.

**The defect.** The description of `#term-pod` on `ru/03.html` and `ru/index.html` carries a whole
nested card spliced into it. The rendered text reads:

> Наименьшая единица размещения: один или несколько контейнеров**Под (Pod)×Наименьшая единица
> размещения: один или несколько контейнеров с общим сетевым пространством имён и общими
> томами.В словарь понятий** с общим сетевым пространством имён и общими томами.

The title of the nested card, its close button and its link label all landed inside the
description, and the sentence is said twice. The glossary article `#term-pod` does carry a card
for «контейнеров» in its lead, which is allowed; whoever wrote these two cards copied the lead
with that markup in it. `tools/build-terms.py` does not generate descriptions, so nothing will
re-create this: it is data, written once by a hand.

**Third instance of one root cause.** Findings 9 and 16 on `math-core` were the same thing -
blind tag stripping where markup is nested. This is the third, and the first found by a machine
rather than an eye on a screenshot.

**Predicates:**

1. The seed's `tools/check-terms.py`, run in this site, prints `ЗЕЛЁНОЕ` and the line
   `описаний карточек проверено: 60, с обломками: 0`.
2. The description of `#term-pod` on `ru/03.html` and `ru/index.html` is one clean sentence:
   no repeated clause, no `×`, no «В словарь понятий» inside the description, and no nested
   `<span class="term"` or `<button` within it. Its meaning matches the glossary article.
3. `tools/check-terms.py` in this site is identical to the seed's, and `./check.sh` stays
   `ЗЕЛЁНОЕ` - so the site holds the rule itself from now on, instead of the seed holding it
   from outside.

4. **Фасеты поиска живьём.** После синхронизации движка поисковый индекс пересобран и несёт
   пятое поле - вид страницы. Окно поиска показывает ряд фасетов, счётчик найденного и янтарный
   значок раздела верхнего уровня. Проверяется в браузере, на 390px, в обеих темах.
