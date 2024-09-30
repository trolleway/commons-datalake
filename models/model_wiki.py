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
from datetime import datetime
import subprocess

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
    exiftool_path = "exiftool"
    site_wikidata = pywikibot.Site("wikidata", "wikidata")
    
    def __init__(self):
        
        
        if not os.path.isdir(self.cachedir):
            os.makedirs(self.cachedir)
        self.cachedfiles_list = os.listdir(self.cachedir)
        
        pywikibot.config.max_retries=10
        
        #if not os.path.isfile('../user-config.py'):
        #    raise Exception('''Now you should enter Wikimedia user data in config. Call \n cp user-config.example.py user-config.py
        #\n open user-config.py in text editor, input username,  and run this script next time''')
    
    def compress_image(self,file_path,dst,quality=80):
        """
        Compresses an image file to JPEG format 

        Args:
            file_path (str): The file path to the image file.

        Returns:
            None
        """
        # Open the image file
        try:
            with Image.open(file_path) as img:
                # Compress the image to JPEG format
                if os.stat(file_path).st_size > 1400000:
                    img.save(dst, "JPEG", optimize=True, quality=quality)
                else:
                    img.save(dst, "JPEG", optimize=True)
        except:
            self.logger.warning('PIL failed to convert https://commons.wikimedia.org/?curid= '+file_path)
            return False
    
    
    def image2datetime(self, path):
    
        def get_datetime_from_string(s):
            # find the substring that matches the format YYYYMMDD_HHMMSS
            # assume it is always 15 characters long and starts with a digit

            for i in range(len(s) - 15):
                if s[i].isdigit():
                    date_str = s[i:i+15]
                    print('test '+date_str)
                    try:
                        datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                        # Valid date string
                        break
                    except ValueError:
                        pass
                        #go next char
                    
            # use datetime.strptime() to convert the substring to a datetime object
            date_obj = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            return date_obj

        with open(path, "rb") as image_file:
            if not path.lower().endswith('.stl'):
                try:
                    image_exif = Image(image_file)
                    
                    dt_str = image_exif.get("datetime_original", None)

                    dt_obj = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                except:
                    dt_obj = None
                    cmd = [self.exiftool_path, path, "-datetimeoriginal", "-csv"]
                    if path.lower().endswith(('.mp4','.mov','.avi')):
                        cmd = [self.exiftool_path, path, "-createdate", "-csv"]
                        self.logger.debug('video')

                    exiftool_text_result = subprocess.check_output(cmd)
                    tmp = exiftool_text_result.splitlines()[1].split(b",")
                    if len(tmp) > 1:
                        dt_str = tmp[1]
                        dt_obj = datetime.strptime(
                            dt_str.decode("UTF-8"), "%Y:%m:%d %H:%M:%S"
                        )
            elif path.lower().endswith('.stl'):
                dt_obj = None

            if dt_obj is None:
                dt_obj = get_datetime_from_string(os.path.basename(path))
                

            if dt_obj is None:
                return None
            return dt_obj 

            
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
        pages_list=list()
        
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
                out_filename = os.path.join(directory, str(page.pageid)+'_cmp'+'.jpg')
                
                # COMPRESS PHOTO
                if url.lower().endswith(('.jpeg','.jpg','.tif','.webp','.tiff')):
                    if not os.path.isfile(out_filename):
                        self.compress_image(cache_filename,out_filename)
            elif convert_mode == 'stocks':
                out_filename = os.path.join(directory, str(page.pageid)+''+'.jpg')
                if url.lower().endswith(('.tiff','.tif','.webp')):
                    self.compress_image(cache_filename,out_filename,quality=95)
                elif not url.lower().endswith(('.jpg','.jpeg')):
                    print('invalid format for stocks '+page.full_url())
                    continue
                else:
                    out_filename = os.path.join(directory, str(page.pageid)+''+ext)
                    shutil.copyfile(cache_filename, out_filename)
                
                            # Get the corresponding ItemPage from the FilePage
               
                #stock get wikibase
                item = page.data_item()
                
                # Fetch the data of the item
                item.get()
                
                # Print the WikiBase entities
                #print("WikiBase entities for the file:", page.title())
                entities=list()
                for prop, claims in item.claims.items():
                    for claim in claims:
                        #print(f"Property: {prop}, Target: {claim.getTarget()}")
                        if prop=='P180':
                            entities.append(claim.getTarget())


                
                caption, keywords = self.get_shutterstock_desc(page,cache_filename,'Q649',None)
                self.write_iptc(out_filename, caption, keywords)
            

                    

            else:
                out_filename = os.path.join(directory, str(page.pageid)+''+ext)
                if not os.path.isfile(out_filename):
                    shutil.copyfile(cache_filename, out_filename)
                    
                
                
        return pages_list    
                # COMPRESS VIDEO FROM vp9 TO h264
                
    def write_iptc(self, path, caption, keywords):
        # path can be both filename or directory
        assert os.path.exists(path)

        '''
        To prevent duplication when adding new items, specific items can be deleted then added back again in the same command. For example, the following command adds the keywords "one" and "two", ensuring that they are not duplicated if they already existed in the keywords of an image:

exiftool -keywords-=one -keywords+=one -keywords-=two -keywords+=two DIR
        '''

        # workaround for write utf-8 keywords: write them to file
        argfiletext = ''

        if isinstance(keywords, list) and len(keywords) > 0:
            for keyword in keywords:
                argfiletext += '-keywords-='+keyword+''+" \n"+'-keywords+='+keyword+' '+"\n"

        argfile = tempfile.NamedTemporaryFile()
        argfilename = 't.txt'
        with open(argfilename, 'w') as f:
            print(f'write to {argfilename}')
            print(argfiletext)
            f.write(argfiletext)

        cmd = [self.exiftool_path, '-preserve', '-overwrite_original', '-charset iptc=UTF8', '-charset', 'utf8', '-codedcharacterset=utf8',
               '-@', argfilename, path]
        print(' '.join(cmd))
        response = subprocess.run(cmd, capture_output=True)

        if isinstance(caption, str):
            cmd = [self.exiftool_path, '-preserve', '-overwrite_original',
                   '-Caption-Abstract='+caption+'', path]
            response = subprocess.run(cmd, capture_output=True)


    def get_image_datetime(self,filename)->datetime:

        dt_obj = self.image2datetime(filename)

        return dt_obj

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
    
    def get_shutterstock_desc(self, page, filename, city_wdid, date=None) -> list:
        # https://support.submit.shutterstock.com/s/article/How-do-I-include-metadata-with-my-content?language=en_US
        '''
        Column A: Filename
Column B: Description
Column C: Keywords (separated by commas)
Column D: Categories ( 1 or 2, separated by commas, must be selected from this list)
Column E*: Illustration (Yes or No)
Column F*: Mature Content (Yes or No)
Column G*: Editorial (Yes or No)

he Illustration , Mature Content, and Editorial tags are optional and can be included or excluded from your CSV 
 Think of your title as a news headline and try to answer the main questions of: Who, What, When, Where, and Why. Be descriptive and use words that capture the emotion or mood of the image.
 Keywords must be in English, however, exceptions are made for scientific Latin names of plants and animals, names of places, and foreign terms or phrases commonly used in the English language.


Kaliningrad, Russia - August 28 2021: Tram car Tatra KT4 in city streets, in red color


        '''



        desc = {
            'Filename': filename,
            'Description': '',
            'Keywords': '',
            'Categories': '',
            'Editorial': 'Yes',
        }
        keywords = list()
        
        item = page.data_item()
        
        # Fetch the data of the item
        item.get()
        
        # Print the WikiBase entities
        #print("WikiBase entities for the file:", page.title())
        entities=list()
        tags=list()
        for prop, claims in item.claims.items():
            for claim in claims:
                #print(f"Property: {prop}, Target: {claim.getTarget()}")
                if prop=='P180':
                    entities.append(claim.getTarget())
                    #entity = pywikibot.ItemPage(self.site_wikidata, claim.getTarget().id)
                    #entity.get()
                    labels_pywikibot = claim.getTarget().labels.toJSON()
                    #print(labels_pywikibot['en']['value'])
                    if 'en' not in labels_pywikibot:
                        print('not enough en label in '+str(claim.getTarget()))
                        quit()
                        
                    tags.append(labels_pywikibot['en']['value'])
        # city
        city_entity = pywikibot.ItemPage(self.site_wikidata, city_wdid)
        city_entity.get()
        city_label = city_entity.labels.toJSON()['en']['value']
        #print(city_entity.claims.get_best_claim('P17'))
        #claims = city_label.claims
        property_id = 'P17'
        claims = city_entity.claims.get(property_id, [])
        best_claim = None
        for claim in claims:
            if best_claim is None or claim.rank > best_claim.rank:
                best_claim = claim
        if best_claim:
            #print(f"Best claim for property {property_id} country: {best_claim}")
            country_label = best_claim.getTarget().labels.toJSON()['en']['value']
            #country_label = best_claim.labels.toJSON()['en']['value']
        else:
            print(f"No claims found for property {property_id}.")
   
        dt_obj = self.get_image_datetime(filename)    


        
        desc = '{city_label}, {country_label} - {date}: {caption}'.format(
            city_label=city_label,
            country_label=country_label,
            date=dt_obj.strftime("%B %-d %Y"),
            caption=' '.join(tags)
        )
        
        tags.append(city_label)
        return desc,tags

    

