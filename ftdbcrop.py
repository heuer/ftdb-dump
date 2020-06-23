#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Crops images.
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
import glob
from functools import partial
from PIL import Image, ImageChops


def crop_image(img, padding=None):
    """\
    Crops an image / removes the white frame around an image.

    :param img: The image.
    :param padding: Optional padding around the image in pixels, default: None
    """
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if not bbox:
        return img
    if padding is not None:
        width, height = bg.size
        left, upper, right, lower = bbox
        bbox = max(0, left - padding), max(0, upper - padding), min(width, right + padding), min(height, lower + padding)
    return img.crop(bbox)


def crop_images(source_dir, target_dir, padding=None):
    """\
    Crops all images of the source directory and saves the result in the target dir.

    :param str source_dir: The source directory.
    :param str target_dir: The target directory.
    :param padding: Optional padding around the image in pixels.
    """
    trim_img = partial(crop_image, padding=padding)
    mask = '*.[gpj]*'
    for name, img in ((os.path.basename(name), Image.open(name)) for name in glob.glob(os.path.join(source_dir, mask))):
        trim_img(img).save(os.path.join(target_dir, name.replace('.gif', '.png')))


def thumbnails(source_dir, target_dir, size):
    """\
    Creates thumbnails of all images in the source dir and saves them in the
    target directory.

    :param str source_dir: The source directory.
    :param str target_dir: The target directory.
    :param tuple size: (width, height) tuple.
    """
    mask = '*.[pj]*'
    for name, img in ((os.path.basename(name), Image.open(name)) for name in glob.glob(os.path.join(source_dir, mask))):
        img.thumbnail(size, Image.LANCZOS)
        img.save(os.path.join(target_dir, name))


if __name__ == '__main__':
    for path in ('cropped_images', 'cropped_images/kits', 'cropped_images/parts',
                 'thumbnails', 'thumbnails/kits', 'thumbnails/parts'):
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
    crop_images('images/parts/', 'cropped_images/parts', padding=2)
    crop_images('images/kits/', 'cropped_images/kits')
    thumbnails('cropped_images/parts', 'thumbnails/parts', (100, 100))
    thumbnails('cropped_images/kits', 'thumbnails/kits', (200, 200))
