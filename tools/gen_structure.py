#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка страницы «Структура» — sources/structure.html.

    python3 tools/gen_structure.py

Читает те же данные, что и визитница:
    data/rukovoditeli.json    — руководители из телефонного справочника
    data/podrazdeleniya.json  — разделы и описания функций подразделений

Страница показывает те же подразделения, что и «Визитница», но списком:
название, чем занимается, руководитель и телефон. Разница в подаче —
в визитнице карточки с полным составом руководства, здесь компактный
перечень для общего представления о структуре округа.

Править руками бессмысленно: правки затрутся следующей сборкой.
"""
import html
import json
import re
from pathlib import Path

import gen_leaders as вз

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sources' / 'structure.html'


def esc(s):
    return html.escape(str(s or ''), quote=True)


def строка_человека(p):
    """Руководитель подразделения: ФИО, должность и телефон одной строкой."""
    фио, пометка = вз.split_mark(p['фио'])
    if фио.lower().startswith('вакан'):
        return '<div class="org-person org-person--vac">Руководитель: вакансия</div>'
    плашка = ' <span class="org-mark">%s</span>' % esc(пометка) if пометка else ''
    return ('<div class="org-person"><strong>%s</strong>%s'
            '<span class="org-post">%s</span></div>' % (esc(фио), плашка, esc(p['должность'])))


def карточка(c):
    руководители = [p for p in c['люди'] if not p['отдел'] and not p['заместитель']]
    if not руководители:
        руководители = [p for p in c['люди'] if not p['отдел']]
    if not руководители:
        руководители = c['люди'][:1]

    телефоны = []
    for p in руководители[:1]:
        телефоны = вз.tel_links(p['телефон'])

    части = ['<div class="org-name">%s</div>' % esc(c['название']),
             '<div class="org-desc">%s</div>' % esc(c['функции'])]
    части += [строка_человека(p) for p in руководители[:1]]
    if телефоны:
        части.append('<div class="org-phone"><strong>Телефон:</strong> %s</div>'
                     % ' '.join(телефоны))
    мета = '%d %s' % (c['штат'], вз.plural(c['штат'], 'сотрудник', 'сотрудника', 'сотрудников'))
    if c['отделов']:
        мета += ' · %d %s' % (c['отделов'], вз.plural(c['отделов'], 'отдел', 'отдела', 'отделов'))
    части.append('<div class="org-meta">%s</div>' % esc(мета))
    return '                            <div class="org-item">\n%s\n                            </div>\n' % (
        '\n'.join('                                ' + ч for ч in части))


def блок_руководства(spr):
    """Глава округа и заместители — отдельным уровнем, как первое лицо структуры."""
    свои = [p for p in spr['руководители']
            if p['подразделение'] == 'Глава округа и руководство администрации']
    строки = []
    for p in свои:
        фио, пометка = вз.split_mark(p['фио'])
        вакансия = фио.lower().startswith('вакан')
        телефоны = вз.tel_links(p['телефон'])
        части = ['<div class="org-name">%s%s</div>' % (
            'Вакансия' if вакансия else esc(фио),
            ' <span class="org-mark">%s</span>' % esc(пометка) if пометка else ''),
            '<div class="org-desc">%s</div>' % esc(p['должность'])]
        if p['кабинет']:
            части.append('<div class="org-phone"><strong>Кабинет:</strong> %s</div>' % esc(p['кабинет']))
        if телефоны:
            части.append('<div class="org-phone"><strong>Телефон:</strong> %s</div>' % ' '.join(телефоны))
        строки.append('                            <div class="org-item">\n%s\n                            </div>\n'
                      % '\n'.join('                                ' + ч for ч in части))
    return строки


def уровень(заголовок, подпись, карточки):
    return (
        '                <div class="org-level">\n'
        '                    <div class="org-level-header">%s<span class="badge-count">%d</span></div>\n'
        '                    <div class="org-level-body">\n'
        '                        <p class="org-level-note">%s</p>\n'
        '                        <div class="org-grid">\n%s'
        '                        </div>\n'
        '                    </div>\n'
        '                </div>\n' % (esc(заголовок), len(карточки), esc(подпись), ''.join(карточки)))


def main():
    spr = json.loads((ROOT / 'data' / 'rukovoditeli.json').read_text(encoding='utf-8'))
    meta = json.loads((ROOT / 'data' / 'podrazdeleniya.json').read_text(encoding='utf-8'))
    cards = вз.build_cards(spr, meta)

    руководство = блок_руководства(spr)
    уровни = [уровень('Руководство округа', 'Глава округа и заместители главы администрации', руководство)]

    for r in meta['разделы']:
        свои = [c for c in cards if c['раздел'] == r['id']]
        # Руководство округа уже показано отдельным уровнем.
        свои = [c for c in свои if c['название'] != 'Глава округа и заместители']
        if not свои:
            continue
        название = r['название']
        описание = r['описание']
        if r['id'] == 'vlast':
            # Глава и заместители показаны выше отдельным уровнем.
            название = 'Органы власти округа'
            описание = 'Представительный орган, контрольные и избирательные органы'
        уровни.append(уровень(название, описание, [карточка(c) for c in свои]))

    всего = sum(len([c for c in cards if c['раздел'] == r['id']]) for r in meta['разделы'])

    шапка = (ROOT / 'tools' / 'templates' / 'chrome-head.html').read_text(encoding='utf-8')
    подвал = (ROOT / 'tools' / 'templates' / 'chrome-foot.html').read_text(encoding='utf-8')
    стили = (ROOT / 'tools' / 'templates' / 'structure.css').read_text(encoding='utf-8')

    шапка = (шапка.replace('{{ЗАГОЛОВОК}}', 'Структура')
             .replace('{{ОПИСАНИЕ}}', 'Структура администрации Благовещенского муниципального '
                      'округа: подразделения, управления, учреждения и территориальные '
                      'администрации с руководителями и телефонами.'))

    содержимое = (
        '        <h2 class="section-title"><span class="accent-line"></span>Структура администрации</h2>\n'
        '        <p class="section-subtitle">Подразделения, управления, учреждения и территориальные '
        'администрации Благовещенского муниципального округа — %d %s с руководителями и телефонами</p>\n'
        '\n        <div class="org-chart">\n%s        </div>\n'
        '\n        <p class="org-note">Сведения приведены по телефонному справочнику органов власти '
        'округа (%s). Подробные карточки подразделений с полным составом руководства — '
        'в разделе <a href="leaders.html">«Визитница»</a>.</p>\n' % (
            всего, вз.plural(всего, 'подразделение', 'подразделения', 'подразделений'),
            ''.join(уровни), esc(spr['актуально'].rstrip('.'))))

    OUT.write_text(шапка.replace('{{СТИЛИ}}', стили).replace('{{СОДЕРЖИМОЕ}}', содержимое) + подвал,
                   encoding='utf-8')
    print('Уровней:        %d' % len(уровни))
    print('Подразделений:  %d' % всего)
    print('Записано:       %s' % OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
