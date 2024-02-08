#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
from pywikibot import exceptions
import logging
import pprint
import os


class Model_wiki:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=4)
    
    def __init__(self):
        pass
        #if not os.path.isfile('../user-config.py'):
        #    raise Exception('''Now you should enter Wikimedia user data in config. Call \n cp user-config.example.py user-config.py
        #\n open user-config.py in text editor, input username,  and run this script next time''')

    def category_intersection_download(self,catlist:list,directory:str):
        assert len(catlist)>0
        
        site = pywikibot.Site("commons", "commons")
        site.login()
        site.get_tokens("csrf")  # preload csrf token
        
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
        
        for page in final_generator:
            
            self.download_from_commons(page.full_url(),directory,printonly=True)
        
        
    def download_from_commons(self,url,directory,printonly=False):
        import requests
        import os
        # Set the headers and the base URL for the API request
        headers = {
            # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'User-Agent': 'YOUR_APP_NAME (YOUR_EMAIL_OR_CONTACT_PAGE)'
        }
        base_url = 'https://api.wikimedia.org/core/v1/commons/file/'

        # Extract the filename from the URL
        filename = url.split('/')[-1]

        # Construct the full URL with the filename
        url = base_url + filename

        # Make the request and get the JSON response
        response = requests.get(url, headers=headers).json()

        # Get the file URL and the file extension from the response
        file_url = response['original']['url']


        # Download the file using requests
        r = requests.get(file_url, allow_redirects=True)

        # Save the file to the current working directory with the same name and extension
        dest_path = os.path.join(directory, response['title'] )
        
        if printonly: 
            self.logger.debug(file_url+'  >>>   '+dest_path)
            return
        open(dest_path, 'wb').write(r.content)
