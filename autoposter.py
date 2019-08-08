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


def get_poster():
    """
    For testing purposes. 
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
    min_length = int(config['Post']['LineMinimumLength'])
    post_interval = config['Post']['PostInterval']
    attach_photo = config['Post']['AttachPhoto']
    owner_id = config['Post']['OwnerID']
    photo_source = config['Post']['PhotoSource']
    photo_location = config['Post']['PhotoLocation']
    random_line = config['Post']['RandomLine']

    if txt_file == '':
        print('Specify your text file in config.ini')
        quit()
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
    line_position = 0
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

        # Get a picture
        upload = VkUpload(vk_session)
        attachments = []
        if attach_photo == 'yes':
            # Loading a picture
            if photo_source == 'mal':
                image_url, p_attempts, mal_id = get_poster()
                image = session.get(image_url, stream=True)
                photo = upload.photo_wall(photos=image.raw)[0]
                logging.info('Attempts to find a picture: %s', str(p_attempts))
                logging.info('MAL ID: %s', str(mal_id))
            if photo_source == 'rand-local':
                files = list(get_files(photo_location))
                image = random.choice(files)
                image = photo_location + '\\' + image
                photo = upload.photo_wall(photos=image)[0]
                logging.info('Photo attached:' + image)
            if photo_source == 'local':
                files = list(get_files(photo_location))
                if current_position >= len(files):
                    current_position = 0  # Reset
                current_position += 1
                image = photo_location + '\\' + files[current_position-1]
                photo = upload.photo_wall(photos=image)[0]
                logging.info('Photo attached:' + image)
            attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))

        # Get a text
        total_lines = sum(1 for line in open(txt_file))
        if random_line == 'yes':
            # Filtering random lines using the loop
            while True:
                curr_line = linecache.getline(txt_file, random.randint(1, total_lines))
                if len(curr_line) >= min_length:
                    txt_line = curr_line
                    break
        else:
            # Filtering lines and sending them one by one.
            # Start over from the first line after last line is sent
            with open(txt_file) as f:
                lines = filter(lambda s: len(s) >= min_length, (line.rstrip() for line in f))
                lines_list = list(lines)
                txt_line = lines_list[line_position]
            line_position += 1
            if line_position >= len(lines_list):
                line_position = 0

        vk.wall.post(attachment=','.join(attachments), message=txt_line, owner_id=owner_id)
        logging.info('Sent text: "%s"', txt_line)
        print('Message sent')
        timestamp = int(time.time())
        value = datetime.fromtimestamp(timestamp + int(post_interval))
        next_message = value.strftime('%H:%M:%S')
        print('Next message in %s seconds (%s)' % (post_interval, next_message))
        time.sleep(int(post_interval))


if __name__ == '__main__':
    main()
