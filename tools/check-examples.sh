#!/usr/bin/env bash
# Example check: the manifests shown on the pages are parsed, not trusted.
#
#     tools/check-examples.sh [page...]        default: every page in ru/
#
# THIS FILE IS THE SITE'S OWN. The mechanism is shared across the series, the
# interpreter is not (§1 AGENTS.md): Bash runs with bash, Terraform with
# terraform validate, and the manifests of this site are parsed as YAML.
#
# Every <pre> declares its kind in the markup, so the contract is visible to a
# reader of the page and not guessed by this script:
#
#   data-run="syntax"  parsed, never executed. Every YAML document in the block
#                      must parse, and a document that names a kind must also
#                      name an apiVersion: a fragment is allowed, a half-object
#                      is not.
#   data-run="cmd"     command lines. Checked twice and never executed against
#                      a cluster: the block must parse as a shell script
#                      (bash -n), and every flag of every kubectl invocation
#                      must exist in that command's own --help, unioned with
#                      the global flags of `kubectl options`. An invented or
#                      renamed flag is the one defect no human eye catches.
#   data-run="run"     not supported on this site while there is no cluster:
#                      a block that claims execution would claim an API server
#                      this host does not have.
#   data-run="setup"   the same, and for the same reason.
#
# WHY YAML AND NOT THE KUBERNETES SCHEMA. Schema validation needs a live API
# server: measured here on 24.10.2026, `kubectl apply --dry-run=client` fails
# without one even with --validate=false, because it cannot recognise the
# resource without the server's API group list. So the manifest check proves
# exactly what it can prove - a well-formed document with the keys the page
# says it has - and the kubectl client is used for what it can do offline:
# generating manifests and answering which flags exist. The line about a live
# cluster stands in lessons/backlog.md.
#
# Output is Russian: it speaks to the person who accepts the work.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

PAGES=("$@")
[ ${#PAGES[@]} -gt 0 ] || PAGES=(ru/*.html)

g() { printf '\033[32m%s\033[0m' "$1"; }
r() { printf '\033[31m%s\033[0m' "$1"; }

FAIL=0
PARSED=0
ok()  { printf '  [ %s ] %s\n' "$(g 'ДА ')" "$1"; }
bad() { printf '  [ %s ] %s\n' "$(r 'НЕТ')" "$1"; FAIL=$((FAIL + 1)); }

tmp=$(mktemp -d "${TMPDIR:-/tmp}/examples.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/blocks"

python3 - "$tmp/blocks" "${PAGES[@]}" > "$tmp/list" <<'PY' || exit 2
import html, pathlib, re, sys

CODE = re.compile(r'<pre\b([^>]*)>\s*<code\b[^>]*>(.*?)</code>\s*</pre>', re.S | re.I)
KIND = re.compile(r'data-run="([a-z]+)"')

out = pathlib.Path(sys.argv[1])
for page in sys.argv[2:]:
    text = pathlib.Path(page).read_text(encoding='utf-8')
    for number, match in enumerate(CODE.finditer(text), 1):
        found = KIND.search(match.group(1))
        name = '%s-%d' % (pathlib.Path(page).stem, number)
        kind = found.group(1) if found else 'нет'
        suffix = '.sh' if kind == 'cmd' else '.yaml'
        (out / (name + suffix)).write_text(html.unescape(match.group(2)) + '\n',
                                           encoding='utf-8')
        print('%s\t%s\t%s' % (page, name, kind))
PY

echo
echo "  Примеры со страниц разбираются"
echo "  ----------------------------------------------"

BLOCKS=$(wc -l < "$tmp/list")

if [ "$BLOCKS" -eq 0 ]; then
  printf '  блоков кода на страницах: 0\n'
  printf '  страницы пока не показывают кода, который надо разбирать\n'
  echo "  ----------------------------------------------"
  printf '  %s\n\n' "$(g 'ЗЕЛЁНОЕ')"
  exit 0
fi

if [ ! -e node_modules/js-yaml ]; then
  printf '  блоков кода на страницах: %s\n' "$BLOCKS"
  printf '  разбирать их нечем: нет node_modules/js-yaml\n'
  printf '  симлинк на общий node_modules ставится при штампе сайта (BRIEF.md §1)\n'
  echo "  ----------------------------------------------"
  printf '  %s\n\n' "$(r 'КРАСНОЕ')"
  exit 1
fi

while IFS=$'\t' read -r page id kind; do
  if [ "$kind" = "cmd" ]; then block="$tmp/blocks/$id.sh"; else block="$tmp/blocks/$id.yaml"; fi
  case "$kind" in
    syntax)
      report=$(node -e '
        const fs = require("fs");
        const yaml = require(process.cwd() + "/node_modules/js-yaml");
        const text = fs.readFileSync(process.argv[1], "utf8");
        let docs;
        try { docs = yaml.loadAll(text); }
        catch (e) { console.log("разбор не прошёл: " + e.message.split("\n")[0]); process.exit(1); }
        const real = docs.filter(d => d !== null && d !== undefined);
        if (real.length === 0) { console.log("блок пуст: ни одного документа"); process.exit(1); }
        for (const d of real) {
          if (d && typeof d === "object" && "kind" in d && !("apiVersion" in d)) {
            console.log("документ " + d.kind + " без apiVersion");
            process.exit(1);
          }
        }
        const named = real.filter(d => d && typeof d === "object" && "kind" in d);
        console.log(named.length
          ? "документов: " + real.length + ", объектов: " + named.map(d => d.kind).join(", ")
          : "документов: " + real.length + ", фрагмент без kind");
      ' "$block" 2>&1)
      if [ $? -eq 0 ]; then
        PARSED=$((PARSED + 1))
        ok "$id · $report ($page)"
      else
        bad "$id · $report ($page)"
      fi
      ;;
    cmd)
      if ! shell=$(bash -n "$block" 2>&1); then
        bad "$id · оболочка не разбирает блок: $(printf '%s' "$shell" | head -1) ($page)"
      else
        report=$(python3 - "$block" <<'PY' 2>&1
import shlex, subprocess, sys, pathlib, re

text = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
text = re.sub(r'\\\n\s*', ' ', text)          # склеить перенос строки обратным слэшем

def flags_of(args):
    """Флаги, которые знает сама команда. None, если команды нет вовсе."""
    done = subprocess.run(['kubectl', *args, '--help'], capture_output=True, text=True)
    if done.returncode != 0 or not done.stdout.strip():
        return None
    found = set(re.findall(r'--[a-zA-Z0-9][a-zA-Z0-9-]*', done.stdout))
    found |= set(re.findall(r'(?<![\w-])-[a-zA-Z](?=[,= ])', done.stdout))
    return found


def known_flags(path):
    """Справка самой длинной команды, которую kubectl признаёт в этом пути.

    Путь собран из слов до первого флага, и в него могло попасть имя ресурса
    («logs deployment/web»). Поэтому хвост отбрасывается по одному слову, но
    первое слово обязано быть настоящей командой: иначе опечатка в глаголе
    прошла бы молча - у несуществующей команды нет флагов, и сверять нечего.
    """
    for depth in range(len(path), 0, -1):
        found = flags_of(path[:depth])
        if found is not None:
            return found
    return None

# Глобальные флаги живут только в `kubectl options`: в справке команды их нет.
_options = subprocess.run(['kubectl', 'options'], capture_output=True, text=True).stdout
GLOBAL = set(re.findall(r'--[a-zA-Z0-9][a-zA-Z0-9-]*', _options))
GLOBAL |= set(re.findall(r'(?<![\w-])(-[a-zA-Z]),', _options))

SEPARATORS = {'|', '||', '&&', ';', '&'}
checked = calls = 0
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    try:
        tokens = shlex.split(line, comments=True)
    except ValueError as e:
        print('строка не разбирается: %s' % e)
        sys.exit(1)
    segment = []
    segments = [segment]
    for token in tokens:
        if token in SEPARATORS:
            segment = []
            segments.append(segment)
        else:
            segment.append(token)
    for seg in segments:
        if not seg or seg[0] != 'kubectl':
            continue
        calls += 1
        path, rest = [], seg[1:]
        i = 0
        while i < len(rest) and len(path) < 3:
            token = rest[i]
            if token.startswith('-'):
                if '=' not in token and i + 1 < len(rest) and not rest[i + 1].startswith('-') and not path:
                    i += 1               # глобальный флаг со значением перед глаголом
            else:
                path.append(token)
            i += 1
        if not path:
            print('kubectl без команды: %s' % line[:40])
            sys.exit(1)
        known = known_flags(path)
        if known is None:
            print('kubectl не знает команду «%s»' % path[0])
            sys.exit(1)
        known |= GLOBAL
        for token in rest:
            if not token.startswith('-') or token == '-':
                continue
            name = token.split('=', 1)[0]
            if name not in known:
                print('у «kubectl %s» нет флага %s' % (' '.join(path), name))
                sys.exit(1)
            checked += 1
if calls == 0:
    print('команд kubectl нет, блок разобран оболочкой')
else:
    print('вызовов kubectl: %d, флагов сверено со справкой: %d' % (calls, checked))
PY
)
        if [ $? -eq 0 ]; then
          PARSED=$((PARSED + 1))
          ok "$id · $report ($page)"
        else
          bad "$id · $report ($page)"
        fi
      fi
      ;;
    run|setup)
      bad "$id · пометка data-run=\"$kind\" на этом сайте не поддержана: кластера нет ($page)"
      ;;
    нет)
      bad "$id · блок без пометки data-run ($page)"
      ;;
    *)
      bad "$id · неизвестная пометка data-run=\"$kind\" ($page)"
      ;;
  esac
done < "$tmp/list"

echo "  ----------------------------------------------"
printf '  блоков кода: %s, разобрано: %s\n' "$BLOCKS" "$PARSED"
if [ "$FAIL" -eq 0 ]; then
  printf '  %s\n\n' "$(g 'ЗЕЛЁНОЕ')"
else
  printf '  %s  - блоков со словом НЕТ: %s\n\n' "$(r 'КРАСНОЕ')" "$FAIL"
fi
[ "$FAIL" -eq 0 ]
