import requests
import json

from pycin import fetch_common_cinemas, today, add_days, ALLE


def main():
    # r = requests.get('https://www.cinemacity.hu/hu/data-api-service/v1/quickbook/10102/film-events/in-cinema/1124/at-date/2019-02-25?attr=&lang=hu_HU')
    # titles = [film['name'] for film in json.loads(r.text)['body']['films']]
    cinemas = fetch_common_cinemas()
    print(cinemas.where(lambda c: c.id == ALLE.id).fetch_events().where(lambda e: 'horror' in e.movie.attributes).movies)


if __name__ == '__main__':
    main()
