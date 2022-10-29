import random
import requests
import re
import json
from bs4 import BeautifulSoup

from models.response import SearchImage
from models.request import PaginationArgs


class ImageSearchController:

    __SEARCH_URL = 'https://www.google.com/search'
    __user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1'
    ]

    # TODO: complete pagination
    @staticmethod
    def get_searched_images(search: str, pagination_args: PaginationArgs):
        params = {
            "q": search,                  # search query
            "tbm": "isch",                # image results
            "hl": "en",                   # language of the search
            "gl": "us",                   # country where search comes from
        }
        headers = {
            "User-Agent": random.choice(ImageSearchController.__user_agents)
        }

        html = requests.get(ImageSearchController.__SEARCH_URL,
                            params=params, headers=headers, timeout=2)
        soup = BeautifulSoup(html.text, "lxml")

        google_images = []

        all_script_tags = soup.select("script")

        # # https://regex101.com/r/48UZhY/4
        matched_images_data = "".join(re.findall(
            r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

        matched_images_data_fix = json.dumps(matched_images_data)
        matched_images_data_json = json.loads(matched_images_data_fix)

        # https://regex101.com/r/VPz7f2/1
        matched_google_image_data = re.findall(
            r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)

        # removing previously matched thumbnails for easier full resolution image matches.
        removed_matched_google_images_thumbnails = re.sub(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))

        # https://regex101.com/r/fXjfb1/4
        # https://stackoverflow.com/a/19821774/15164646
        # TODO: perform pagination
        matched_google_full_resolution_images = re.findall(
            r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)

        full_res_images = [
            bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for img in matched_google_full_resolution_images
        ]

        for original in full_res_images:
            google_images.append(SearchImage(original))

        return {'search': search, 'result': google_images}
