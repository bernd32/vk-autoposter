import random
import linecache
import vk_api
import requests
from bs4 import BeautifulSoup
import time
from vk_api import VkUpload
import configparser
import logging
import os
from datetime import datetime


def get_files(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for f in files:
        if not f.startswith('.'):
            yield f


def get_mal_picture():
    """
    :return: Anime picture URL from MyAnimeList.net, number of attempts to find it,
    and anime's ID on MAL
    """
    attempts = 0
    while True:
        attempts += 1
        mal_id = str(random.randint(1, 40000))
        result = requests.get('https://myanimelist.net/anime/' + mal_id + '/a/pics')
        page = result.text
        soup = BeautifulSoup(page, 'html.parser')
        try:
            img_src = soup.find('a', class_='js-picture-gallery')['href']
        except (AttributeError, TypeError):
            img_src = 404
        if img_src != 404:
            return img_src, attempts, mal_id
        else:
            time.sleep(1)  # Wait a second before starting a new search
           
def get_vndb_picture():
    """
    :return: VN picture URL from vndb, number of attempts to find it,
    and vndb's ID
    """
    attempts = 0
    while True:
        attempts += 1
        vndb_id = str(random.randint(1, 26400))
        result = requests.get('https://vndb.org/v' + vndb_id)
        page = result.text
        soup = BeautifulSoup(page, 'html.parser')
        try:
            img_src = soup.find('div', class_='imghover--visible').img['src']
        except (AttributeError, TypeError):
            img_src = 404
        if img_src != 404:
            return img_src, attempts, vndb_id
        else:
            time.sleep(1)  # Wait a second before starting a new search


def get_verse(filepath, min_len):
    """
    :param filepath: Path to txt-file (e.g. /home/Documents/file.txt or file.txt)
    :param min_len: Minimum line length
    :return: A random text line (exclude ones with ':', '=' etc. last character)
    """
    if filepath == '':
        return '', 0
    else:
        attempts = 0
        lines = sum(1 for line in open(filepath))
        while True:
            attempts += 1
            line = linecache.getline(filepath, random.randint(2, lines))
            line = line.rstrip()
            last_sym = line[-1:]
            if last_sym not in (",", ":", "=", "-") and len(line) > min_len:
                return line, attempts


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='events.log',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.DEBUG)

    scope = 'wall,photos'
    # Reading config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    login = config['Auth']['Login']
    password = config['Auth']['Password']
    app_id = config['Auth']['App_ID']
    txt_file = config['Post']['TxtFile']
    min_length = config['Post']['LineMinimumLength']
    post_interval = config['Post']['PostInterval']
    attach_photo = config['Post']['AttachPhoto']
    owner_id = config['Post']['OwnerID']
    photo_source = config['Post']['PhotoSource']
    photo_location = config['Post']['PhotoLocation']
    random_line = config['Post']['RandomLine']

    if app_id == '':
        print('Specify app id in config.ini')
        quit()
    if (photo_source == 'local' or photo_source == 'rand-local') and photo_location == '':
        print('Specify your photo location in config.ini')
        quit()
    if owner_id == '':
        owner_id = None
    else:
        owner_id = int(owner_id)

    current_position = 0
    
    while True:
        session = requests.Session()
        vk_session = vk_api.VkApi(login=login, password=password,
                                  app_id=int(app_id), scope=scope)
        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            logging.error(error_msg)
            return
        vk = vk_session.get_api()
        upload = VkUpload(vk_session)
        attachments = []
        
        if post_interval == '':
            # post a message in random interval between 1 and 10800 seconds
            post_interval = random.randint(1, 10800)
            logging.info('Random interval = true')

        if attach_photo == 'yes':
            # Loading a picture
            if photo_source == 'mal':
                image_url, p_attempts, mal_id = get_mal_picture()
                image = session.get(image_url, stream=True)
                photo = upload.photo_wall(photos=image.raw)[0]
                attachments.append(
                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                )
                logging.info('Attempts to find a picture: %s', str(p_attempts))
                logging.info('MAL ID: %s', str(mal_id))
                
            if photo_source == 'vndb':
                image_url, p_attempts, vn_id = get_vndb_picture()
                image = session.get(image_url, stream=True)
                photo = upload.photo_wall(photos=image.raw)[0]
                attachments.append(
                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                )
                logging.info('Attempts to find a picture: %s', str(p_attempts))
                logging.info('VNDB ID: %s', str(vn_id))
                
            if photo_source == 'rand-local':
                files = list(get_files(photo_location))
                image = random.choice(files)
                image = photo_location + '\\' + image
                photo = upload.photo_wall(photos=image)[0]
                attachments.append(
                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                )
                
            if photo_source == 'local':
                files = list(get_files(photo_location))
                if current_position >= len(files):
                    current_position = 0
                current_position += 1
                image = photo_location + '\\' + files[current_position-1]
                photo = upload.photo_wall(photos=image)[0]
                attachments.append(
                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                )

        text, v_attempts = get_verse(txt_file, int(min_length))
        vk.wall.post(attachment=','.join(attachments), message=text, owner_id=owner_id)
        logging.info('Sent text: "%s"', text)
        logging.info('Attempts to find a text: %s', str(v_attempts))
        print('Message sent')
        timestamp = int(time.time())
        value = datetime.fromtimestamp(timestamp + int(post_interval))
        next_message = value.strftime('%H:%M:%S')
        print('Next message in %s seconds (%s)' % (post_interval, next_message))
        time.sleep(int(post_interval))


if __name__ == '__main__':
    main()
