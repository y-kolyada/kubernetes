#!/usr/bin/env python3
"""Check terms: the contract between glossary.html and the in-page .term cards.

Every concept in ru/glossary.html must have at least one interactive in-page
card (.term > .term-btn + .term-card) placed at its primary introduction in the
chapters (01-15), the Engineering Navigator (navigator.html), the Landing page
(index.html), or as an in-page reference in glossary.html itself.

Conversely, every .term card on any page must link to a valid #term-* anchor
defined in ru/glossary.html.

Third, the description of a card must be clean text. A card is written from a
lead that may itself carry a card, and a script that strips that markup badly
leaves the title and the close button of the nested card glued into the
description: «...to the expectationLimit*Number, which...». That happened on
math-core at a green check and was found by an eye on a screenshot (finding 9).

What this side does NOT demand is that the card repeat its article word for
word. A card has eight to fifteen words where an article has a paragraph, and
a shorter wording is the point of it; a synonym is worth more than a copy,
because a reader who has met «the unit circle» in the card and «the circle of
radius one» in the article has met both the way the subject is really spoken.
The machine checks for debris, not for uniformity: an author writing a card
narrower than the article is doing the job, not breaking a contract.

Fourth, every acronym used in the prose must be explained. An acronym looks
like an ordinary word: the author who writes it knows what it means and does
not see the gap, the reader who does not know has no way to ask, and between
those two states there is no signal until a machine makes one. So every
[A-Z]{2,6} token in the body of a page must either appear in a glossary
article's title or object line, or stand in SHELL_WORDS below with a reason.
This part starts working as soon as the glossary has its first article:
before that there is nothing to check against (finding 8, devops-kubernetes).

    python3 tools/check-terms.py
"""

import glob
import html
import os
import re
import sys

GLOSSARY_PATH = os.path.join('ru', 'glossary.html')
GLOSSARY_TERM_RE = re.compile(r'<div class="glossary-term"\s+id="([^"]+)">')
# Сокращения, которые серия сознательно не объясняет нигде: слова оболочки
# страницы и названия ступеней, раскрытые на посадочной и в навигаторе.
SHELL_WORDS = {'HTML', 'CSS', 'AI', 'IGL', 'SRE', 'HTTP'}


def site_words():
    """Сокращения, которые этот сайт не объясняет нарочно.

    Список предметный, поэтому он принадлежит сайту, а не движку: на сайте
    об IAM это ACL и AD, на сайте о Kubernetes - другие. Жить ему в tools/
    нельзя - по §1 сайт не правит движок, - поэтому он лежит в site.conf
    строкой `acronyms = ACL, AD`. Пустая строка означает «объясняем всё».
    """
    try:
        with open('site.conf', encoding='utf-8') as f:
            for line in f:
                name, _, value = line.partition('=')
                if name.strip() == 'acronyms':
                    return {w.strip().upper() for w in value.split(',') if w.strip()}
    except OSError:
        pass
    return set()
ACRONYM_RE = re.compile(r'\b[A-Z]{2,6}\b')
MARKUP_RE = re.compile(r'<pre\b[\s\S]*?</pre>|<code\b[\s\S]*?</code>'
                       r'|<svg\b[\s\S]*?</svg>|<[^>]+>')
GLOSSARY_NAME_RE = re.compile(r'<span class="glossary-title">([^<]*)<'
                              r'|<code class="glossary-object">([^<]*)<')

# Карточка целиком: от «<span class="term">» до ссылки в словарь, и внутрь
# другой карточки эта выборка не заходит - иначе карточка без описания
# утащила бы описание соседней, и сверка ниже сравнивала бы чужие тексты.
IN_PAGE_TERM_RE = re.compile(
    r'<span class="term">((?:(?!<span class="term">)[\s\S])*?)'
    r'<span class="term-links"><a href="([^"]+)"'
)
CARD_DESC_RE = re.compile(r'<span class="term-desc">([\s\S]*)</span>\s*$')
GLOSSARY_LEAD_RE = re.compile(
    r'<div class="glossary-term" id="([^"]+)">([\s\S]*?)<div class="glossary-meta"')
LEAD_TEXT_RE = re.compile(r'<p class="glossary-lead">([\s\S]*?)</p>')


def drop_cards(chunk):
    """Снять всплывающие карточки, оставив слова, на которых они висят.

    Лид статьи словаря сам может нести карточку внутри себя, и тогда слепое
    снятие тегов приклеило бы к описанию название и крестик вложенной
    карточки. Скобки считаются руками, а не регулярным выражением: вложенные
    <span> ему не по зубам, а ошибка здесь тихая.
    """
    out = []
    i = 0
    while True:
        start = chunk.find('<span class="term-card"', i)
        if start < 0:
            out.append(chunk[i:])
            return ''.join(out)
        out.append(chunk[i:start])
        depth = 0
        k = start
        while k < len(chunk):
            opened = chunk.find('<span', k)
            closed = chunk.find('</span>', k)
            if closed < 0:
                k = len(chunk)
                break
            if 0 <= opened < closed:
                depth += 1
                k = opened + 5
            else:
                depth -= 1
                k = closed + 7
                if depth == 0:
                    break
        i = k


# Знак препинания, оставшийся за снятым тегом, отделяется от слова пробелом,
# и «переменных.» превращается в «переменных .». Та же склейка сделана в
# tools/build-search.py по той же причине.
GAP_RE = re.compile(r'\s+([?!,.:;)])')


# Обломки, которые остаются от плохо снятой разметки вложенной карточки.
# Склейка ищется только по кириллице: русское слово внутри себя заглавной
# буквы не имеет, а латинское («MathML», «GitHub») имеет законно.
GLUED_RE = re.compile(r'[а-яё][А-ЯЁ]')
CLOSE_RE = re.compile(r'\S[\u00D7\u2715\u2716]\S')
CARD_INSIDE_RE = re.compile(r'<span class="term"|<button')


def debris(chunk):
    """Назвать обломок в описании карточки или вернуть пустую строку."""
    if CARD_INSIDE_RE.search(chunk):
        return 'внутри описания осталась разметка карточки'
    said = plain(chunk)
    if CLOSE_RE.search(said):
        return 'в описании крестик закрытия вложенной карточки'
    found = GLUED_RE.search(said)
    if found:
        return 'два слова слиплись: «%s»' % said[max(0, found.start() - 12):found.end() + 12]
    return ''


def plain(chunk):
    """Текст без разметки, без двойных пробелов и без щелей перед точкой."""
    words = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', chunk)).split())
    return GAP_RE.sub(r'\1', words)


def main():
    if not os.path.isfile(GLOSSARY_PATH):
        print()
        print('  Двусторонний контракт терминов')
        print('  ' + '-' * 46)
        print('  терминов в словаре: 0 (словарь ещё не создан)')
        print('  ----------------------------------------------')
        print('  ЗЕЛЁНОЕ')
        print()
        return 0

    with open(GLOSSARY_PATH, encoding='utf-8') as f:
        glossary_html = f.read()

    glossary_terms = GLOSSARY_TERM_RE.findall(glossary_html)
    if not glossary_terms:
        print()
        print('  Двусторонний контракт терминов')
        print('  ' + '-' * 46)
        print('  терминов в словаре: 0 (пустой каркас словаря)')
        print('  ----------------------------------------------')
        print('  ЗЕЛЁНОЕ')
        print()
        return 0

    glossary_term_set = set(glossary_terms)
    leads = {}
    for anchor, block in GLOSSARY_LEAD_RE.findall(glossary_html):
        found = LEAD_TEXT_RE.search(block)
        if found:
            leads[anchor] = plain(drop_cards(found.group(1)))

    # Scan all Russian pages
    ru_files = sorted(glob.glob(os.path.join('ru', '*.html')))
    term_counts = {}
    found_term_links = {}  # term_id -> list of (file, href)
    broken_links = []      # (file, href, reason)
    drifted = []           # (file, anchor, описание карточки, лид статьи)
    compared = 0           # сверенных описаний
    acronyms = {}          # сокращение -> страницы, где встретилось

    total_cards = 0
    landing_cards = 0
    chapter_cards = 0
    navigator_cards = 0
    glossary_cards = 0

    for file_path in ru_files:
        basename = os.path.basename(file_path)
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        matches = IN_PAGE_TERM_RE.findall(content)
        count = len(matches)
        total_cards += count
        term_counts[basename] = count

        if basename == 'index.html':
            landing_cards += count
        elif basename == 'navigator.html':
            navigator_cards += count
        elif basename == 'glossary.html':
            glossary_cards += count
        elif re.match(r'^\d{2}\.html$', basename):
            chapter_cards += count

        if '<main' in content and '</main>' in content:
            body = content[content.index('<main'):content.index('</main>')]
            for found in ACRONYM_RE.finditer(MARKUP_RE.sub(' ', body)):
                acronyms.setdefault(found.group(0), set()).add(basename)

        for body, href in matches:
            target_page, _, anchor = href.partition('#')
            if not anchor:
                broken_links.append((basename, href, 'ссылка не содержит якоря'))
                continue

            if anchor not in glossary_term_set:
                broken_links.append((basename, href, f'якорь #{anchor} отсутствует в словаре'))
                continue

            found_term_links.setdefault(anchor, []).append((basename, href))

            # Третья сторона контракта: в описании карточки нет обломков.
            # Проверяется мусор, а не единообразие: карточка на восемь слов
            # вправе сказать то же короче и другими словами, чем статья на
            # абзац, и синоним там полезнее копии (находка 9, math-core).
            desc = CARD_DESC_RE.search(body)
            if desc is None:
                continue
            compared += 1
            why = debris(desc.group(1))
            if why:
                drifted.append((basename, anchor, why, plain(desc.group(1))))

    # Identify glossary terms missing in-page markup
    missing_in_pages = [t for t in glossary_terms if t not in found_term_links]

    explained = set()
    for found in GLOSSARY_NAME_RE.finditer(glossary_html):
        explained.update(ACRONYM_RE.findall(found.group(1) or found.group(2)))
    skip = SHELL_WORDS | site_words()
    unexplained = sorted(a for a in acronyms if a not in explained and a not in skip)

    has_errors = bool(broken_links or missing_in_pages or unexplained or drifted)

    print()
    print('  Двусторонний контракт терминов')
    print('  ' + '-' * 46)
    print(f'  терминов в словаре:          {len(glossary_terms)}')
    print(f'  карточек .term на страницах: {total_cards}')
    print(f'    из них на посадочной:      {landing_cards}')
    print(f'    из них в главах (01-15):   {chapter_cards}')
    print(f'    из них в навигаторе:       {navigator_cards}')
    print(f'    из них в словаре:          {glossary_cards}')
    print(f'  покрытие терминов словаря:   {len(found_term_links)}/{len(glossary_terms)}')
    print(f'  неразмеченных терминов:      {len(missing_in_pages)}')
    print(f'  битых ссылок на термины:     {len(broken_links)}')
    print(f'  сокращений в тексте:         {len(acronyms)}, без объяснения: {len(unexplained)}')
    print(f'  описаний карточек проверено: {compared}, с обломками: {len(drifted)}')

    if missing_in_pages:
        print()
        print('  ОШИБКА: следующие термины словаря не имеют интерактивных карточек .term:')
        for t in missing_in_pages[:10]:
            print(f'    -> #{t}')
        if len(missing_in_pages) > 10:
            print(f'    -> ... и ещё {len(missing_in_pages) - 10}')

    if broken_links:
        print()
        print('  ОШИБКА: обнаружены некорректные ссылки в карточках .term:')
        for b_file, b_href, b_why in broken_links[:10]:
            print(f'    -> {b_file}: {b_href} ({b_why})')

    if drifted:
        print()
        print('  ОШИБКА: в описании карточки остались обломки разметки:')
        for d_file, d_anchor, d_why, d_said in drifted[:10]:
            print(f'    -> {d_file} #{d_anchor}: {d_why}')
            print(f'       {d_said[:90]}')
        if len(drifted) > 10:
            print(f'    -> ... и ещё {len(drifted) - 10}')

    if unexplained:
        print()
        print('  ОШИБКА: сокращения введены в тексте и нигде не объяснены:')
        for a in unexplained[:10]:
            print(f'    -> {a} ({", ".join(sorted(acronyms[a])[:4])})')
        if len(unexplained) > 10:
            print(f'    -> ... и ещё {len(unexplained) - 10}')
        print('  Либо статья в словаре, либо строка `acronyms =` в site.conf с причиной.')

    print('  ' + '-' * 46)
    if has_errors:
        print('  КРАСНОЕ')
        print()
        return 1
    else:
        print('  ЗЕЛЁНОЕ')
        print()
        return 0


if __name__ == '__main__':
    sys.exit(main())
