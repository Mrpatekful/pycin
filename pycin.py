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

from collections import namedtuple

from datetime import datetime
from dateutil.relativedelta import relativedelta


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

DATA_API_URL = 'https://www.cinemacity.hu/hu/' \
               'data-api-service/v1/quickbook/10102/'
DATE_FORMAT = '%Y-%m-%d'
EVENT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
DEFAULT_LANG = 'en'


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


def today():
    """Convenience function for getting the current
    date in datetime format."""
    return datetime.fromtimestamp(time.mktime(time.localtime()))


def add_days(date, days):
    """Convenience function for adding days to a datetime object."""
    return date + relativedelta(days=days)


def fetch_common_cinemas(lang=DEFAULT_LANG):
    """Convenience function for fetching the most common cinemas."""
    return _CinemaQueryResult([ALLE, ARENA, CAMPONA, WESTEND], lang)


def create_cinema_query(cinema, lang=DEFAULT_LANG):
    """Convenience function for fcreating a query with known cinemas."""
    if not isinstance(cinema, list):
        cinema = [cinema]
    return _CinemaQueryResult(cinema, lang)


class _QueryResult:

    def where(self, predicate):
        """Selects the subset of the querried elements, 
        based on the provided predicate function.
        
        Arguments:
            predicate: function, that returns bool value.
        """
        raise NotImplementedError('Subclasses must implement this.')

    def select(self, *attributes):
        """Lists the event attribute values, which are present 
        in the query.
        
        Arguments:
            attributes: name of the namedtuple attributes,
                which are returned in the list. Defaults to all
                attributes.

        Returns:
            A list of tuples, which are the values of the `Event`
            namedtuple attributes. If the `attributes` parameter
            is provided, the order of the values in the tuples is
            the same as the provided attributes names. By default
            the namedtuple objects are returned.
        """
        raise NotImplementedError('Subclasses must implement this.')


class _EventQueryResult(_QueryResult):
    """Stores the query result for the events of a cinema."""

    def __init__(self, cinemas, movies, events):
        """Creates and _EventQueryResult object.
        
        Arguments:
            cinemas: a list of `Cinema` namedtuple objects, 
                which are present in the events.
            movies: a list of `Movie` namedtuple objects,
                which are present in the events.
            events: a list of `Event` namedtuple objects.
        """
        self._movies = movies
        self._events = events
        self._cinemas = cinemas

    def where(self, predicate=lambda event: True):
        """Creates a new `_EventQueryResult` object from the cinemas,
        which are seleceted by the predicate function.
        
        Arguments:
            predicate: function, that receives a `Event` 
                namedtuple object and returns a bool value.
        
        Returns:
            The new `_EventQueryResult` object with the selected
            events.
        """
        events = [e for e in self._events if predicate(e)]
        movies, cinemas = {}, {}
        for event in events:
            movies[event.movie.id] = event.movie
            cinemas[event.cinema.id] = event.cinema
        return _EventQueryResult(
            list(cinemas.values()), list(movies.values()), events)

    def select(self, *attributes):
        """Lists the event attribute values, which are present 
        in the query.
        
        Arguments:
            attributes: name of the `Event` namedtuple attributes,
                which are returned in the list. Defaults to all
                attributes.

        Returns:
            A list of tuples, which are the values of the `Event`
            namedtuple attributes. If the `attributes` parameter
            is provided, the order of the values in the tuples is
            the same as the provided attributes names. By default
            the namedtuple objects are returned.
        """
        if not attributes:
            return self._events
        try:
            res = [
                tuple(getattr(ev, attr) for attr in attributes)
                for ev in self._events
            ]
        except AttributeError as e:
            msg = '{msg}. Available attributes are {attribs}'.format(
                msg=e, attribs=','.join(Event._fields))
            raise AttributeError(msg)

        return res

    @property
    def movies(self):
        return self._movies

    @property
    def cinemas(self):
        return self._cinemas
    

class _CinemaQueryResult(_QueryResult):
    """Stores the query result for the cinemas."""

    def __init__(self, cinemas, lang=DEFAULT_LANG):
        """Creates a cinema query object.
        
        Arguments:
            cinemas: list, containg the 
        """
        self._lang = lang
        self._cinemas = cinemas

    def where(self, predicate=lambda cinema: True):
        """Creates a new `_CinemaQueryResult` object from the cinemas,
        which are seleceted by the predicate function.
        
        Arguments:
            predicate: function, that receives a `Cinema` 
                namedtuple object and returns a bool value.
        
        Returns:
            The new `_CinemaQueryResult` object with the selected
            cinemas.
        """
        return _CinemaQueryResult([c for c in self._cinemas
                            if predicate(c)], self._lang)
    
    def select(self, *attributes):
        """Lists the cinema attribute values, which are present 
        in the query.
        
        Arguments:
            attributes: name of the `Cinema` namedtuple attributes,
                which are returned in the list. Defaults to all
                attributes.
        
        Returns:
            A list of tuples, which are the values of the `Cinema`
            namedtuple attributes. If the `attributes` parameter
            is provided, the order of the values in the tuples is
            the same as the provided attributes names. By default
            the namedtuple objects are returned.
        """
        if not attributes:
            return self._cinemas
        try:
            res = [
                tuple(getattr(cin, attr) for attr in attributes)
                for cin in self._cinemas
            ]
        except AttributeError as e:
            msg = '{msg}. Available attributes are {attribs}'.format(
                msg=e, attribs=','.join(Cinema._fields))
            raise AttributeError(msg)

        return res

    def fetch_events(self, start_date=None, end_date=None):
        """Queries the events for the cinemas, which are present
        in the `_CinemaQueryResult` object.
        
        Arguments:
            start_date: datetime object, that marks the beginning
                of the time interval for the querried event dates.
                Defaults to today.
            end_date: datetime object, which is the end of the time
                interval for the events in the query.

        Returns:
            `_EventQueryResult` type objects, that holds the requested events.
        """
        if start_date is None:
            start_date = today()
        date = start_date
        end_date = end_date if end_date else date
        assert date <= end_date, 'start_date must be lesser' \
                                    ' or equal to end_date'
        movies = {}
        events = []

        while date <= end_date:
            for cinema in self._cinemas:
                date_string = datetime.strftime(date, DATE_FORMAT)

                logger.info('Fetching events for {id} on {date}.'.format(
                    id=cinema.id, date=date_string))

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

        logger.info('Event query created with {size} elements.'.format(
            size=len(events)))
        
        return _EventQueryResult(
            self._cinemas, list(movies.values()), events)


def fetch_cinemas(lang=DEFAULT_LANG, until_date=None):
    """Queries the Cinema City cinemas.
    
    Arguments:
        lang: str, language of the query result. Can be `en` or `hu`.
    
    Returns:
        `_CinemaQueryResult` type object, which holds the querried cinemas.
    """
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

    logger.info('Cinema query created with {size} elements.'.format(
        size=len(cinemas)))

    return _CinemaQueryResult(cinemas, lang)
