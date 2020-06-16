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
from collections import namedtuple
import xlsxwriter


Row = namedtuple('Row', ['id', 'title', 'url', 'article_numbers', 'count'], defaults=(None,))


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
    write_header(sheet, ('Bild', 'Beschreibung', 'Artikelnummer (Jahr)'), row=0, header_style=bold_style)
    write_parts(sheet, (Row(p['id'], p['title'], p['url'], p['article_numbers']) for p in db['parts'].values()),
                start_row=1, text_style=text_style)
    wb.close()
    with open('excel/einzelteile.xlsx', 'wb') as f:
        f.write(buff.getvalue())


def write_header(sheet, headers, row, header_style):
    """\
    Writes a header and freezes the row after the header row.
    
    :param sheet: Worksheet
    :param headers: Iterable of strings.
    :param row: Row index of the header.
    :param header_style: Format of the header cells.
    """
    for idx, header in enumerate(headers):
        sheet.write(row, idx, header, header_style)
    sheet.freeze_panes(row + 1, 0)


def write_parts(sheet, rows, start_row, text_style=None):
    """\
    Writes parts specification.

    :param sheet: Worksheet
    :param rows: Iterable of Row instances.
    :param start_row: Start row index.
    :param text_style: Format of the text cells
    """
    article_nos_col = 2
    for row_idx, row in enumerate(rows, start=start_row):
        img = 'images/parts/{}.png'.format(row.id)
        if os.path.isfile(img):
            sheet.insert_image(row_idx, 0, img)
        sheet.set_row(row_idx, 100)
        sheet.write_formula(row_idx, 1, '=HYPERLINK("{}","{}")'.format(row.url, row.title), text_style)
        if row.count:
            article_nos_col = 3
            sheet.write(row_idx, 2, row.count, text_style)
        sheet.write(row_idx, article_nos_col, _artnos(row.article_numbers), text_style)
    sheet.set_column(0, 0, 20)
    sheet.set_column(1, 1, 70)
    sheet.set_column(article_nos_col, article_nos_col, 22)


def _artnos(dct):
    """\
    Returns the article numbers as string.

    :param dct: A dict with a artno -> year mapping.
    """
    return ', '.join(['{} ({})'.format(v or '', k or '') for k, v in sorted(dct.items(), key=itemgetter(0))]).replace('()', '')


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
    write_header(sheet, ('Bild', 'Beschreibung', 'Anzahl', 'Artikelnummer (Jahr)'), row=4, header_style=bold_style)
    parts = sorted((part for part in db['parts'].values() if str(part['id']) in ck['parts']), key=itemgetter('title'))
    write_parts(sheet, (Row(p['id'], p['title'], p['url'], p['article_numbers'], ck['parts'][str(p['id'])]) for p in parts),
                start_row=5, text_style=text_style)
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
