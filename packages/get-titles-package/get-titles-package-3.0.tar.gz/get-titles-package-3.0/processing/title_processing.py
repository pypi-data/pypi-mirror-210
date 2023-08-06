import requests


def get_movie_title(movie_id):
    url = "https://imdb8.p.rapidapi.com/title/get-details"

    querystring = {
        "tconst": movie_id
    }

    headers = {
        "X-RapidAPI-Key": "747d924829msh0b2f964c759cd82p18430ejsnafe54fbde2a6",
        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    if "title" in data:
        title = data["title"]
        print("Name:", title)
    else:
        print("Failed to retrieve movie title.")
