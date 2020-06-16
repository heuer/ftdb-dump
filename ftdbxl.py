#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Converts the JSON dump into XLSX files.
#
# Written in 2020 by Lars Heuer
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
#
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#
import io
from operator import itemgetter
import os
import json
import xlsxwriter


def create_parts_xlfile(db):
    """\
    Creates the parts overview Excel file.

    :param db: dict with at least a "parts" key which returns an iterable of dicts.
    """
    buff = io.BytesIO()
    wb = xlsxwriter.Workbook(buff)
    sheet = wb.add_worksheet('Einzelteile')
    bold_style = wb.add_format({'bold': True})
    text_style = wb.add_format({'align': 'top', 'font_color': 'black'})
    write_parts(sheet, db['parts'].values(), start_row=0, bold_style=bold_style,
                text_style=text_style)
    wb.close()
    with open('excel/einzelteile.xlsx', 'wb') as f:
        f.write(buff.getvalue())


def write_parts(sheet, parts, start_row, bold_style, text_style=None):
    """\
    Writes parts specification.

    :param sheet: Worksheet
    :param parts: The parts to write (iterable of dicts).
    :param start_row: Start row for the header.
    :param bold_style: Format of the header row.
    :param text_style: Format of the text cells
    """
    for idx, header in enumerate(('Bild', 'Beschreibung', 'Artikelnummer (Jahr)')):
        sheet.write(start_row, idx, header, bold_style)
    sheet.freeze_panes(start_row + 1, 0)
    for row_idx, part in enumerate(sorted(parts, key=lambda x: x['title']), start=start_row + 1):
        img = 'images/parts/{}.png'.format(part['id'])
        if os.path.isfile(img):
            sheet.insert_image(row_idx, 0, img)
        sheet.set_row(row_idx, 100)
        title = part['title']
        sheet.write_formula(row_idx, 1, '=HYPERLINK("{}","{}")'.format(part['url'], title), text_style)
        sheet.write(row_idx, 2, _artnos(part), text_style)
    sheet.set_column(0, 0, 20)
    sheet.set_column(1, 1, 70)
    sheet.set_column(2, 2, 22)


def _artnos(dct):
    """\
    Returns the article numbers as string.

    :param dct: A dict with a "article_numbers" key.
    """
    return ', '.join(['{} ({})'.format(v or '', k or '') for k, v in sorted(dct['article_numbers'].items(), key=itemgetter(0))]).replace('()', '')


def create_kit_xlfiles(db):
    """\
    Creates Excel files for all construction kits of the provided database (a dict).

    :param db: dict with a "kits" and "parts" key which return iterables of dicts.
    """
    for ck in (ck for ck in db['kits'].values() if ck['parts']):
        with open('excel/kits/{}-{}.xlsx'.format(ck['id'], ck['title'].replace(' ', '_')), 'wb') as f:
            f.write(create_kit_xlfile(db, ck))


def create_kit_xlfile(db, ck):
    """\
    Creates a single construction kit Excel document.

    :param db: Dict with a "parts" key.
    :param ck: Dict which represents a construction kit.
    """
    buff = io.BytesIO()
    wb = xlsxwriter.Workbook(buff)
    sheet = wb.add_worksheet(str(ck['id']))
    bold_style = wb.add_format({'bold': True})
    title_style = wb.add_format({'bold': True, 'font_size': 14})
    text_style = wb.add_format({'align': 'top', 'font_color': 'black'})
    sheet.write(0, 0, ck['title'], title_style)
    sheet.write_formula(1, 0, '=HYPERLINK("{}")'.format(ck['url']), text_style)
    sheet.write(2, 0, _artnos(ck['article_numbers']))
    img = 'images/kits/{}.png'.format(ck['id'])
    if os.path.isfile(img):
        sheet.insert_image(3, 0, img)
        sheet.set_row(3, 180)
    parts = sorted((part for part in db['parts'].values() if str(part['id']) in ck['parts']), key=lambda x: x['title'])
    write_parts(sheet, parts, start_row=4, bold_style=bold_style, text_style=text_style)
    wb.close()
    return buff.getvalue()


if __name__ == '__main__':
    try:
        os.mkdir('excel')
    except FileExistsError:
        pass
    try:
        os.mkdir('excel/kits')
    except FileExistsError:
        pass
    with open('ftdb-dump.json', 'r') as f:
        db = json.load(f)
    create_parts_xlfile(db)
    create_kit_xlfiles(db)
