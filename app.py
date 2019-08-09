# We are trying to avoid "Circular Import"
# https://parts.ford.com/ will delete session after ~6-7 hours...
# speed up download process or generate new cookies after several hours...

import os
import time
import datetime
import requests
import parsers
import resources
from utils import (
    correct_name_generator, 
    create_subdir, 
    set_cookie
)

class OSMixin:
    
    BASE_DIR = '/home/dgachechiladze/Desktop/Ford'

    def create_dir(self, menu_name):
        dirname = os.path.join(OSMixin.BASE_DIR, menu_name)
        try:
            os.mkdir(dirname)
        except FileExistsError as exc:
            pass # this happened when dir already exists... return name, but avoid creation
        return dirname

    create_subdir = staticmethod(create_subdir)

# We have large datasets...
# avoid recursion usage !!!
# >>> import sys
# >>> sys.getrecursionlimit() << never ignore this to avoid runtime error
class DownloadClient(OSMixin):

    BASE_URL = 'https://parts.ford.com/shop/en/us/shop-parts'
    XHR_BASE_URL = 'https://parts.ford.com/shop/FordRelatedItemsView'
    
    def __init__(self):
        self.menu_dict = {} # this variable is shared by multiple methods...
        cookies = set_cookie()
        setattr(type(self), 'COOKIES', cookies) # COOKIES is static variable
        
    def _get_menu(self):
        print('=====================================Start Menu Parsing=====================================================')
        response = requests.get(self.__class__.BASE_URL, cookies=self.__class__.COOKIES)
        menu_parser = parsers.MenuPageParser(response.text)
        setattr(self, 'menu_dict', menu_parser.parse())
        print('=====================================End Menu Parsing=====================================================')

    def _get_list(self):
        print('=====================================Start List Parsing=====================================================')
        for menu_name, submenus in self.menu_dict.items():
            for submenu in submenus:
                url = submenu['url']
                try:
                    submenu['resources'] = resources.ResourceSet()
                    print('=============> List Url => ', url)
                    response = requests.get(url, cookies=self.__class__.COOKIES)
                    num_pages = parsers.ListPageParser.get_num_pages(response.text)
                    get_range = parsers.ListPageParser.generate_page_range(num_pages)
                    for page_num in get_range:
                        new_url = parsers.ListPageParser.generate_valid_url(url, page_num)
                        print('=========================> List Url(Pagination) => ', new_url)
                        response = requests.get(new_url, cookies=self.__class__.COOKIES)
                        list_parser = parsers.ListPageParser(response.text)
                        resource_set = list_parser.parse()
                        submenu['resources'].add(resource_set)
                except requests.exceptions.RequestException:
                    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Http Problem XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                    time.sleep(15)
        print('=====================================End List Parsing=====================================================')

    def _get_content(self):
        print('=====================================Start Content Parsing=====================================================')
        for menu_name, submenus in self.menu_dict.items():
            for submenu in submenus:
                for resource in submenu['resources']:
                    print('========================> Resource Url => ', resource.url)
                    try:
                        response = requests.get(resource.url, cookies=self.__class__.COOKIES)
                        content_parser = parsers.ContentPageParser(response.text)
                        parsed_dict = content_parser.parse()
                        resource.title = parsed_dict['title']
                        resource.number = parsed_dict['number']
                        resource.dirname = '{title}_{number}'.format(
                            title=resource.title,
                            number=resource.number
                        )
                        resource.slider_images = parsed_dict['slider_images']
                        resource.sections_data = parsed_dict['section_data']
                        for section_id, section_value in resource.sections_data.items():
                            for xhr_key, xhr_value in section_value.items():
                                if isinstance(xhr_value, dict):
                                    try:
                                        # Ford's server ignores X-Requested-With: XMLHttpRequest
                                        xhr_response = requests.get(self.__class__.XHR_BASE_URL, params=xhr_value, cookies=self.__class__.COOKIES)
                                        print('==========================================> xhr_url ', xhr_response.url)
                                        text = parsers.ContentPageParser.xhr_response_parser(xhr_response.text)
                                        section_value['text'] = text
                                    except requests.exceptions.RequestException:
                                        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Http Problem XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                                        time.sleep(15)
                    except requests.exceptions.RequestException:
                        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Http Problem XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                        time.sleep(15)
                        # wait 15 seconds...
        print('=====================================End Content Parsing=====================================================')

    def start_download(self):
        print('=====================================Start Download=====================================================')
        for menu_name, submenus in self.menu_dict.items():
            dirname = self.create_dir(menu_name)
            for submenu in submenus:
                submenu_name = submenu['name']
                subdirname = self.create_subdir(dirname, submenu_name)
                for resource in submenu['resources']:
                    try:
                        print('Resource url ====> ', resource.url)
                        try:
                            new_dir = self.create_subdir(subdirname, correct_name_generator(resource.dirname))
                        except Exception as exc:
                            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Problem During Resource Dir Creation XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Resource_Dir => ', new_dir)
                        else:
                            resource.download(new_dir)
                    except requests.exceptions.RequestException:
                        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Http Problem XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                        time.sleep(15)
        print('=====================================End Download=====================================================')

    def _send_request(self):
        # implements request execution ordering !!!
        # 1 -> Parse Menu View 
        # 2 -> Parse List View 
        # 3 -> Parse Content View 
        # 4 -> Download
        start = datetime.datetime.now()
        self._get_menu()
        self._get_list()
        self._get_content()
        self.start_download()
        stop = datetime.datetime.now()
        print('Finished in  =====================================> ', stop-start)

    def __call__(self):
        self._send_request()

def main():
    dc = DownloadClient()
    dc()

if __name__ == '__main__':
    main()