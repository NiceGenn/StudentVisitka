#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Временный переключатель цветовых схем на сайте.

    python3 tools/gen_themes.py         поставить переключатель
    python3 tools/gen_themes.py --off   убрать его без следа

Панель нужна, чтобы выбрать схему на живом сайте, а не по скриншотам.
Как только схема выбрана — переключатель убирается: посетителю сайта
органа власти выбирать палитру незачем.

Ставит два файла и подключает их во всех страницах:
    sources/assets/css/themes.css  — все схемы из data/palitry.json
    sources/assets/js/themes.js    — панель выбора

Снятие (--off) удаляет файлы и все подключения, ничего больше не трогая.
"""
import json
import re
import sys
from pathlib import Path

import gen_palette as пал

ROOT = Path(__file__).resolve().parent.parent
СТРАНИЦЫ = sorted((ROOT / 'sources').glob('*.html'))
ШАБЛОНЫ = [ROOT / 'tools' / 'templates' / 'chrome-head.html',
           ROOT / 'tools' / 'templates' / 'chrome-foot.html']

CSS = ROOT / 'sources' / 'assets' / 'css' / 'themes.css'
JS = ROOT / 'sources' / 'assets' / 'js' / 'themes.js'

ССЫЛКА = '    <link rel="stylesheet" href="assets/css/themes.css" />\n'
СКРИПТ = '    <script src="assets/js/themes.js" defer></script>\n'

ПАНЕЛЬ_CSS = '''
/* ==========================================
   ПАНЕЛЬ ВЫБОРА СХЕМЫ — ВРЕМЕННАЯ
   Ставится и снимается: python3 tools/gen_themes.py [--off]
   ========================================== */

.th-panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 900;
  font-family: 'Inter', Arial, sans-serif;
}

.th-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font: 600 14px/1 'Inter', Arial, sans-serif;
  color: #ffffff;
  background: var(--color-primary-dark);
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.th-toggle::before {
  content: '';
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--color-accent);
  border: 2px solid #ffffff;
}

.th-list {
  position: absolute;
  right: 0;
  bottom: 56px;
  width: 260px;
  max-height: 70vh;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid var(--tone-line-2);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 8px;
}

.th-list p {
  font-size: 12px;
  color: var(--tone-muted-2);
  padding: 6px 10px 10px;
  margin: 0;
  border-bottom: 1px solid var(--tone-line-5);
}

.th-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  text-align: left;
  font: 500 14px/1.3 'Inter', Arial, sans-serif;
  color: #1a1a1a;
  background: none;
  border: none;
  border-radius: 6px;
  padding: 9px 10px;
  cursor: pointer;
}

.th-item:hover {
  background: var(--tone-surface-2);
}

.th-item.is-on {
  background: var(--tone-line-4);
  font-weight: 600;
}

.th-dots {
  display: inline-flex;
  flex-shrink: 0;
}

.th-dots i {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1.5px solid #ffffff;
  margin-left: -5px;
}

.th-dots i:first-child {
  margin-left: 0;
}

@media (max-width: 768px) {
  .th-panel {
    right: 12px;
    bottom: 12px;
  }

  .th-list {
    width: calc(100vw - 40px);
  }
}
'''

ПАНЕЛЬ_JS = '''// ============================================================
// ПАНЕЛЬ ВЫБОРА ЦВЕТОВОЙ СХЕМЫ — ВРЕМЕННАЯ
// Ставится и снимается: python3 tools/gen_themes.py [--off]
// ============================================================

(function () {
  const схемы = %s;

  const панель = document.createElement('div');
  панель.className = 'th-panel';
  панель.innerHTML =
    '<button type="button" class="th-toggle">Цветовая схема</button>' +
    '<div class="th-list" hidden><p>Выберите схему — сайт сразу перекрасится. ' +
    'Панель временная, после выбора её уберут.</p>' +
    схемы
      .map(function (с) {
        return (
          '<button type="button" class="th-item" data-id="' + с.id + '">' +
          '<span class="th-dots">' +
          '<i style="background:' + с.осн + '"></i>' +
          '<i style="background:' + с.тёмный + '"></i>' +
          '<i style="background:' + с.акцент + '"></i>' +
          '</span>' + с.имя + '</button>'
        );
      })
      .join('') +
    '</div>';
  document.body.appendChild(панель);

  const кнопка = панель.querySelector('.th-toggle');
  const список = панель.querySelector('.th-list');
  const пункты = панель.querySelectorAll('.th-item');

  кнопка.addEventListener('click', function () {
    список.hidden = !список.hidden;
  });

  function применить(ид) {
    if (ид === 'steel') document.documentElement.removeAttribute('data-palette');
    else document.documentElement.dataset.palette = ид;
    пункты.forEach(function (п) {
      п.classList.toggle('is-on', п.dataset.id === ид);
    });
    try {
      localStorage.setItem('схема', ид);
    } catch (e) {
      // Приватный режим — выбор просто не запомнится.
    }
  }

  пункты.forEach(function (п) {
    п.addEventListener('click', function () {
      применить(п.dataset.id);
    });
  });

  let сохранённая = 'steel';
  try {
    сохранённая = localStorage.getItem('схема') || 'steel';
  } catch (e) {
    // Ничего: останется схема по умолчанию.
  }
  применить(сохранённая);
})();
'''


def собрать():
    данные = json.loads((ROOT / 'data' / 'palitry.json').read_text(encoding='utf-8'))
    схемы = данные['схемы']

    куски = ['/* Все схемы из data/palitry.json. Файл временный. */\n']
    for c in схемы:
        блок = пал.блок_root(данные, c)
        тело = блок.split(':root {', 1)[1]
        куски.append('/* %s — %s */\n:root[data-palette="%s"] {%s'
                     % (c['имя'], c['описание'], c['id'], тело))
    CSS.write_text('\n'.join(куски) + ПАНЕЛЬ_CSS, encoding='utf-8')

    краткие = [{'id': c['id'], 'имя': c['имя'], 'осн': c['основной'],
                'тёмный': c['тёмный'], 'акцент': c['акцент']} for c in схемы]
    JS.write_text(ПАНЕЛЬ_JS % json.dumps(краткие, ensure_ascii=False, indent=4),
                  encoding='utf-8')

    подключено = 0
    for f in СТРАНИЦЫ + ШАБЛОНЫ:
        s = f.read_text(encoding='utf-8')
        if 'themes.css' in s or 'themes.js' in s:
            continue
        if '<link rel="stylesheet" href="assets/css/style.css" />\n' in s:
            s = s.replace('<link rel="stylesheet" href="assets/css/style.css" />\n',
                          '<link rel="stylesheet" href="assets/css/style.css" />\n' + ССЫЛКА, 1)
            подключено += 1
        if '</body>' in s:
            s = s.replace('  </body>', СКРИПТ + '  </body>', 1)
        f.write_text(s, encoding='utf-8')
    print('Схем в панели: %d' % len(схемы))
    print('Страниц подключено: %d' % подключено)
    print('Дальше: python3 tools/gen_structure.py && ./tools/build.sh')


def убрать():
    for f in (CSS, JS):
        if f.exists():
            f.unlink()
            print('удалён: %s' % f.relative_to(ROOT))
    снято = 0
    for f in СТРАНИЦЫ + ШАБЛОНЫ:
        s = было = f.read_text(encoding='utf-8')
        s = re.sub(r'^.*themes\.(css|js).*\n', '', s, flags=re.M)
        if s != было:
            f.write_text(s, encoding='utf-8')
            снято += 1
    print('Страниц очищено: %d' % снято)
    print('Дальше: python3 tools/gen_structure.py && ./tools/build.sh')


if __name__ == '__main__':
    убрать() if '--off' in sys.argv else собрать()
