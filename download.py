#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pywikibot
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description=" ")

    parser.add_argument('-ci','--categories_intersection', type=str, required=True, nargs='2', help='list of commons categories for intersection search')
    # PROPOSED ARGUMENTS:
    # --target raw Download source files as is
    # --target sns compress tiff/webp images to jpeg, video to mp4, maybe downsize very big canvas. adds unsharp mask

    # --print-date overlay date in image using google fonts. Date take from commons SDC or EXIF 
    args = parser.parse_args()

    # DOWNLOAD FILES FROM CATEGORY INTERSECTIONS
