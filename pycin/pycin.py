"""
@author:    Patrik Purgai
@copyright: Copyright 2019, pycin
@license:   MIT
@email:     purgai.patrik@gmail.com
@date:      2019.02.24.
"""

import requests
import time
import json
import logging

from collections import Iterable, namedtuple
from functools import lru_cache, wraps
from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'
EVENT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
UNTIL_DATE = '2020-12-31'

# Available languages are `en_GB` or `hu_HU`
LANGUAGE = 'en_GB'

DATA_API_URL = 'https://www.cinemacity.hu/en/data-api-service/v1/quickbook/10102/'
EVENT_URL = '{data_api_url}film-events/in-cinema/{id}/at-date/{date}?attr=&lang={lang}'
CINEMA_URL = '{data_api_url}cinemas/with-event/until/{until_date}?attr=&lang={lang}'


Movie = namedtuple('Movie', ['id', 'name', 'attributes', 'length'])
"""Namedtuple, holding the information of a movie.
:param id: str -- unique identifier.
:param name: str -- name(title) of the movie(film).
:param attributes: list -- list of string containing attribute keywords.
:param length: int -- length of the movie in minutes.
"""

Event = namedtuple('Event', ['id', 'booking_link', 'movie', 'cinema',
                             'date', 'sold_out', 'attributes'])
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

ALBA = Cinema('1124', 'Alba - Székesfehérvár')
ALLE = Cinema('1133', 'Allee - Budapest')
ARENA = Cinema('1132', 'Aréna - Budapest')
BALATON = Cinema('1131', 'Balaton - Veszprém')
CAMPONA = Cinema('1139', 'Campona - Budapest')
DEBRECEN = Cinema('1127', 'Debrecen')
DUNA_PLAZA = Cinema('1141', 'Duna Pláza - Budapest')
GYOR = Cinema('1125', 'Győr')
MISKOLC = Cinema('1129', 'Miskolc')
NYIREGYHAZA = Cinema('1143', 'Nyíregyháza')
PECS = Cinema('1128', 'Pécs')
SAVARIA = Cinema('1134', 'Savaria - Szombathely')
SOPRON = Cinema('1136', 'Sopron')
SZEGED = Cinema('1126', 'Szeged')
SZOLNOK = Cinema('1130', 'Szolnok')
WESTEND = Cinema('1137', 'Westend - Budapest')
ZALAEGERSZEG = Cinema('1135', 'Zalaegerszeg')


CINEMAS = [
    ALBA, ALLE, ARENA, BALATON, CAMPONA, DEBRECEN,
    DUNA_PLAZA, GYOR, MISKOLC, NYIREGYHAZA, PECS, SAVARIA,
    SOPRON, SZEGED, SZOLNOK, WESTEND, ZALAEGERSZEG
]


BUDAPEST_CINEMAS = [
    ALLE, ARENA, CAMPONA, DUNA_PLAZA, WESTEND
]


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def logged(func):
    """Wraps a function and logs its process"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logger.debug('Query finished in {:.4f}s.'.format(time.time() - start))
        return result
    return wrapped


def fetch_events(dates, cinemas=BUDAPEST_CINEMAS):
    """Fetches the events, which are held in the provided
    cinemas on the provided dates. The events are requested from
    the CinemaCity API through the `DATA_API_URL` `EVENT_URL`.
    Note, that this function may take several seconds since it
    accesses the data endpoint `len(dates) * len(cinemas)` times.

    Arguments:
        cinemas: Iterable, containing `Cinema` type namedtuple
            objects, for which the events will be fetched.
        dates: Iterable, containing datetime objects, which are
            the dates of the requested events.

    Returns:
        Query object, that holds the requested events.
    """
    assert isinstance(cinemas, Iterable), 'Cinemas must be an `Iterable`.'
    assert isinstance(dates, Iterable), 'Dates must be an `Iterable`.'

    dates = {datetime.strftime(d, DATE_FORMAT) for d in dates}

    movies, events = {}, {}

    for cinema in cinemas:
        for date in dates:
            raw_movies, raw_events = fetch_raw_events(
                cinema, date)

            for movie in raw_movies:
                if movie['id'] not in movies:
                    movies[movie['id']] = create_movie(**movie)

            for event in raw_events:
                events[event['id']] = create_event(
                    movie=movies[event['filmId']],
                    cinema=cinema,
                    **event)

    return Query(e for e in events.values())


def fetch_cinemas(predicate=lambda cinema: True):
    """Fetches the cinemas from the CinemaCity API through
    the `DATA_API_URL` `CINEMA_URL`.

    Arguments:
        predicate: an optional predicate function for filtering
            the returned cinemas. By default all cinemas are listed.

    Returns:
        list of the available cinemas.
    """
    cinemas = (
        create_cinema(**cinema) for
        cinema in fetch_raw_cinemas(UNTIL_DATE)
    )

    return [cinema for cinema in cinemas if predicate(cinema)]


def create_event(**parameters):
    """Convenience method for creating `Event` object."""
    return Event(
        id=parameters['id'],
        movie=parameters['movie'],
        cinema=parameters['cinema'],
        date=datetime.strptime(
            parameters['eventDateTime'], EVENT_DATE_FORMAT),
        sold_out=parameters['soldOut'],
        booking_link=parameters['bookingLink'],
        attributes=tuple(parameters['attributeIds']))


def create_movie(**parameters):
    """Convenience method for creating `Movie` object."""
    return Movie(
        id=parameters['id'],
        name=parameters['name'],
        attributes=tuple(parameters['attributeIds']),
        length=parameters['length'])


def create_cinema(**parameters):
    """Convenience method for creating `Cinema` object."""
    return Cinema(
        id=parameters['id'],
        name=parameters['displayName'])


@logged
@lru_cache(maxsize=128)
def fetch_raw_events(cinema, date):
    """Fetches the event data from the CinemaCity data API.
    The results are cached with lru_caching.

    Arguments:
        cinema: a `Cinema` type namedtuple object.
        date: str, a date formated according to `DATE_FORMAT`
            constant.

    Returns:
        The fetched data of films and events in a tuple of
        dictionaries.
    """
    response = requests.get(EVENT_URL.format(
        data_api_url=DATA_API_URL, id=cinema.id,
        date=date, lang=LANGUAGE))

    data = json.loads(response.text)['body']

    time.sleep(0.1)

    return data['films'], data['events']


@logged
@lru_cache(maxsize=1)
def fetch_raw_cinemas(until_date):
    """Fetches the cinema data from the CinemaCity data API.

    Arguments:
        until_date: str, a date that is formatted, described
            by the `DATE_FORMAT`.

    Returns:
        The fetched data of films and events in a tuple of
        dictionaries.
    """
    response = requests.get(CINEMA_URL.format(
        data_api_url=DATA_API_URL, until_date=until_date,
        lang=LANGUAGE))

    data = json.loads(response.text)['body']

    time.sleep(0.1)

    return data['cinemas']


class Query:

    def __init__(self, events):
        self._events = events

    def filter(self, predicate=lambda event: True):
        """Selects the subset of the querried elements, 
        based on the provided predicate function.

        Arguments:
            predicate: function, that returns bool value.
        """
        return Query(e for e in self._events if predicate(e))

    def select(self, selector=lambda event: event):
        """Lists the event attribute values, which are selected 
        vy the selector funciton.

        Arguments:
            selector: a function that receives an event type and
                returns a value. 

        Returns:
            An iterable that contains the output values of the
            selector funciton for each element of the `events`
            list.
        """
        return (selector(e) for e in self._events)
