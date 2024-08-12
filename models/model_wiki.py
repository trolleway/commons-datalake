#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
os.environ["PYWIKIBOT_NO_USER_CONFIG"] = '2'

import pywikibot
from pywikibot import pagegenerators
from pywikibot import exceptions
import logging
import pprint
import os
from urllib.parse import urlparse
import tempfile
from PIL import Image
import sys
import shutil

class Model_wiki:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=4)
    cachedir='imgcache'
    cachedfiles_list = list()
    
    def __init__(self):
        
        
        if not os.path.isdir(self.cachedir):
            os.makedirs(self.cachedir)
        self.cachedfiles_list = os.listdir(self.cachedir)
        
        pywikibot.config.max_retries=10
        
        #if not os.path.isfile('../user-config.py'):
        #    raise Exception('''Now you should enter Wikimedia user data in config. Call \n cp user-config.example.py user-config.py
        #\n open user-config.py in text editor, input username,  and run this script next time''')
    
    def compress_image(self,file_path,dst):
        """
        Compresses an image file to JPEG format 

        Args:
            file_path (str): The file path to the image file.

        Returns:
            None
        """
        # Open the image file
        with Image.open(file_path) as img:
            # Compress the image to JPEG format
            img.save(dst, "JPEG", optimize=True)
        
    def category_intersection_download(self,catlist:list,directory:str,convert_mode=None):
        assert len(catlist)>0
        counter = 0
        
        site = pywikibot.Site("commons", "commons")
        #site.login()
        #site.get_tokens("csrf")  # preload csrf token
        
        category_objects=dict()
        generators=dict()
        
        category_counter=0
        category_objects[0] = pywikibot.Category(site, catlist[0])
        generators[category_counter] = pagegenerators.CategorizedPageGenerator(
            category_objects[0], recurse=True, start=None, total=None, content=True, namespaces=None)
        

        if len(catlist)>1:
            for category in catlist[1:]:
                category_counter = category_counter + 1
                category_objects[category_counter] = pywikibot.Category(site, category)
                generators[category_counter] = pagegenerators.CategoryFilterPageGenerator(generators[category_counter-1], [category_objects[category_counter]])
        

        final_generator = generators[category_counter]

        def spinning_cursor():
            while True:
                for cursor in '|/-\\':
                    yield cursor
        spinner = spinning_cursor()

                   
            
        '''if convert_mode is None or convert_mode=='raw':
            for page in final_generator: 
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                self.dowload_or_cache_read(page)
                sys.stdout.write('\b') 
        elif convert_mode=='sns':
        '''
        
        listfiles_cache = os.listdir(self.cachedir)
        
        for page in final_generator:
            try:
                url = page.get_file_url() 
            except:
                continue
            # IF FILE IS PHOTO OR VIDEO
            cache_filename = self.dowload_or_cache_read(page)
            #if not url.lower().endswith(('.jpeg','.jpg','.tif','.webp','.webm')): continue
            
            counter = counter+1
            print('file '+str(counter), end='\r')
            #sys.stdout.write(next(spinner))
            #sys.stdout.flush()
            #sys.stdout.write('\b') 
            
            
            
            ext = os.path.splitext(os.path.basename(urlparse(url).path))[1]
            fn=os.path.splitext(os.path.basename(urlparse(url).path))[0]
            if convert_mode == 'sns':
                compressed_filename = os.path.join(directory, str(page.pageid)+'_cmp'+'.jpg')
                
                # COMPRESS PHOTO
                if url.lower().endswith(('.jpeg','.jpg','.tif','.webp')):
                    if not os.path.isfile(compressed_filename):
                        self.compress_image(cache_filename,compressed_filename)
            else:
                out_filename = os.path.join(directory, str(page.pageid)+''+ext)
                if not os.path.isfile(out_filename):
                    shutil.copyfile(cache_filename, out_filename)
                    
                
                
                
                # COMPRESS VIDEO FROM vp9 TO h264
        
    def dowload_or_cache_read(self,FilePage)->str:
            
        url = FilePage.get_file_url()   
        pageid = FilePage.pageid
        filename, file_extension = os.path.splitext(os.path.basename(urlparse(url).path))
        
        cache_filename = str(FilePage.pageid)+''+file_extension
        cache_filepath = os.path.join(self.cachedir, cache_filename )
        #filepath = os.path.join(self.cachedir,fn+ext )
        if cache_filename is self.cachedfiles_list:
            return cache_filepath
        if os.path.isfile(cache_filepath):
            self.logger.info('already downloaded '+cache_filepath)
            self.cachedfiles_list.append(cache_filename)
            return cache_filepath

        FilePage.download(filename=cache_filepath)
        self.cachedfiles_list.append(cache_filename)
        
        return cache_filepath
    
        
