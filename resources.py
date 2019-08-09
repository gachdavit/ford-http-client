# We are trying to avoid "Circular Import"
import os
import requests
import collections
import app
from utils import (
    correct_name_generator, get_svg, set_cookie
)

DEFAULT_CHUNK_SIZE = 1024

class Resource:

    # __slots__ is advance feature of python
    # we can reduce usage of RAM, because we don't have __dict__ attribute anymore.
    
    __slots__ = (
        'title',
        'number',
        'dirname',
        'url',
        'slider_images',
        'sections_data'
    )

    SECTION_IMAGES = 'https://parts.ford.com/images/section-images/'
    RELATED_ITEMS_URL = 'https://parts.ford.com/shop/FordRelatedItemsView'

    def __init__(self, url):
        self.url = url
        cookies = set_cookie()
        setattr(type(self), 'COOKIES', cookies) # COOKIES is static variable
    
    def download(self, new_dir):
        for slider_image in self.slider_images:
            os_slider_image = os.path.basename(slider_image)
            slider_image_path = os.path.join(new_dir, correct_name_generator(os_slider_image))
            response = requests.get(slider_image, cookies=self.__class__.COOKIES)
            with open(slider_image_path, 'wb') as f:
                f.write(response.content)
        section_data_dict = self.sections_data.items()
        with open(os.path.join(new_dir, 'www'), 'w+') as f:
            f.write(self.url)
        for index, (section_id, section_data) in enumerate(section_data_dict, start=1):
            image = section_data['image'].lstrip('/')
            if 'http' not in image:
                image = os.path.join(self.__class__.SECTION_IMAGES, image)
            if len(section_data_dict) == 1:
                filename = os.path.basename(image)
                image_path = os.path.join(new_dir, filename) if filename else ''
                with open(os.path.join(new_dir, 'related_parts'), 'w+') as f:
                    f.write(section_data['text'])
            else:
                dir_index = str(index) # this is directory name... represents sectionId
                dir_with_section = app.OSMixin.create_subdir(new_dir, correct_name_generator(dir_index))
                with open(os.path.join(dir_with_section, 'related_parts'), 'w+') as f:
                    f.write(section_data['text'])
                filename = os.path.basename(image)
                image_path = os.path.join(dir_with_section, filename) if filename else ''
            response = requests.get(image, cookies=self.__class__.COOKIES)
            if image_path:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                image_to_svg = get_svg(image)
                svg_image_response = requests.get(image_to_svg, cookies=self.__class__.COOKIES, stream=True)
                if svg_image_response.status_code == 200:
                    get_svg_path = get_svg(image_path)
                    with open(get_svg_path, 'wb') as f:
                        for chunk in svg_image_response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)

# uses list_iterator object behind the scenes !!!
class ResourceSet(collections.Iterable):
    
    def __init__(self):
        self.container = []

    def __str__(self):
        left_expression = '['
        right_expression = ']'
        beautify = ''
        for item in self.container:
            beautify += item.url + ', '
        beautify = left_expression + beautify.rstrip(', ') +  right_expression
        return beautify

    __repr__ = __str__

    def __iter__(self):
        return iter(self.container)
    
    def __len__(self):
        return len(self.container)

    def add(self, param):
        # list's extend's like interface implementation below.
        if isinstance(param, Resource):
            self.container.append(param)
        if isinstance(param, ResourceSet):
            for resource in param:
                self.container.append(resource)
