import csv
import json

import requests

from recommender import Recommender

movies_dict = {}
movies_dict_en = {}

# csv class
# extract csv
with open('movie_opinions.csv', newline = '', encoding = 'utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter = ';', quotechar = '"')
    # transform csv
    for row in csv_reader:
        person = row[0]
        row.pop(0)
        # transform to json
        movies_dict[person] = {row[i]: float(row[i + 1]) for i in range(0, len(row), 2) if row[i] != ''}
        # print(json.dumps(movies_dict, indent=2))

    csv_file.close()

headers = {"x-locale": "pl_PL", "content-type": "application/json"}
# load csv
for key in movies_dict:
    movies_dict_en[key] = {}
    for movie_title, score in movies_dict[key].items():
        movie_title_url_encoded = requests.utils.quote(movie_title)
        req_movie_search = requests.get("https://www.filmweb.pl/api/v1/live/search?query="
                                        + movie_title_url_encoded + "&pageSize=1", headers = headers)
        resp_movie_search = req_movie_search.json()
        movie_id = resp_movie_search["searchHits"][0]["id"]
        print(movie_id)
        req_movie_info = requests.get('https://www.filmweb.pl/api/v1/title/' + str(movie_id) + '/info',
                                      headers = headers)
        resp_movie_info = req_movie_info.json()
        print(resp_movie_info)
        if "originalTitle" in resp_movie_info:
            movies_dict_en[key].update({resp_movie_info["originalTitle"]: score})
        else:
            movies_dict_en[key].update({resp_movie_info["title"]: score})

with open('movie_opinions_unified.json', 'w', encoding = 'utf-8-sig') as json_file:
    json_file.write(json.dumps(movies_dict_en, indent = 2, ensure_ascii = False))

    json_file.close()

print(json.dumps(movies_dict_en, indent = 2))

# USE THIS TO USE ALREADY EXISITNG JSON FILE
# with open('movie_opinions_unified.json', 'r', encoding = 'utf-8-sig') as json_file:
#     movies_dict_en = json.load(json_file)

# Calculating distance scores
recommender = Recommender(movies_dict_en)
distance_scores = recommender.calculate_distance_score()

# Writing distance scores to file
with open('distance_scores.json', 'w', encoding = 'utf-8-sig') as distance_file:
    distance_file.write(json.dumps(distance_scores, indent = 2, ensure_ascii = False))

print(json.dumps(distance_scores, indent = 2, ensure_ascii = False))
