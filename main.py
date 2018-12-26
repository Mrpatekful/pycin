import requests
import json


def main():
    r = requests.get('https://www.cinemacity.hu/hu/data-api-service/v1/quickbook/10102/film-events/in-cinema/1124/at-date/2018-12-25?attr=&lang=hu_HU')
    titles = [film['name'] for film in json.loads(r.text)['body']['films']]
    print(titles)


if __name__ == '__main__':
    main()