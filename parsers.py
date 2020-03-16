import os
import copy
import collections
import math
from bs4 import BeautifulSoup
from resources import Resource, ResourceSet
from utils import correct_name_generator

# custom exception
class BadParsedNumPages(Exception):
    pass
    
class BasePageParser:
    
    DEFAULT_PARSER = 'lxml'

    def __init__(self, html_stream):
        self._html_stream = html_stream

    correct_name_generator = staticmethod(correct_name_generator)

class MenuPageParser(BasePageParser):

    def parse(self):
        menu_dict = collections.OrderedDict()
        soup = BeautifulSoup(self._html_stream, self.__class__.DEFAULT_PARSER)
        divs = soup.find_all('div', {'id': 'heading1'})
        for div in divs:
            menu = {}
            h4 = div.find('h4')
            h4_verbose = h4.text.replace('\n', '').strip()
            normalize_h4_verbose = self.__class__.correct_name_generator(h4_verbose)
            inner_divs = div.find_next_siblings('div')
            for inner_div in inner_divs:
                lis = inner_div.find_all('li')
                for li in lis:
                    a = li.find('a')
                    a_href = a['href']
                    a_verbose = a.get_text()
                    normalize_a_verbose = self.__class__.correct_name_generator(a_verbose)
                    menu_dict.setdefault(normalize_h4_verbose, []).append({
                        'name': normalize_a_verbose,
                        'url': a_href,
                    })
        return menu_dict

class ListPageParser(BasePageParser):

    ITEM_PER_PAGE = 100 # this is performance optimizer !!! reduce num requests !!! ~ 3x faster than 12 per page
    PAGINATION_SUFFIX = '#list' # this is "fragment identified" SUFFIX for URL

    def parse(self):
        SECTION_ID = '#sectionId'
        USAGES = '#usages'
        resource_set = ResourceSet()
        soup = BeautifulSoup(self._html_stream, self.__class__.DEFAULT_PARSER)
        divs = soup.find_all('div', {'class': 'partTile'})
        prev_url = None
        for div in divs:
            a = div.find('a')
            a_href = a['href']
            if USAGES in a_href:
                continue
            if SECTION_ID in a_href:
                url = a_href.split('#')[0]
                if prev_url is None:
                    resource = Resource(url=url)
                    resource_set.add(resource)
                    prev_url = url
                    continue
                else:
                    if prev_url == url:
                        continue
                    else:
                        resource = Resource(url=url)
                        resource_set.add(resource)
                        prev_url = url
                        continue
            resource = Resource(url=a_href)
            resource_set.add(resource)
        return resource_set

    @classmethod
    def get_num_pages(cls, html_stream):
        soup = BeautifulSoup(html_stream, cls.DEFAULT_PARSER)
        span = soup.find('span', {'class': 'resultCount'})
        filtered = list(filter(None, span.get_text().split(' ')))
        try:
            get_number = filtered[-2] 
            try:
                get_int = math.ceil(int(get_number) / cls.ITEM_PER_PAGE)
            except ValueError:
                get_number = get_number.replace(',', '')
                get_int = math.ceil(int(get_number) / cls.ITEM_PER_PAGE)
            return get_int
        except IndexError:
            raise BadParsedNumPages
    
    @staticmethod
    def generate_page_range(num_pages):
        return range(1, num_pages+1)

    @classmethod
    def generate_valid_url(cls, url, page_num):
        # URL: https://parts.ford.com/shop/en/us/accessories/electronics/<item_per_page>/<page>#list
        return '{url}/{item_per_page}/{page_num}{suffix}'.format(
            url=url,
            item_per_page=cls.ITEM_PER_PAGE,
            page_num=page_num,
            suffix=cls.PAGINATION_SUFFIX
        )

class JSParser:
    
    LEFT_EXPRESSION = '['
    COLON_EXPRESSION = ':'
    ASSIGNMENT_EXPRESSION = '='
    # SCHEMA's static variables are used only for testing purposes and prototyping...
    SLIDER_SCHEMA = '''
        <script type="text/javascript">
			var imageServicesList = [];
			imageServicesList = {
            "imageData": [
                {
                    "imageFolder": "047",
                    "imagePath": "https://parts.ford.com/images/photo-images/047/",
                    "imageName": "56047.jpg",
                    "imageSequence": "1.0"
                },
                {
                    "imageFolder": "046",
                    "imagePath": "https://parts.ford.com/images/photo-images/046/",
                    "imageName": "56046.jpg",
                    "imageSequence": "2.0"
                },
                {
                    "imageFolder": "045",
                    "imagePath": "https://parts.ford.com/images/photo-images/045/",
                    "imageName": "56045.jpg",
                    "imageSequence": "4.0"
                },
                {
                    "imageFolder": "045",
                    "imagePath": "https://parts.ford.com/images/photo-images/045/",
                    "imageName": "56045.jpg",
                    "imageSequence": "4.0"
                },{
                    "imageFolder": "045",
                    "imagePath": "https://parts.ford.com/images/photo-images/045/",
                    "imageName": "56045.jpg",
                    "imageSequence": "4.0"
                },

                ]
            };
		    var imageHostName='https://parts.ford.com';
		</script>
    '''
    SECTION_IDS_SCHEMA = '''
        <script>
            var recordSetTotal =0;
            
                recordSetTotal= 2;
            
            
            var vinDataComplete=true;
            
        url = window.location.href;
        
        var productDetailsSectionId ='4093766';
        
        if(url.indexOf('#sectionId:') !=-1){
                var usageItemsList = [];
                usageItemsList = [
            {
                "xads_3sectiondescription": "Anti-Lock Braking System",
                "displayDescription": "02/22/2010 - 07/05/2016, F250/350/450/550 Super Duty, Less Traction Control, With Trailer Sway Control (TSC)",
                "xads_5sectionid": "4093766",
                "mfName_ntk": "Ford",
                "name": "Bracket                                                                                                                         ",
                "buyable": 0,
                "longDescription": ["02/22/2010 - 07/05/2016, F250/350/450/550 Super Duty, Less Traction Control, With Trailer Sway Control (TSC)"],
                "catentry_id": "7003158",
                "parentCatentry_id": [6596539],
                "storeent_id": 1251,
                "xillustration_thumb": "f020808502.png",
                "partNumber_ntk": "1832512_991040_132_1",
                "xillustration_full": "f020808502.svg",
                "xbuyable_catentry_id": "6596540"
            },
            {
                "xads_3sectiondescription": "Anti-Lock Braking System",
                "displayDescription": "02/22/2010 - 07/05/2016, F250/350/450/550 Super Duty, Roll Stability Control Brk W/Betc",
                "xads_5sectionid": "4067933",
                "mfName_ntk": "Ford",
                "name": "Bracket                                                                                                                         ",
                "buyable": 0,
                "longDescription": ["02/22/2010 - 07/05/2016, F250/350/450/550 Super Duty, Roll Stability Control Brk W/Betc"],
                "catentry_id": "7003162",
                "parentCatentry_id": [6596539],
                "storeent_id": 1251,
                "xillustration_thumb": "f022372602.png",
                "partNumber_ntk": "1832512_994438_132_1",
                "xillustration_full": "f022372602.svg",
                "xbuyable_catentry_id": "6596540"
            }
            ];
                for(var i=0;i<usageItemsList.length;i++){
                    if(url.substring(url.indexOf('#sectionId:')+11) == usageItemsList[i].xads_5sectionid){
                        
                        var productDetailsSectionId= url.substring(url.indexOf('#sectionId:')+11);
                        break;
                    }
                }
        }
        </script>
    '''

    def __init__(self, soup):
        self.soup = soup

    def get_slider_script_tag(self):
        scripts = self.soup.find_all('script')
        for index, script in enumerate(scripts):
            get_text = script.get_text()
            if 'imageFolder' in get_text and \
               'imagePath' in get_text and \
               'imageName' in get_text and \
               'imageSequence' in get_text:
                return get_text

    # implements JS source code parser
    def get_slider_images(self):
        get_text = self.get_slider_script_tag()
        if get_text is None:
            return []
        tokens = filter(None, get_text.split('\n'))
        pathes, names = [], []
        for token in tokens:
            if self.__class__.COLON_EXPRESSION in token and \
               self.__class__.LEFT_EXPRESSION not in token and \
               self.__class__.ASSIGNMENT_EXPRESSION not in token:
                token = token.replace('"', '').replace(',', '').replace('\t', '').replace(' ', '')
                if 'imagePath' in token:
                    path = token.split('imagePath:')[1]
                    pathes.append(path)
                if 'imageName' in token:
                    name = token.split('imageName:')[1]
                    names.append(name)
        make_zip = zip(pathes, names)
        images = [os.path.join(path, name) for path, name in make_zip]
        return images

    def get_section_script_tag(self):
        scripts = self.soup.find_all('script')
        for index, script in enumerate(scripts):
            get_text = script.get_text()
            if '"xads_5sectionid"' in get_text:
                return get_text
    
    # implements JS source code parser
    def get_section_ids(self):
        get_text = self.get_section_script_tag()
        section_ids = []
        if get_text is None:
            return section_ids
        tokens = filter(None, get_text.split('\n'))
        for token in tokens:
            if token == '\t':
                continue
            token = token.replace('\t', '').replace(' ', '')
            if not token:
                continue
            if '"xads_5sectionid"' in token:
                token = token.split(':')[1].rstrip(',').replace('"', '') # this is sectionId
                section_ids.append(token)
        return section_ids

class ContentPageParser(BasePageParser):

    def parse_related(self, soup):
        inputs = soup.find('div', {'class': 'form-group search-filed'})
        related = {'partnumber': ''}
        for input_ in inputs.find_all('input'):
            if 'partnumber' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'vehicleId' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'parent_category_rn' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'categoryId' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'catalogId' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'langId' in input_['name']:
                related[input_['name']] = input_['value']
            elif 'storeId' in input_['name']:
                related[input_['name']] = input_['value']
        return related

    def parse(self):
        parsed_dict = {}
        soup = BeautifulSoup(self._html_stream, self.__class__.DEFAULT_PARSER)
        h2 = soup.find('h2', {'id': 'productName'})
        span = soup.find('span', {'id': 'productPartNumber'})
        image_list = soup.find_all('img', {'class': 'bdr img-responsive'})
        images = [image['src'] for image in image_list]
        js_parser = JSParser(soup)
        slider_images = js_parser.get_slider_images()
        section_ids = js_parser.get_section_ids()
        xhr_request_body = self.parse_related(soup)
        od_section = collections.OrderedDict() 
        sections_data = zip(section_ids, images)
        for section_id, image in sections_data:
            xhr_dict = copy.copy(xhr_request_body) # python's dict is mutable ! use shallow copy to avoid reference on same pointer !!!
            xhr_dict.update({'sectionId': section_id})
            od_section[section_id] = {
                'image': image,
                'xhr_request_body': xhr_dict,
                'text': ''
            }
        number = self.__class__.parse_number(span.text.split('\n'))
        title = h2.get_text().replace('\n', '').strip()
        parsed_dict.update({
            'title': title, 
            'number': number, 
            'slider_images': slider_images,
            'section_data': od_section
        })
        return parsed_dict

    @classmethod
    def xhr_response_parser(cls, html_stream):
        soup = BeautifulSoup(html_stream, cls.DEFAULT_PARSER)
        h4s = soup.find_all('h4', {'class': 'panel-title'})
        text = ''
        for h4 in h4s:
	        text += h4.get_text().replace('\n', '').replace(' ', '').replace('\t', '') +'\n'
        return text


    @staticmethod
    def parse_number(number_str):
        filtered = list(filter(None, number_str))
        return filtered[0]
