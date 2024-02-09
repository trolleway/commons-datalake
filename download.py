#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from models.model_wiki import Model_wiki

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='''    
    python3 download.py -ci "ZiU-682 in Saint Petersburg" "Photographs_by_Artem_Svetlov/Saint_Petersburg/Trolleybuses"
    ''')

    parser.add_argument('-ci','--categories_intersection', type=str, required=True, nargs=2, help='list of commons categories for intersection search')
    # PROPOSED ARGUMENTS:
    # --target raw Download source files as is
    # --target sns compress tiff/webp images to jpeg, video to mp4, maybe downsize very big canvas. adds unsharp mask

    # --print-date overlay date in image using google fonts. Date take from commons SDC or EXIF 
    args = parser.parse_args()

    # DOWNLOAD FILES FROM CATEGORY INTERSECTIONS
    
    
    modelwiki=Model_wiki()
    modelwiki.category_intersection_download(
        [args.categories_intersection[0],args.categories_intersection[1]],
        'downloads',convert_mode='sns')
    

    
    
    #modelwiki.category_intersection_download(
    #    ['ZiU-682 in Saint Petersburg','Photographs_by_Artem_Svetlov/Saint_Petersburg/Trolleybuses'],
    #    'downloads',convert_mode='sns')
    #modelwiki.category_intersection_download(['Saint Petersburg photographs taken on 2005-07-28'],'downloads')
