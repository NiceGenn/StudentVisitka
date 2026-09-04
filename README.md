# VisitkaStudent — сайт администрации города Благовещенска

Статический сайт-визитка органов местного самоуправления: восемь страниц,
общая таблица стилей, немного JavaScript. Ни сборщиков, ни зависимостей —
достаточно открыть `src/index.html` в браузере.

## Быстрый старт

```bash
git clone https://github.com/NiceGenn/VisitkaStudent.git
cd VisitkaStudent

# локальный просмотр
python3 -m http.server 8000 --directory src
# → http://localhost:8000/
```

Открывать файлы напрямую (`file://`) тоже можно, но локальный сервер ближе
к тому, как сайт ведёт себя на хостинге.

## Структура репозитория

```
.
├── src/                  исходники сайта — единственное, что нужно править
│   ├── index.html        главная
│   ├── about.html        об администрации
│   ├── structure.html    структура
│   ├── leaders.html      визитница (генерируется, см. ниже)
│   ├── services.html     услуги
│   ├── news.html         новости
│   ├── schools.html      школы и сады
│   ├── docs.html         документы
│   ├── contacts.html     контакты
│   └── assets/
│       ├── css/style.css общие стили всех страниц
│       ├── js/script.js  аккордеон FAQ, плавная прокрутка, год в подвале
│       └── images/       фотографии
├── data/                 данные проекта
│   ├── rukovoditeli.json   руководители из телефонного справочника
│   ├── podrazdeleniya.json разделы и описания функций подразделений
│   └── palitry.json        цветовые схемы сайта
├── scripts/
│   ├── build.sh          сборка dist/ и архива релиза
│   ├── import_xlsx.py    справочник .xlsx → data/rukovoditeli.json
│   ├── gen_leaders.py    данные → src/leaders.html
│   ├── gen_palette.py    смена цветовой схемы
│   └── templates/        шаблоны и стили страницы «Визитница»
├── docs/                 документация проекта
│   ├── STRUCTURE.md      разбор страниц, стилей и известных пробелов
│   ├── COLORS.md         цветовые схемы и как их менять
│   └── DEPLOY.md         публикация: GitHub Pages, обычный хостинг, релизы
├── CLAUDE.md             память проекта для Claude Code
├── CHANGELOG.md          история версий
└── .github/workflows/    публикация на Pages и сборка релиза по тегу
```

Каталоги `dist/` и `release/` создаются сборкой и в репозиторий не попадают.

## Визитница

`src/leaders.html` — карточки подразделений: чем занимается подразделение,
кто им руководит, кабинет, телефон и почта. Страница **генерируется**, править
её руками бессмысленно — правки затрёт следующая сборка:

```bash
# 1. обновить данные из нового телефонного справочника
python3 scripts/import_xlsx.py ~/Downloads/spravochnik.xlsx

# 2. пересобрать страницу
python3 scripts/gen_leaders.py
```

Тексты о функциях подразделений живут в `data/podrazdeleniya.json`, вёрстка
карточки — в `scripts/templates/`. Для импорта нужен `openpyxl`
(`pip install openpyxl`); генератору хватает стандартной библиотеки.

## Цветовая схема

Все цвета заданы переменными в блоке `:root` файла `src/assets/css/style.css`.
В комплекте одиннадцать готовых схем — от исходного бордо до светлой шапки:

```bash
python3 scripts/gen_palette.py                 # список схем
python3 scripts/gen_palette.py navy --apply    # применить
python3 scripts/gen_leaders.py                 # пересобрать визитницу
```

Каждая схема проверена на контрастность по WCAG AA. Подробности —
в [docs/COLORS.md](docs/COLORS.md).

## Сборка релиза

```bash
./scripts/build.sh          # версия берётся из CHANGELOG.md
./scripts/build.sh 1.1.0    # или задаётся явно
```

Скрипт копирует `src/` в `dist/`, проверяет, что все внутренние ссылки и
ресурсы существуют, и кладёт `release/visitka-student-v<версия>.zip` —
готовый к заливке на любой хостинг архив.

Релиз на GitHub собирается автоматически при пуше тега:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

Подробности — в [docs/DEPLOY.md](docs/DEPLOY.md).

## Внесение изменений

- Правится только `src/`. `dist/` — результат сборки, его не коммитят.
- Общие стили живут в `src/assets/css/style.css`; стили, нужные одной
  странице, лежат в её теге `<style>` — так уже устроен проект.
- Перед коммитом полезно прогнать `./scripts/build.sh`: он не собирает
  ничего сложного, но ловит битые ссылки и отсутствующие картинки.

## Известные пробелы

Семь ссылок ведут на ещё не написанные страницы: `finance.html`,
`education.html`, `culture.html`, `gkh.html`, `economy.html`, `social.html`
(карточки отделов на главной) и `faq.html` (новости). Это исходное
состояние проекта, а не следствие переноса в репозиторий. Список и варианты
решения — в [docs/STRUCTURE.md](docs/STRUCTURE.md).
