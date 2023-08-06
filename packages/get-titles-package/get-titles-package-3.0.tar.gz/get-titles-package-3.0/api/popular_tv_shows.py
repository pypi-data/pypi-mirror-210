import requests
from processing.title_processing import get_movie_title


class TVShowTitleFetcher:
    def __init__(self):
        self.url = "https://imdb8.p.rapidapi.com/title/get-most-popular-tv-shows"
        self.querystring = {"homeCountry": "US", "purchaseCountry": "US", "currentCountry": "US"}
        self.headers = {
            "X-RapidAPI-Key": "747d924829msh0b2f964c759cd82p18430ejsnafe54fbde2a6",
            "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }
        self.api_response = None

    def fetch_tv_show_titles(self, limit):
        response = requests.get(self.url, headers=self.headers, params=self.querystring)
        self.api_response = response.json()

        count = 0
        for tv_show_id in self.api_response:
            if count >= limit:
                break

            tv_show_id = tv_show_id.strip('/title/')
            tv_show_id = "tt" + tv_show_id
            title = get_movie_title(tv_show_id)
            count += 1



