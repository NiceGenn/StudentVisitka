#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Цветовая схема сайта.

    python3 scripts/gen_palette.py                 список схем
    python3 scripts/gen_palette.py navy            показать блок :root
    python3 scripts/gen_palette.py navy --apply    применить к style.css

Схемы описаны в data/palitry.json. Фирменные цвета там заданы явно, тёплые
оттенки фонов и рамок пересчитываются в тон схемы: светлота и насыщенность
сохраняются, меняется только тон. Поэтому кремовая плашка объявления в синей
схеме становится холодно-голубой, а не остаётся жёлтым пятном.

Схема, меняющая не только цвета (например, светлая шапка), дополняется
блоком правил из поля «дополнительно».
"""
import colorsys
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ДАННЫЕ = ROOT / 'data' / 'palitry.json'
СТИЛИ = ROOT / 'src' / 'assets' / 'css' / 'style.css'

НАЧАЛО = '/* НАЧАЛО ДОПОЛНЕНИЙ СХЕМЫ — правится генератором */'
КОНЕЦ = '/* КОНЕЦ ДОПОЛНЕНИЙ СХЕМЫ */'


def перекрасить(цвет, тон):
    """Оттенок сохраняет светлоту и насыщенность, но получает тон схемы."""
    r, g, b = (int(цвет[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(тон / 360.0, l, s)
    return '#%02x%02x%02x' % tuple(round(c * 255) for c in (r, g, b))


def блок_root(данные, схема):
    строки = ['/* ==========================================',
              '   ЦВЕТОВАЯ СХЕМА: %s' % схема['имя'],
              '   %s' % схема['описание'],
              '',
              '   Все цвета сайта заданы здесь. Сменить схему:',
              '   python3 scripts/gen_palette.py <id> --apply',
              '   Список схем — в data/palitry.json и docs/COLORS.md.',
              '   ========================================== */',
              '', ':root {', '  /* фирменные цвета */']
    for имя, поле in данные['роли'].items():
        строки.append('  --%s: %s;' % (имя, схема[поле]))

    подписи = {'surface': 'фоны и заливки', 'line': 'рамки и разделители',
               'muted': 'приглушённый текст', 'deep': 'тёмные оттенки'}
    for группа, подпись in подписи.items():
        свои = [(и, ц) for и, ц in данные['базовые_оттенки'].items()
                if и.split('-')[1] == группа]
        if not свои:
            continue
        строки.append('')
        строки.append('  /* %s */' % подпись)
        # У исходной схемы оттенки берутся как есть: их тона слегка разнятся,
        # и пересчёт по одному тону заметно сдвинул бы вид сайта.
        if схема.get('исходные_оттенки'):
            строки += ['  --%s: %s;' % (и, ц) for и, ц in свои]
        else:
            строки += ['  --%s: %s;' % (и, перекрасить(ц, схема['тон'])) for и, ц in свои]
    строки += ['}', '']
    return '\n'.join(строки)


def дополнения(схема):
    правила = схема.get('дополнительно', '').strip()
    if not правила:
        return ''
    return '\n%s\n%s\n%s\n' % (НАЧАЛО, правила, КОНЕЦ)


def применить(текст, схема, root):
    # Старый блок :root вместе с шапкой-комментарием заменяем целиком.
    текст = re.sub(r'/\* =+\n   ЦВЕТОВАЯ СХЕМА.*?\n\}\n', root, текст, count=1, flags=re.S)
    текст = re.sub(re.escape(НАЧАЛО) + r'.*?' + re.escape(КОНЕЦ) + r'\n', '', текст, flags=re.S)
    доп = дополнения(схема)
    if доп:
        текст = текст.replace('\n}\n\n* {', '\n}\n' + доп + '\n* {', 1)
    return текст


def main():
    данные = json.loads(ДАННЫЕ.read_text(encoding='utf-8'))
    схемы = {c['id']: c for c in данные['схемы']}

    if len(sys.argv) < 2:
        print('Доступные схемы:\n')
        for c in данные['схемы']:
            print('  %-10s %-22s %s' % (c['id'], c['имя'], c['описание']))
        print('\nПоказать блок:   python3 scripts/gen_palette.py <id>')
        print('Применить:       python3 scripts/gen_palette.py <id> --apply')
        return

    ид = sys.argv[1]
    if ид not in схемы:
        sys.exit('Нет схемы «%s». Доступные: %s' % (ид, ', '.join(схемы)))
    схема = схемы[ид]
    root = блок_root(данные, схема)

    if '--apply' not in sys.argv:
        print(root + дополнения(схема))
        return

    текст = СТИЛИ.read_text(encoding='utf-8')
    новый = применить(текст, схема, root)
    if новый == текст:
        sys.exit('Не нашёл блок :root в style.css — проверьте файл вручную.')
    СТИЛИ.write_text(новый, encoding='utf-8')
    print('Схема «%s» применена к %s' % (схема['имя'], СТИЛИ.relative_to(ROOT)))
    print('Дальше: python3 scripts/gen_leaders.py && ./scripts/build.sh')


if __name__ == '__main__':
    main()
