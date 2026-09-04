#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка страницы «Структура» — sources/structure.html.

    python3 tools/gen_structure.py

Читает два файла:
    data/rukovoditeli.json    — руководители из телефонного справочника
                                (готовит tools/import_xlsx.py)
    data/podrazdeleniya.json  — разделы страницы и описания функций подразделений

Страница генерируется целиком, править её руками бессмысленно: правки
затрутся следующей сборкой. Тексты о функциях подразделений живут
в data/podrazdeleniya.json, персональные данные — в справочнике.
"""
import html
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sources' / 'structure.html'

# Подразделения-контейнеры: у них нет собственного руководителя, каждый
# входящий отдел показывается отдельной карточкой.
CONTEINERS = {
    'Структурные подразделения администрации Благовещенского муниципального округа',
    'Муниципальные казенные учреждения Благовещенского муниципального округа',
}

# Пометки из справочника, которые выносятся из ФИО в отдельную плашку.
MARKS = ('декрет', 'отпуск', 'совместительство')

ICONS = {
    'star': 'M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z',
    'gavel': 'M1 21h12v2H1zM5.24 8.07l2.83-2.83 14.14 14.14-2.83 2.83zM13.72 1l5.66 5.66-2.83 2.83-5.66-5.66zM4.11 10.6l5.66 5.66-2.83 2.83-5.66-5.66z',
    'shield': 'M12 1 3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11z',
    'check': 'M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z',
    'clipboard': 'M19 3h-4.18C14.4 1.84 13.3 1 12 1s-2.4.84-2.82 2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m-7 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2m2 14H7v-2h7zm3-4H7v-2h10zm0-4H7V7h10z',
    'users': 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3m-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3m0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5m8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5',
    'alert': 'M1 21h22L12 2zm12-3h-2v-2h2zm0-4h-2v-4h2z',
    'lock': 'M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2m-6 9a2 2 0 1 1 0-4 2 2 0 0 1 0 4m3.1-9H8.9V6a3.1 3.1 0 0 1 6.2 0z',
    'search': 'M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14',
    'road': 'M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1h12v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-8zM6.85 7h10.29l1.04 3H5.81zM6.5 16a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3m11 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3',
    'leaf': 'M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3 11 0 13-14 13-14-1 2-8 2.25-13 3.25S4 15 4 15c2-3.5 5.5-4.5 13-7',
    'heart': 'M12 21.35 10.55 20C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54z',
    'child': 'M12 2a2 2 0 1 1 0 4 2 2 0 0 1 0-4m5 5H7a1 1 0 0 0-1 1v6h2v8h8v-8h2V8a1 1 0 0 0-1-1',
    'cart': 'M7 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2M1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42a.25.25 0 0 1-.25-.25l.03-.12L8.1 13h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1 1 0 0 0 20 4H5.21l-.94-2zm16 16c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2',
    'map': 'M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5M15 19l-6-2.11V5l6 2.11z',
    'home': 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z',
    'building': 'M12 7V3H2v18h20V7zM6 19H4v-2h2zm0-4H4v-2h2zm0-4H4V9h2zm0-4H4V5h2zm4 12H8v-2h2zm0-4H8v-2h2zm0-4H8V9h2zm0-4H8V5h2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8zm-2-8h-2v2h2zm0 4h-2v2h2z',
    'chart': 'M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z',
    'flag': 'M14.4 6 14 4H5v17h2v-7h5.6l.4 2h7V6z',
    'coins': 'M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4',
    'book': 'M12 3C7.58 3 4 4.79 4 7c0 2.21 3.58 4 8 4s8-1.79 8-4-3.58-4-8-4m0 6c-3.87 0-6-1.5-6-2s2.13-2 6-2 6 1.5 6 2-2.13 2-6 2m-8 2.38c-.61.34-1.04.73-1.26 1.12C2.25 12.82 2 13.38 2 14c0 2.21 3.58 4 8 4s8-1.79 8-4c0-.62-.25-1.18-.74-1.5-.22-.39-.65-.78-1.26-1.12V14c0 1.1-2.69 2-6 2s-6-.9-6-2z',
    'calc': 'M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m-7 3h5v2h-5zM7 18H5v-2h2zm0-4H5v-2h2zm0-4H5V8h2zm5 8h-3v-2h3zm0-4h-3v-2h3zm7 4h-5v-2h5zm0-4h-5v-2h5z',
    'monitor': 'M20 3H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h6v2H8v2h8v-2h-2v-2h6a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m0 12H4V5h16z',
    'bolt': 'M11 21h-1l1-7H6.5c-.88 0-.33-.75-.31-.78C7.48 10.94 9.4 7.57 12.16 3h1l-1 7h4.51c.4 0 .62.19.4.66C12.97 17.55 11 21 11 21',
}


def esc(s):
    return html.escape(str(s or ''), quote=True)


def initials(fio):
    parts = [p for p in re.split(r'\s+', fio) if p and p[0].isalpha()]
    if not parts:
        return '—'
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else '')).upper()


def short_fio(fio):
    """«Иванов Иван Иванович» → «Иванов И. И.»"""
    parts = [p for p in re.split(r'\s+', fio) if p]
    if len(parts) < 2:
        return fio
    return parts[0] + ' ' + ' '.join(p[0].upper() + '.' for p in parts[1:3])


def split_mark(fio):
    """Отделяет пометку в скобках: «Иванова И. И. (декрет)» → ('Иванова И. И.', 'декрет')."""
    m = re.search(r'\(([^)]*)\)\s*$', fio)
    if m and any(k in m.group(1).lower() for k in MARKS):
        return fio[:m.start()].strip(), m.group(1).strip()
    return fio.strip(), ''


def tel_links(raw):
    """Телефоны из справочника → ссылки tel: для шестизначных городских номеров."""
    out = []
    for num in re.findall(r'\d[\d-]{4,}', raw or ''):
        digits = re.sub(r'\D', '', num)
        if len(digits) == 6:
            out.append('<a href="tel:+74162%s">%s</a>' % (digits, esc(num)))
        else:
            out.append('<span>%s</span>' % esc(num))
    return out


def slug(text, used):
    table = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
             'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
             'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
             'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
             'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}
    s = ''.join(table.get(c, c if c.isalnum() else '-') for c in text.lower())
    s = re.sub(r'-+', '-', s).strip('-')[:48] or 'card'
    base, n = s, 2
    while s in used:
        s, n = '%s-%d' % (base, n), n + 1
    used.add(s)
    return s


def build_cards(spr, meta):
    """Собирает список карточек: контейнеры разворачиваются в карточки отделов."""
    штат = {}
    отделы_группы = OrderedDict()
    for row in spr['численность']:
        штат[(row['подразделение'], row['отдел'])] = row['человек']
        отделы_группы.setdefault(row['подразделение'], []).append(row['отдел'])

    по_группам = OrderedDict()
    for p in spr['сотрудники']:
        по_группам.setdefault(p['подразделение'], []).append(p)

    описания = meta['подразделения']
    терр = meta['территориальные_администрации']

    cards, used = [], set()
    for группа, отделы in отделы_группы.items():
        люди = по_группам.get(группа, [])
        if группа in CONTEINERS:
            for отдел in отделы:
                if not отдел:
                    continue
                инфо = описания.get(отдел, терр)
                cards.append(OrderedDict(
                    id=slug(отдел, used), раздел=инфо['раздел'], название=отдел,
                    полное=отдел, надгруппа=группа, иконка=инфо['иконка'],
                    функции=инфо['функции'], направления=инфо['направления'],
                    штат=штат.get((группа, отдел), 0), отделов=0,
                    люди=[p for p in люди if p['отдел'] == отдел]))
        else:
            инфо = описания.get(группа)
            if инфо is None:
                raise SystemExit('Нет описания функций для «%s» — добавьте его '
                                 'в data/podrazdeleniya.json' % группа)
            cards.append(OrderedDict(
                id=slug(инфо.get('короткое', группа), used), раздел=инфо['раздел'],
                название=инфо.get('короткое', группа), полное=группа, надгруппа='',
                иконка=инфо['иконка'], функции=инфо['функции'],
                направления=инфо['направления'],
                штат=sum(штат.get((группа, о), 0) for о in отделы),
                отделов=len([о for о in отделы if о]),
                люди=list(люди), заимствовать=инфо.get('руководитель_из', '')))

    # Руководитель, числящийся в другом подразделении (начальник финуправления —
    # в блоке руководства администрации).
    по_фио = {(p['подразделение'], p['фио']): p for p in spr['сотрудники']}
    for c in cards:
        ссылка = c.get('заимствовать')
        if ссылка and '|' in ссылка:
            гр, фио = ссылка.split('|', 1)
            p = по_фио.get((гр.strip(), фио.strip()))
            if p:
                c['люди'] = [dict(p, отдел='', заместитель=False,
                                  заимствован=True)] + c['люди']
    return cards


def person_html(p, main=False):
    фио, пометка = split_mark(p['фио'])
    вакансия = фио.lower().startswith('вакан')
    cls = 'vz-person' + (' vz-person--main' if main else '') + (' vz-person--vac' if вакансия else '')
    ava = '<span class="vz-ava%s">%s</span>' % (
        ' vz-ava--vac' if вакансия else '', '—' if вакансия else esc(initials(фио)))

    контакты = []
    if p['кабинет']:
        каб = p['кабинет']
        контакты.append('<span class="vz-room">%s</span>' % esc(
            ('каб. ' + каб) if re.match(r'^\s*\d', каб) else каб))
    контакты += tel_links(p['телефон'])
    if p['почта'] and '@' in p['почта']:
        контакты.append('<a href="mailto:%s">%s</a>' % (esc(p['почта']), esc(p['почта'])))

    плашки = ''
    if пометка:
        плашки += '<span class="vz-badge">%s</span>' % esc(пометка)
    if p.get('заимствован'):
        плашки += '<span class="vz-badge vz-badge--ref">по должности</span>'

    отдел = ''
    if p['отдел'] and not main:
        отдел = '<div class="vz-otdel">%s</div>' % esc(p['отдел'])

    return (
        '<div class="%s">%s<div class="vz-person-body">%s'
        '<div class="vz-fio">%s%s</div>'
        '<div class="vz-post">%s</div>'
        '<div class="vz-contacts">%s</div>'
        '</div></div>' % (
            cls, ava, отдел,
            'Вакансия' if вакансия else esc(фио), плашки,
            esc(p['должность']),
            ''.join(контакты) or '<span class="vz-none">контакты не указаны</span>'))


def card_html(c):
    руководящие = [p for p in c['люди'] if p.get('руководитель')]
    рядовые = [p for p in c['люди'] if not p.get('руководитель')]

    главные, замы, прочие = [], [], []
    for p in руководящие:
        if p['отдел']:
            прочие.append(p)
        elif p['заместитель']:
            замы.append(p)
        elif re.search(r'отдел|сектор', p['должность'], re.I):
            # «Начальник отдела ...» без заполненной колонки «Отдел».
            прочие.append(p)
        else:
            главные.append(p)
    if not главные and замы:
        главные, замы = замы[:1], замы[1:]
    if not главные and прочие:
        главные, прочие = прочие[:1], прочие[1:]
    отделы = прочие

    блоки = ''
    if главные:
        блоки += '<h5 class="vz-h5">%s</h5>' % ('Руководство' if len(главные) > 1 else 'Руководитель')
        блоки += ''.join(person_html(p, main=True) for p in главные)
    if замы:
        блоки += '<h5 class="vz-h5">Заместители</h5>' + ''.join(person_html(p) for p in замы)
    if отделы:
        блоки += '<h5 class="vz-h5">Руководители отделов</h5>' + ''.join(person_html(p) for p in отделы)
    if рядовые:
        блоки += '<h5 class="vz-h5">Сотрудники</h5>' + ''.join(person_html(p) for p in рядовые)
    if not блоки:
        блоки = '<p class="vz-none">В справочнике состав не указан</p>'

    мета = ['%d %s' % (c['штат'], plural(c['штат'], 'сотрудник', 'сотрудника', 'сотрудников'))]
    if c['отделов']:
        мета.append('%d %s' % (c['отделов'], plural(c['отделов'], 'отдел', 'отдела', 'отделов')))
    if c['надгруппа']:
        мета.append('в составе администрации')

    поиск = ' '.join([c['название'], c['полное']] +
                     [p['фио'] + ' ' + p['должность'] + ' ' + p['отдел'] for p in c['люди']]).lower()
    людей = len(c['люди'])

    return (
        '\n        <article class="vz-card" id="%s" data-section="%s" data-search="%s">\n'
        '          <button type="button" class="vz-card-head" aria-expanded="false">\n'
        '            <span class="vz-icon"><svg viewBox="0 0 24 24"><path d="%s"/></svg></span>\n'
        '            <span class="vz-card-title">\n'
        '              <span class="vz-h4">%s</span>\n'
        '              <span class="vz-metaline">%s</span>\n'
        '            </span>\n'
        '            <span class="vz-toggle" aria-hidden="true"></span>\n'
        '          </button>\n'
        '          <div class="vz-func">\n'
        '            <p>%s</p>\n'
        '            <ul class="vz-tags">%s</ul>\n'
        '          </div>\n'
        '          <div class="vz-people" hidden>%s\n'
        '            <p class="vz-count">Всего в справочнике: %d %s</p>\n'
        '          </div>\n'
        '        </article>\n' % (
            c['id'], c['раздел'], esc(поиск), ICONS[c['иконка']],
            esc(c['название']), esc(' · '.join(мета)), esc(c['функции']),
            ''.join('<li>%s</li>' % esc(t) for t in c['направления']), блоки,
            людей, plural(людей, 'человек', 'человека', 'человек')))


def plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


def main():
    spr = json.loads((ROOT / 'data' / 'rukovoditeli.json').read_text(encoding='utf-8'))
    meta = json.loads((ROOT / 'data' / 'podrazdeleniya.json').read_text(encoding='utf-8'))
    cards = build_cards(spr, meta)

    всего_людей = sum(len(c['люди']) for c in cards)
    разделы = [r for r in meta['разделы'] if any(c['раздел'] == r['id'] for c in cards)]

    фильтры = '<button type="button" class="vz-chip is-active" data-filter="all">Все</button>' + ''.join(
        '<button type="button" class="vz-chip" data-filter="%s">%s</button>' % (esc(r['id']), esc(r['название']))
        for r in разделы)

    секции = ''
    for r in разделы:
        свои = [c for c in cards if c['раздел'] == r['id']]
        секции += (
            '\n      <section class="vz-section" data-section="%s">\n'
            '        <h3 class="vz-section-title">%s <span>%d</span></h3>\n'
            '        <p class="vz-section-sub">%s</p>\n'
            '        <div class="vz-grid">%s        </div>\n'
            '      </section>\n' % (
                esc(r['id']), esc(r['название']), len(свои), esc(r['описание']),
                ''.join(card_html(c) for c in свои)))

    шапка = (ROOT / 'tools' / 'templates' / 'chrome-head.html').read_text(encoding='utf-8')
    подвал = (ROOT / 'tools' / 'templates' / 'chrome-foot.html').read_text(encoding='utf-8')
    стили = (ROOT / 'tools' / 'templates' / 'leaders.css').read_text(encoding='utf-8')

    шапка = (шапка.replace('{{ЗАГОЛОВОК}}', 'Структура')
                  .replace('{{ОПИСАНИЕ}}', 'Структура администрации Благовещенского '
                           'муниципального округа: подразделения, чем каждое занимается, '
                           'руководители и сотрудники с телефонами.'))
    страница = шапка.replace('{{СТИЛИ}}', стили).replace('{{СОДЕРЖИМОЕ}}', (
        '        <h2 class="section-title"><span class="accent-line"></span>Структура администрации</h2>\n'
        '        <p class="section-subtitle">Подразделения, управления и учреждения Благовещенского '
        'муниципального округа. Нажмите на подразделение, чтобы увидеть руководителя и сотрудников</p>\n'
        '\n'
        '        <div class="vz-toolbar">\n'
        '          <div class="vz-searchbox">\n'
        '            <svg viewBox="0 0 24 24"><path d="%s"/></svg>\n'
        '            <input type="search" id="vz-search" placeholder="Фамилия, должность или подразделение" '
        'aria-label="Поиск по визитнице" autocomplete="off" />\n'
        '          </div>\n'
        '          <div class="vz-chips">%s</div>\n'
        '        </div>\n'
        '        <p class="vz-status" id="vz-status">%d %s · %d %s</p>\n'
        '%s'
        '        <p class="vz-empty" id="vz-empty" hidden>Ничего не найдено. '
        'Попробуйте другой запрос или снимите фильтр по разделу.</p>\n'
        '        <p class="vz-note">Сведения приведены по телефонному справочнику '
        'органов власти округа (%s). Описания функций подготовлены по типовым положениям '
        'о подразделениях и подлежат уточнению по действующим положениям.</p>\n' % (
            ICONS['search'], фильтры,
            len(cards), plural(len(cards), 'подразделение', 'подразделения', 'подразделений'),
            всего_людей, plural(всего_людей, 'сотрудник', 'сотрудника', 'сотрудников'),
            секции, esc(spr['актуально'].rstrip('.')))))

    OUT.write_text(страница + подвал, encoding='utf-8')
    print('Подразделений: %d' % len(cards))
    print('Сотрудников:   %d' % всего_людей)
    print('Записано:      %s' % OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
