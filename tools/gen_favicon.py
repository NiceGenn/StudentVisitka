#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка фавиконки из герба округа.

    python3 tools/gen_favicon.py

Кладёт в sources/assets/:
    favicon.svg          — упрощённый герб, векторный
    favicon-16.png       — без звёзд: на 16 пикселях они превращаются в кашу
    favicon-32.png
    favicon-48.png
    favicon.ico          — те же три размера одним файлом, для старых браузеров
    apple-touch-icon.png — 180×180, настоящий герб на светлой плашке

Почему не сам герб. Герб вместе с короной вытянут (316×500), в квадрат
фавиконки он влезает полоской в треть ширины, а на 16 пикселях от него
остаётся серое пятно. Поэтому для иконки герб пересобран: щит раздвинут
до почти квадратного, корона сжата в пять зубцов над ним, фазаны и
ветви убраны — на таком размере их всё равно не видно. Цвета взяты
пипеткой из docs/original/gerb-bmo.png, форма щита повторяет исходную.

Растр рендерится Chromium через Playwright — тем же движком, что покажет
иконку в браузере, поэтому SVG и PNG совпадают пиксель в пиксель.
"""
import json
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'sources' / 'assets'
ГЕРБ = ROOT / 'docs' / 'original' / 'gerb-bmo.png'

# Цвета сняты пипеткой с герба.
СИНИЙ = '#008ed5'
ЗЕЛЁНЫЙ = '#00b136'
ЗОЛОТО = '#ffcd00'
БЕЛЫЙ = '#ffffff'
КОНТУР = '#271c22'

# Щит: прямые плечи, книзу сходится к острию. Пропорции раздвинуты
# до 50×46 против исходных 316×370 — иначе в квадрате остаются поля.
ЩИТ = 'M7 15 H57 V37 C57 48.5 48 56.5 32 61 C16 56.5 7 48.5 7 37 Z'

# Корона: пять зубцов на широком обруче, как в гербе, но без огранки.
КОРОНА = ('M11 15 L12.6 4.5 L19.5 10 L26 2.5 L32 9 L38 2.5 L44.5 10 '
          'L51.4 4.5 L53 15 Z')

# Белая волнистая перевязь между синим и зелёным полем.
ВОЛНА = ('M4 30.5 C12 26.5 20 33 32 31 C44 29 52 34.5 60 30.5 '
         'L60 36.5 C52 40.5 44 35 32 37 C20 39 12 33.5 4 36.5 Z')


def звезда(cx, cy, r, лучей=8):
    """Восьмиконечная звезда — такая же, как в верхнем поле герба."""
    точки = []
    for i in range(лучей * 2):
        радиус = r if i % 2 == 0 else r * 0.42
        угол = math.pi / 2 + i * math.pi / лучей
        точки.append('%.2f %.2f' % (cx + радиус * math.cos(угол),
                                    cy - радиус * math.sin(угол)))
    return 'M' + ' L'.join(точки) + ' Z'


def собрать_svg():
    звёзды = ''.join('<path d="%s" />' % звезда(x, 22.5, 5.2)
                     for x in (17.5, 32, 46.5))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
        'role="img" aria-label="Герб Благовещенского муниципального округа">\n'
        '  <title>Герб Благовещенского муниципального округа</title>\n'
        '  <defs><clipPath id="shield"><path d="%s" /></clipPath></defs>\n'
        '  <path class="detail" d="%s" fill="%s" stroke="%s" '
        'stroke-width="1.6" stroke-linejoin="round" />\n'
        '  <g clip-path="url(#shield)">\n'
        '    <rect x="0" y="0" width="64" height="64" fill="%s" />\n'
        '    <rect x="0" y="33" width="64" height="31" fill="%s" />\n'
        '    <path d="%s" fill="%s" />\n'
        '    <g class="detail" fill="%s" stroke="%s" stroke-width="0.8" '
        'stroke-linejoin="round">%s</g>\n'
        '  </g>\n'
        '  <path d="%s" fill="none" stroke="%s" stroke-width="1.8" '
        'stroke-linejoin="round" />\n'
        '</svg>\n' % (ЩИТ, КОРОНА, ЗОЛОТО, КОНТУР, СИНИЙ, ЗЕЛЁНЫЙ,
                      ВОЛНА, БЕЛЫЙ, ЗОЛОТО, КОНТУР, звёзды, ЩИТ, КОНТУР))


СКРИПТ_РЕНДЕРА = r'''
import pw from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pw;
const задания = JSON.parse(process.argv[2]);
const b = await chromium.launch({ executablePath: process.argv[3] });
for (const з of задания) {
  const p = await b.newPage({ viewport: { width: з.размер, height: з.размер },
                              deviceScaleFactor: 1 });
  await p.goto('data:text/html;charset=utf-8,' + encodeURIComponent(з.html));
  await p.waitForTimeout(120);
  await p.screenshot({ path: з.файл, omitBackground: true });
  await p.close();
}
await b.close();
'''


def страница(svg, размер, детали=True):
    """SVG в пустой странице нужного размера, фон прозрачный.

    На 16 пикселях убираем корону и звёзды и обрезаем поле по самому щиту:
    корона съедает пятую часть высоты, а остаётся от неё один жёлтый штрих.
    Щит во всё поле читается заметно лучше.
    """
    скрыть = ''
    if not детали:
        скрыть = '.detail{display:none}'
        svg = svg.replace('viewBox="0 0 64 64"', 'viewBox="6 14 52 48"')
    return ('<style>html,body{margin:0;padding:0;background:transparent}'
            'svg{display:block;width:%dpx;height:%dpx}%s</style>%s'
            % (размер, размер, скрыть, svg))


def найти_chromium():
    подходящие = sorted(Path('/opt/pw-browsers').glob('chromium*/chrome-linux/chrome'))
    if подходящие:
        return str(подходящие[0])
    raise SystemExit('Chromium не найден в /opt/pw-browsers')


def main():
    svg = собрать_svg()
    (ASSETS / 'favicon.svg').write_text(svg, encoding='utf-8')

    # Крупные размеры со звёздами, 16 пикселей — без них.
    задания = []
    for размер in (16, 32, 48):
        задания.append(dict(размер=размер,
                            файл=str(ASSETS / ('favicon-%d.png' % размер)),
                            html=страница(svg, размер, детали=размер >= 32)))

    with tempfile.TemporaryDirectory() as tmp:
        скрипт = Path(tmp) / 'render.mjs'
        скрипт.write_text(СКРИПТ_РЕНДЕРА, encoding='utf-8')
        subprocess.run(['node', str(скрипт),
                        json.dumps(задания, ensure_ascii=False), найти_chromium()],
                       check=True)

    from PIL import Image
    слои = [Image.open(ASSETS / ('favicon-%d.png' % р)).convert('RGBA')
            for р in (16, 32, 48)]
    слои[2].save(ASSETS / 'favicon.ico', format='ICO',
                 sizes=[(16, 16), (32, 32), (48, 48)])

    # Иконка для домашнего экрана — места хватает, берём настоящий герб.
    герб = Image.open(ГЕРБ).convert('RGBA')
    поле = Image.new('RGBA', (180, 180), (255, 255, 255, 255))
    вписан = герб.crop(герб.getbbox())
    k = 156 / max(вписан.size)
    вписан = вписан.resize((max(1, round(вписан.width * k)),
                            max(1, round(вписан.height * k))), Image.LANCZOS)
    поле.paste(вписан, ((180 - вписан.width) // 2, (180 - вписан.height) // 2), вписан)
    поле.save(ASSETS / 'apple-touch-icon.png', optimize=True)

    for имя in ('favicon.svg', 'favicon.ico', 'favicon-16.png',
                'favicon-32.png', 'favicon-48.png', 'apple-touch-icon.png'):
        f = ASSETS / имя
        print('%-22s %6d Б' % (имя, f.stat().st_size))


if __name__ == '__main__':
    main()
