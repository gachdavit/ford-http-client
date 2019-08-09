# this is collection of helper methods
import os
import json

def correct_name_generator(name):
    #  general purpose method. used for various situations
    return name.replace('/', '-')

def get_svg(image_name):
    name, ext = os.path.splitext(image_name)
    return name +'.svg'

def get_html(image_name):        
    name, ext = os.path.splitext(image_name)
    return name +'.html'

def create_subdir(dir1, dir2):
    subdirname = os.path.join(dir1, dir2)
    try:
        os.mkdir(subdirname)
    except FileExistsError as exc:
        subdirname = generate_unique_dirname(subdirname)
        os.mkdir(subdirname)
    return subdirname

def set_cookie():
    cookie_file = open('cookies.json', 'r')
    cookie_dict = json.load(cookie_file)
    cookie_file.close()
    return cookie_dict

def generate_unique_dirname(dir_):
    while os.path.exists(dir_):
        dir_ += '-1'
    return dir_

if __name__ == '__main__':
    # this is for testing
    #new_dir = os.path.exists('')
    ''' '''
    dir_ = '/home/dgach/Desktop/http client/a'
    generate_unique_dirname(dir_)