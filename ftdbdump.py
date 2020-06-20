#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# FTDB - Dump -- Downloads all construction kits from FTDB.
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
import json
import requests


def download_construction_kits(sess):
    """\
    Downloads all construction kits.

    :param sess: requests.Session
    :rtype: dict
    """
    url = 'https://ft-datenbank.de/api/tickets?drill_ft_cat_all=653'
    dct = _fetch_json(sess, url)
    construction_kits = {}
    parts = {}
    result = {'kits': construction_kits,
              'parts': parts}
    total_pages = dct['cPages'] + 1
    for i in range(1, total_pages):
        dct = _fetch_json(sess, url + '&page={}'.format(i))
        for ticket_id in parse_construction_kit_ids(dct):
            ck = get_construction_kit(sess, ticket_id)
            construction_kits[ck['id']] = ck
    parts_url = 'https://ft-datenbank.de/api/ft-partslist/'
    for ticket_id in construction_kits.keys():
        ck = construction_kits[ticket_id]
        dct = _fetch_json(sess, parts_url + str(ticket_id))
        if dct['cTotal'] == 0:
            continue
        total_pages = dct['cPages'] + 1
        for i in range(1, total_pages):
            dct = _fetch_json(sess, parts_url + '{}?page={}'.format(ticket_id, i))
            for part in parse_parts(dct):
                part_id = part['id']
                ck['parts'][part_id] = part.pop('count', None)
                parts[part_id] = part
    return result


def _fetch_json(sess, url):
    """\
    Fetches the provided url and returns the JSON result as dict.

    :param sess: requests.Session
    :param url: The URL to fetch.
    :rtype: dict
    """
    res = sess.get(url)
    dct = res.json()
    if dct['status'] != 'OK':
        raise Exception('Unexpected result "%s"' % dct['status'])
    return dct


def _parse_article_nos(dct):
    """\
    Parses the article numbers.

    Returns either a dict or None.
    """
    article_numbers = dct.get('ft_article_nos')
    if article_numbers in (None, '[]'):
        return {}
    # Use '' as key since JSON accepts only strings as key, not None / null
    return dict([(k or '', v) for k, v in json.loads(article_numbers)])


def _parse_common(dct):
    """\
    Fetches common information like "ticket_id" from a result set (i.e. construction
    kit or part).

    :param dct: A dict to fetch the information from.
    :rtype: dict
    """
    res = {'id': dct['ticket_id'], 'created': dct['createdUTC'].replace(' ', 'T'),
           'title': dct['title'], 'article_numbers': _parse_article_nos(dct),
           'uuid': dct.get('ft_variant_uuid')}
    url = 'https://ft-datenbank.de/api/ticket/{}'.format(dct['ticket_id'])
    res['url_api'] = url
    res['url'] = url.replace('/api', '')
    icon = dct.get('ft_icon')
    res['thumbnail_url'] = 'https://ft-datenbank.de/thumbnail/{}'.format(icon) if icon else None
    return res


def parse_construction_kit_ids(dct):
    """\
    Returns a list of ticket ids.

    fischertip construction kits (category 661) are omitted.
    """
    return (d['ticket_id'] for d in dct['results'] if '661' not in d['ft_cat_all'])


def parse_parts(dct):
    """\
    Returns an iterable of part dicts.

    Note: Each part contains a "count" key which should be removed since
    it is construction kit specific.

    :param dct: A dict with a "results" key to read the parts from
    """
    for d in dct['results']:
        part_dict = _parse_common(d)
        part_dict['weight'] = d.get('ft_weight')
        cnt = d.get('ft_count')
        part_dict['count'] = int(cnt) if cnt else None
        yield part_dict


def get_construction_kit(sess, ticket_id):
    """\
    Fetches the JSON information for the provided ticket id and returns
    it as Python dict.

    :param sess: requests.Session
    :param ticket_id: The ticket identifier
    """
    dct = _fetch_json(sess, 'https://ft-datenbank.de/api/ticket/{}'.format(ticket_id))['results']
    ck = _parse_common(dct)
    # This information is almost useless since it does not provide a count
    # indicator.
    #contains = dct.get('ft_contains') or []
    #ck['parts'] = dict((part_id, None) for part_id in contains)
    # Set parts to an empty dict, will be filled later
    # Would be more efficient it would be done here, though
    ck['parts'] = {}
    return ck


if __name__ == '__main__':
    import datetime
    sess = requests.session()
    result = download_construction_kits(sess)
    with open('ftdb-dump-{}.json'.format(datetime.date.today().isoformat()), 'w') as f:
        json.dump(result, f, sort_keys=True, indent=2)
