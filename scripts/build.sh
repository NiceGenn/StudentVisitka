#!/usr/bin/env bash
#
# Сборка релиза статического сайта.
#
#   ./scripts/build.sh            -> dist/ + release/visitka-student-<версия>.zip
#   ./scripts/build.sh 1.2.0      -> та же сборка с явно заданной версией
#
# Сборка намеренно простая: сайт статический, шаг сборки только копирует
# src/ в dist/, проверяет целостность ссылок и упаковывает архив.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/src"
DIST="$ROOT/dist"
RELEASE="$ROOT/release"

VERSION="${1:-$(sed -n 's/^## \[\([0-9][^]]*\)\].*/\1/p' "$ROOT/CHANGELOG.md" | head -n1)}"
VERSION="${VERSION:-0.0.0}"
NAME="visitka-student-v${VERSION}"

echo "==> Сборка ${NAME}"

rm -rf "$DIST"
mkdir -p "$DIST" "$RELEASE"
cp -R "$SRC"/. "$DIST"/

# Файл для GitHub Pages: отключает обработку Jekyll.
touch "$DIST/.nojekyll"

# Визитница генерируется из data/ — предупреждаем, если страница отстала.
for data_file in "$ROOT"/data/*.json; do
  if [ -e "$data_file" ] && [ "$data_file" -nt "$SRC/leaders.html" ]; then
    echo "==> ВНИМАНИЕ: $(basename "$data_file") новее src/leaders.html"
    echo "    выполните: python3 scripts/gen_leaders.py"
    break
  fi
done

echo "==> Проверка внутренних ссылок"
missing=0
while IFS= read -r page; do
  while IFS= read -r link; do
    [ -e "$DIST/$link" ] || { echo "    ОШИБКА: $(basename "$page") -> $link (файл отсутствует)"; missing=$((missing + 1)); }
  done < <(grep -oh 'href="[a-zA-Z0-9._/-]*\.html"\|href="assets/[^"]*"\|src="assets/[^"]*"' "$page" \
             | sed 's/^[a-z]*="//; s/"$//' | sort -u)
done < <(find "$DIST" -name '*.html')

if [ "$missing" -gt 0 ]; then
  echo "==> Найдено битых ссылок: $missing (см. docs/STRUCTURE.md, раздел «Известные пробелы»)"
else
  echo "==> Битых ссылок нет"
fi

echo "==> Упаковка архива"
rm -f "$RELEASE/${NAME}.zip"
( cd "$DIST" && zip -qr "$RELEASE/${NAME}.zip" . )

echo "==> Готово:"
echo "    каталог: dist/"
echo "    архив:   release/${NAME}.zip ($(du -h "$RELEASE/${NAME}.zip" | cut -f1))"
