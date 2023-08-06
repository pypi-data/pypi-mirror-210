import os
import requests
import re
from bs4 import BeautifulSoup
from shttst.processing.audio_to_dataset import AudioToDatasetProcessor

def unique_list(array):
    return list(set(array))

def download_mp3(id, out_dir='/content/chomik') -> str:
    try:
        os.makedirs(out_dir, exist_ok=True)
        MP3_URL = f"https://chomikuj.pl/Audio.ashx?id={id}&type=2&tp=mp3"
        resp = requests.get(MP3_URL)

        file_path = os.path.join(out_dir, f'{id}.mp3')
        with open(file_path, 'w+b') as fs:
            fs.write(resp.content)

        return file_path
    except Exception as e:
        print(e)
        return None

def get_all_dirs(url, only_sub_url=True):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    results = soup.find(id="TreeContainer")
    results = results.find_all('a')
    results = unique_list([f"https://chomikuj.pl{r['href']}" for r in results])
    if only_sub_url:
        results = list(filter(lambda x: x.startswith(url), results))
    return results

def get_dir_pages(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")

    number_of_pages = 1
    result = soup.find(id="galleryView")
    if result:
        result = result.find('div', class_='paginator')
        if result:
            number_of_pages = max([int(r.text) for r in result.find('ul').find_all('li')])
    else:
        result = soup.find(id="listView")
        if result:
            result = result.find('div', class_='paginator')
            if result:
                number_of_pages = max([int(r.text) for r in result.find('ul').find_all('li')])

    return number_of_pages

def get_page_mp3s(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    result = soup.find(id="galleryView")
    if not result:
        result = soup.find(id="listView")
    if result:
        audios = result.find_all('a', class_='downloadAction')
        
        return(unique_list([re.search(r'\d{10}', r['href']).group() for r in audios if '.mp3' in r['href']]))
    
    return []

def get_folder_id(url) -> str:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup.find('input', {'name': 'folderId'}).attrs['value']

def download_chomik_dir(url: str, out_dir='/content/chomik'):
    folder_id = get_folder_id(url)
    max_pages = get_dir_pages(url)
    for i in range(max_pages):
        mp3s = get_page_mp3s(f'{url},{i+1}')
        for mp3 in mp3s:
            download_mp3(mp3, os.path.join(out_dir, folder_id, 'wavs'))

def download_all_chomik_dirs(url: str, out_dir='/content/chomik'):
    chomik_dirs = get_all_dirs(url)
    for dir in chomik_dirs:
        download_chomik_dir(dir, out_dir)

def create_dataset_from_chomik_dir(url: str, keep_not_fine=False, denoise_all=False, use_classifier=True, out_dir='/content/chomik', vad_min_silence=1000, vad_max_duration=14, total_size_per_dir=1024 * 1024 * 50):
    folder_id = get_folder_id(url)
    book_dir = os.path.join(out_dir, folder_id)
    if os.path.exists(book_dir):
        return
    
    processor = AudioToDatasetProcessor(keep_not_fine, denoise_all, use_classifier)
    mp3s = get_page_mp3s(url)
    total_size = 0
    for mp3 in mp3s:
        if total_size >= total_size_per_dir:
            break
        path = download_mp3(mp3, os.path.join(book_dir, 'wavs'))
        total_size += os.path.getsize(path)
        if path:
            processor(path, vad_min_silence=vad_min_silence, vad_max_duration=vad_max_duration)
        


if __name__ == '__main__':
    # URL = "https://chomikuj.pl/JuRiWlO/Audiobooki/"
    URL = 'https://chomikuj.pl/piotrbobisz/!Ostatnio+Dodane!/Audiobooki'
    for dir in get_all_dirs(URL):
        create_dataset_from_chomik_dir(dir)





