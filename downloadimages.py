#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Downloads thumbnails for construction kits and / or parts.
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
import os
import json
import requests


def download_images(sess, constructs, path, size=200):
    """\
    Downloads all thumbnails and stores them in the provided path.

    :param sess: requests.Session
    :param constructs: Iterable of dicts with a "id" and an optional "thumbnail_url" key.
    :param str path: Path to store the images
    :param int size: Size of the images, default: 200px
    """
    for identifier, url in ((c['id'], c['thumbnail_url']) for c in constructs if c.get('thumbnail_url') is not None):
        res = sess.get('{}?size={}'.format(url, size), stream=True)
        res.raise_for_status()
        content_type = res.headers['Content-Type']
        ext = content_type.replace('image/', '')
        with open(os.path.join(path, '{}.{}'.format(identifier, ext)), 'wb') as f:
            for chunk in res.iter_content(chunk_size=128):
                f.write(chunk)


if __name__ == '__main__':
    try:
        os.mkdir('images')
    except FileExistsError:
        pass
    try:
        os.mkdir('images/kits')
    except FileExistsError:
        pass
    try:
        os.mkdir('images/parts')
    except FileExistsError:
        pass
    with open('ftdb-dump.json', 'r') as f:
        db = json.load(f)
    sess = requests.session()
    download_images(sess, db['kits'].values(), path='images/kits/', size=200)
    #download_images(sess, db['parts'].values(), path='images/parts/', size=100)
