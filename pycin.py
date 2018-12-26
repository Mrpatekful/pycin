"""

"""

import requests
import time
import json

from collections import namedtuple

from datetime import datetime
from dateutil.relativedelta import relativedelta


DATA_API_URL = 'https://www.cinemacity.hu/hu/' \
               'data-api-service/v1/quickbook/10102/'
DATE_FORMAT = '%Y-%m-%d'
EVENT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
DEFAULT_LANG = 'hu'


Movie = namedtuple('Movie', ['id', 'name', 'attributes', 'length'])
"""Namedtuple, holding the information of a movie.
:param id: str -- unique identifier.
:param name: str -- name(title) of the movie(film).
:param attributes: list -- list of string containing attribute keywords.
:param length: int -- length of the movie in minutes.
"""

Event = namedtuple('Event', ['id', 'booking_link',
                             'movie', 'cinema', 'date', 'sold_out'])
"""Namedtuple, holding the information of an event.
:param id: str -- unique identifier.
:param booking_link: str -- url for the booking link.
:param movie: Movie -- namedtuple object of the movie.
:param cinema: Cinema -- namedtuple object of the cinema.
:param date: datetime -- the date of the event.
:param sold_out: bool -- boolean signaling the availability of tickets.
"""

Cinema = namedtuple('Cinema', ['id', 'name'])
"""Namedtuple, holding the information of a cinema.
:param id: str -- unique identifier.
:param name: str -- name of the cinema.
"""

# common cinemas
ALLE = Cinema('1133', 'Allee - Budapest' )
ARENA = Cinema('1132', 'Aréna - Budapest' ) 
CAMPONA = Cinema('1139', 'Campona - Budapest')
WESTEND = Cinema('1137', 'Westend - Budapest')


class EventQuery:
    """Stores the query result for the events of a cinema."""

    def __init__(self, cinemas, movies, events):
        self._movies = movies
        self._events = events
        self._cinemas = cinemas

    def select_events(self, event_predicate=lambda event: True):
        events = [event for event in self._events if event_predicate(event)]
        movies, cinemas = {}, {}
        for event in events:
            movies[event.movie.id] = event.movie
            cinemas[event.cinema.id] = event.cinema
        return EventQuery(list(cinemas.values()), list(movies.values()), events)

    def movies(self, *attributes):
        if not attributes:
            return self._movies
        movies = []
        for movie in self._movies:
            movies.append(tuple(getattr(movie, attrib)
                                for attrib in attributes))

        return movies

    def cinemas(self, *attributes):
        if not attributes:
            return self._cinemas
        cinemas = []
        for cinema in self._cinemas:
            cinemas.append(tuple(getattr(cinema, attrib)
                                 for attrib in attributes))

        return cinemas
    
    def events(self, *attributes):
        if not attributes:
            return self._events
        events = []
        for event in self._events:
            events.append(tuple(getattr(event, attrib)
                                for attrib in attributes))

        return events
    

class CinemaQuery:

    def __init__(self, cinemas, lang=DEFAULT_LANG):
        self._lang = lang
        self._cinemas = cinemas

    def select_cinemas(self, cinema_predicate=lambda cinema: True):
        return CinemaQuery([c for c in self._cinemas
                            if cinema_predicate(c)], self._lang)
    
    def query_events(self, start_date, end_date=None):
        date = start_date
        end_date = end_date if end_date else date
        assert date <= end_date, 'start_date must be lesser' \
                                 ' or equal to end_date'
        movies = {}
        events = []

        while date <= end_date:
            for cinema in self._cinemas:
                date_string = datetime.strftime(date, DATE_FORMAT)
                request_url = '{url}/film-events/in-cinema/{cid}/' \
                              'at-date/{date}?attr=&lang={lang}'.format(
                               url=DATA_API_URL, cid=cinema.id,
                               date=date_string, lang=self._lang)
                response = requests.get(request_url)
                data = json.loads(response.text)['body']
                
                for movie in data['films']:
                    if movie['id'] not in movies:
                        movies[movie['id']] = Movie(movie['id'], movie['name'],
                                                    movie['attributeIds'],
                                                    movie['length'])
                
                for event in data['events']:
                    events.append(Event(
                        event['id'], event['bookingLink'],
                        movies[event['filmId']],
                        cinema, datetime.strptime(
                          event['eventDateTime'], EVENT_DATE_FORMAT),
                        event['soldOut']))

                time.sleep(0.2)

            date = date + relativedelta(days=1)
        return EventQuery(self._cinemas, list(movies.values()), events)

    def cinemas(self, *attributes):
        if not attributes:
            return self._cinemas
        cinemas = []
        for cinema in self._cinemas:
            cinemas.append(tuple(getattr(cinema, attrib)
                                 for attrib in attributes))
        return cinemas


def query_cinemas(lang=DEFAULT_LANG, until_date=None):
    if not until_date:
        until_date = datetime.fromtimestamp(
            time.mktime(time.localtime())) + relativedelta(years=1)

    until_date = datetime.strftime(until_date, DATE_FORMAT)

    assert lang in ('hu', 'en')
    lang = '{}_{}'.format(lang, lang.upper())
    request_url = '{url}cinemas/with-event/until/{until_date}' \
                  '?attr=&lang={lang}'.format(
                   url=DATA_API_URL, until_date=until_date, lang=lang)
    response = requests.get(request_url)
    data = json.loads(response.text)['body']['cinemas']
    cinemas = [Cinema(c['id'], c['displayName']) for c in data]
    return CinemaQuery(cinemas, lang)
