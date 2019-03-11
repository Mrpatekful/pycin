# Python API for the Hungarian Cinema City

## Description

This framework provides a Python interface for the CinemaCity data API. To fetch location or date data of the screenings, call `search_events(cinemas, dates)` with the required cinemas and dates. The possible cinemas are wrapped into a `Cinema` namedtuple object, and are available as constants in the package (e.g. `ALLE` or `DUNA_PLAZA`). The dates have to be provided as datetime objects. By executing the `search_events` query, the returned object is a `Query`, that holds the available events. These events are stored as an iterable inside the `Query` object. To search for an event with a specific attribute (e.g. an event with a particular movie) the `filter()` method should be used. This method has an optional parameter, which is a function, that serves as a predicate to filter the events. Note that the return value of this function is another `Query` object, thus the method can be chained. To retrieve a specific field from the event, use the `select()` method, which also accepts a function as a parameter and maps this function to the contained iterator. The returned list is the output of this method for each event element.

### Entities

`Cinema` is the representation of a Cinema City location like *Cinema City Alle*. This entity has an `id` and `name` fields.
`Movie` refers to a movie which can be screened at multiple cinemas on multiple events. It has a unique `id` field, a `name` that is the movie title. The `attributes` field contains movie specific information like dubbing or 3D. `length` field stores the movie's length in minutes.
`Event` also has a unique `id` field and several supplementary fields like `booking_link` and `sold_out`. The `date` field is a Python `datetime` object, which stores the begining time of the movie screening. The `movie` and `cinema` fields hold the location of the movie screening as a `Cinema` type object and the screened movie as a `Movie` type object.

## Example usage

Fetching the available cinemas.

```python

from pycin import fetch_cinemas


cinemas = fetch_cinemas()

print(cinemas)
```

Output:

```
[Cinema(id='1124', name='Alba - Székesfehérvár'), Cinema(id='1133', name='Allee - Budapest'), Cinema(id='1132', name='Aréna - Budapest'), Cinema(id='1131', name='Balaton - Veszprém'), Cinema(id='1139', name='Campona - Budapest'), Cinema(id='1127', name='Debrecen'), Cinema(id='1141', name='Duna Pláza - Budapest'), Cinema(id='1125', name='Győr'), Cinema(id='1129', name='Miskolc'), Cinema(id='1143', name='Nyíregyháza'), Cinema(id='1128', name='Pécs'), Cinema(id='1134', name='Savaria - Szombathely'), Cinema(id='1136', name='Sopron'), Cinema(id='1126', name='Szeged'), Cinema(id='1130', name='Szolnok'), Cinema(id='1137', name='Westend - Budapest'), Cinema(id='1135', name='Zalaegerszeg')]
```

Fetching the events in the cinema *Alle*, *Westend*, where the screened movie has the id *3196o2r*.

```python

from datetime import datetime
from pycin import ALLE, WESTEND

query = search_events([datetime.today()], [ALLE, WESTEND])

result = list(
    query.filter(lambda e: e.movie.id == '3196o2r')
    .select(lambda e: (e.date, e.cinema.name))
)

print(result)
```

Output:

```
[(datetime.datetime(2019, 2, 28, 17, 40), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 19, 50), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 22, 0), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 17, 20), 'Alba - Székesfehérvár'), (datetime.datetime(2019, 2, 28, 19, 30), 'Alba - Székesfehérvár')]
```

Finding the unique set of movies, which are played after 8:00 PM on the next week at any Cinema City in Budapest (because default location is `BUDAPEST_CINEMAS`).

```python

from datetime import timedelta

next_week = [datetime.today() + timedelta(d) for d in range(7)]

query = search_events(next_week)

result = set(
    query.filter(lambda e: e.date.hour > 20)
    .select(lambda e: e.movie.name)
)

print(result)
```

```
{'Kölcsönlakás', 'Cold Pursuit', 'Happy DeathDay 2U', 'Instant Family', 'Heavy Trip (Hevi Reissu)', 'Sink or Swim (Le grand bain)', 'Alita: Battle Angel', 'Most van most', 'En Liberté (The Trouble with You)', 'Bohemian Rhapsody', 'Vice', 'Apró mesék', 'Green Book', 'Drunk Parents', 'The Prodigy', 'Captain Marvel', 'Glass', 'Fighting with My Family'}
```