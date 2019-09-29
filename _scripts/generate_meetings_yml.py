# py37
#
# Partially automate generation of meeting YAMLs for CUAMS website
#
# Resources:
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://realpython.com/python-f-strings/
# https://realpython.com/python-requests/
# https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/pagination
# https://realpython.com/python-json/
#
import urllib
import requests
import bs4
import re
import os
import json
import time
import random
from collections import namedtuple

TYPES = ['Main', 'Sunday', 'Bonus']
Show = namedtuple('Show', ['type', 'schedule', 'anime_name'])

def getAnimeYamlBlock(anime_name, assets_dir_string, schedule, delay=3):
    '''Generate YAML-format block for anime_name by querying MAL/ANN/AniList.
    '''

    def searchRequestWrapper(requests_f, delay, **kwargs):
        '''Wrapper to retry on 429 error.
        '''
        max_attempts = 10
        attempt_n = 0
        search_response = requests_f(**kwargs)
        while(True):
            attempt_n += 1
            if attempt_n > max_attempts:
                raise Exception('Max attempts reached.')
            print(f'Attempt {attempt_n} response: {search_response}')
            if search_response.status_code == 200:
                break
            elif search_response.status_code == 429:
                # If we get a retry-after, respect it, otherwise just double
                try:
                    delay = int(search_response.headers['Retry-after'])
                except TypeError:
                    delay = delay*2

                print(f'Delaying for {delay}s ...')
                time.sleep(delay)
            else:
                raise Exception('search_response.status_code', search_response.status_code)
        return(search_response)

    # anime_name = 'Kekkai Sensen & Beyond'
    delay += random.uniform(-1, 1)
    print(f'Delaying for {delay}s ...')
    time.sleep(delay)
    anime_name_encoded = urllib.parse.quote(anime_name)

    #
    # MAL
    #
    print('Querying MAL...')
    search_url = f'https://myanimelist.net/anime.php?q={anime_name_encoded}'
    search_response = searchRequestWrapper(requests.get, delay, url=search_url)

    search_soup = bs4.BeautifulSoup(search_response.text, 'html.parser')
    search_results = search_soup.find_all(id=re.compile('^sarea'))
    print(f'Found {len(search_results)} results')

    if len(search_results):
        # NOTE: assumes first search result is correct
        # TODO: query user to confirm whether result is correct
        anime_url = search_results[0].get('href')

        # Get anime info
        print('Getting MAL anime info...')
        anime_response = searchRequestWrapper(requests.get, delay, url=anime_url, headers = {'User-agent': 'CUAMS Scraper'})

        anime_soup = bs4.BeautifulSoup(anime_response.text, 'html.parser')
        anime_image_url = anime_soup.find(itemprop='image').get('src')

        anime_image_basename = os.path.basename(urllib.parse.urlparse(anime_url).path)
        anime_image_ext = os.path.splitext(urllib.parse.urlparse(anime_image_url).path)[1]
        anime_image_filename = anime_image_basename + anime_image_ext
        urllib.request.urlretrieve(anime_image_url, anime_image_filename)
        print(f'Downloaded anime image: {anime_image_url}')

        anime_episodes = anime_soup.find('span', string='Episodes:').next_sibling.strip()
        anime_aired = anime_soup.find('span', string='Aired:').next_sibling.strip()
        anime_year = anime_aired.split(' to ')[0].split(', ')[1]
        anime_studios = ', '.join(t.string for t in anime_soup.find('span', string='Studios:').find_next_siblings('a'))

    else:
        anime_url = 'https://myanimelist.net/anime/UNKNOWN/UNKNOWN'
        anime_image_filename = 'UNKNOWN'
        anime_episodes = 'UNKNOWN'
        anime_year = 'UNKNOWN'
        anime_studios = 'UNKNOWN'

    #
    # ANN
    #
    print('Querying ANN...')
    search_url = f'https://www.animenewsnetwork.com/encyclopedia/search/name?only=anime&q={anime_name_encoded}'
    search_response = searchRequestWrapper(requests.get, delay, url=search_url)

    search_soup = bs4.BeautifulSoup(search_response.text, 'html.parser')
    search_results = search_soup.find(id='content-zone').find_all('a', href=re.compile('/encyclopedia/anime'))
    print(f'Found {len(search_results)} results')

    if len(search_results):
        ANN_anime_url = urllib.parse.urljoin(
            'https://www.animenewsnetwork.com/',
            search_results[0].get('href')
        )
    else:
        ANN_anime_url = 'https://www.animenewsnetwork.com/encyclopedia/anime.php?id=UNKNOWN'

    #
    # AniList API
    #
    print('Querying AniList...')
    query = '''query ($id: Int, $page: Int, $perPage: Int, $search: String) {     Page (page: $page, perPage: $perPage) {         pageInfo {             total             currentPage             lastPage             hasNextPage             perPage          }         media (id: $id, search: $search) {             id             title {                 romaji              }          }      }  } '''
    variables = {'search': f'{anime_name}', 'page': 1, 'perPage': 5}

    search_response = searchRequestWrapper(requests.post, delay, url='https://graphql.anilist.co', json={'query': query, 'variables': variables})
    search_results = json.loads(search_response.text)['data']['Page']['media']
    print(f'Found {len(search_results)} results')

    if len(search_results):
        AniList_anime_url = urllib.parse.urljoin(
            'https://anilist.co/anime/',
            str(search_results[0]['id'])
        )
    else:
        AniList_anime_url = 'https://anilist.co/anime/UNKNOWN'

    meetings_yaml_template = f'''  - title: "{anime_name}"
    image: "{os.path.join(assets_dir_string, anime_image_filename)}"
    episodes: {anime_episodes}
    year: {anime_year}
    studio: "{anime_studios}"
    schedule: {schedule}
    info:
    - title: AL
      link: {AniList_anime_url}
    - title: MAL
      link: {anime_url}
    - title: ANN
      link: {ANN_anime_url}'''

    return(meetings_yaml_template)

if __name__ == '__main__':

    out_dir = './_output'
    out_schedule_shows_file = 'schedule.shows_only.yml'
    out_meetings_yaml_file = 'meetings.yml'
    #
    assets_dir_string = '/assets/images/anime/'
    # NOTE: use MAL anime names to increase probability of success
    shows = [
        Show('Main', 'Michaelmas 2019', 'Hinamatsuri'),
        Show('Main', 'Michaelmas 2019', 'SSSS. Gridman'),
        Show('Main', 'Michaelmas 2019', 'ACCA: 13-ku Kansatsu-ka'),
        Show('Main', 'Lent 2019', 'Humanity has Declined!'),
        Show('Main', 'Lent/Easter 2019', 'Shouwa Genroku Rakugo Shinjuu'),
        Show('Main', 'Lent 2019', 'Ookami to Koushinryou'),
        Show('Main', 'Easter 2019', 'Angel Beats!'),
        Show('Main', 'Easter 2019', 'Ookami to Koushinryou II'),
        Show('Sunday', 'Michaelmas 2019', 'Girls und Panzer'),
        Show('Sunday', 'Michaelmas 2019', 'Seishun Buta Yarou'),
        Show('Sunday', 'Michaelmas 2019', 'Gakkou Gurashi'),
        Show('Sunday', 'Lent 2019', 'Kekkai Sensen'),
        Show('Sunday', 'Lent 2019', 'Plastic Memories'),
        Show('Sunday', 'Easter 2019', 'Kekkai Sensen & Beyond'),
        Show('Sunday', 'Easter 2019', 'Granbelm'),
        Show('Bonus', 'Freshers\' Squash', 'Daicon Opening Animations'),
        Show('Bonus', 'Freshers\' Squash', 'Dareka no Manazashi'),
        Show('Bonus', 'Freshers\' Squash', 'Maquia'),
    ]

    os.makedirs(out_dir, exist_ok=True)
    os.chdir(out_dir)
    
    with open(out_schedule_shows_file, 'w') as f:
        f.write('     shows:\n')
        for show in shows:
            f.write(f'     - "{show.anime_name}"\n')

    blocks = []
    try:
        for show_type in TYPES:
            blocks.append(f'- type: {show_type}')
            for show in shows:
                if show.type == show_type:
                    print(f'--- Processing {show.anime_name} ---')
                    block = getAnimeYamlBlock(show.anime_name, assets_dir_string, show.schedule, delay=5)
                    print(block)
                    blocks.append(block)
    except KeyboardInterrupt:
        print("Aborted, writing results to file")

    with open(out_meetings_yaml_file, 'w') as f:
        f.write('\n'.join(blocks))
        print(f'Wrote blocks to {out_meetings_yaml_file}')
        
