# Исходный архив

Нетронутая копия того, с чего начинался проект: архив `obrazovanie-site.zip`
в том виде, в каком его прислали. Здесь ничего не правится — папка нужна
только для сверки «что было / что стало».

Здесь же `spravochnik.xlsx` — телефонный справочник органов власти округа,
из которого собраны данные визитницы и структуры. Его разбирает
`tools/import_xlsx.py` в `data/rukovoditeli.json`.

Рабочие исходники сайта лежат в `sources/`.

## Что здесь

```
about.html  contacts.html  docs.htm   index.html
news.html   schools.html   services.html  structure.html
css/style.css
js/script.js
images/blag-city.jpg  images/bashun.jpg
spravochnik.xlsx
```

Обратите внимание на `docs.htm`: именно так файл назывался изначально,
хотя все 27 ссылок на него вели на `docs.html`. Раздел «Документы» из-за
этого не открывался вообще.

## Чем отличается от `sources/`

| | Здесь | В `sources/` |
| --- | --- | --- |
| Страница документов | `docs.htm` | `docs.html` — переименована |
| Ресурсы | `css/`, `js/`, `images/` в корне | собраны в `assets/` |
| Пути в разметке | `href="css/style.css"` | `href="assets/css/style.css"` |
| Цвета | литералами: `#7a1a1a` | переменными: `var(--color-primary)` |
| Меню | восемь пунктов | добавлена «Визитница» |
| `contacts.html` | десять пометок `[citation:N]` в тексте | убраны |
| Страниц | восемь | девять — добавлена `leaders.html` |

Тексты, вёрстка и структура страниц не менялись. Обе фотографии совпадают
побайтово. Подробный разбор — в `docs/STRUCTURE.md`.
