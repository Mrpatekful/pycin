# Python API for the Hungarian Cinema City

This framework provides a Python interface for the Cinema City data API. Events at a specific time and location can be querried from the API by calling `fetch_events([dates], [locations])`. The data from the query is stored as an iterable of nested DTOs, which are the following. **`Cinema`** object with `id` *( `str`, the unique identifier of a venue. )* and `name` *( `str`, the name of a venue. )* attributes. **`Movie`** object with `id` *( `str`, the unique identifier of a movie. )*, `name` *( `str`, the name of a venue. )*, `attributes` *( `tuple`, movie specific information like dubbing or 3D. )* and `length` *( `int`, length of the movie in minutes. )*. **`Event`** object with `id` *( `str`, the unique identifier of an event. )*, `date` *( `datetime`, begining time of the movie screening. )*, `booking_link` *( `str`, url of the ticket booking link. )*, `sold_out` *( `bool`, availability of tickets. )*, `movie` *( `Movie`, the screened movie, stored as a `Movie` object. )*, `cinema` *( `Cinema`, the location of the event, stored as a `Cinema` object. )* and `attributes` *( `tuple`, movie specific information like dubbing or 3D. )*.

## Usage

Installing the package is straightforward with pip directly from this git repository or from pypi with either of the following commands.

```bash
pip install git+https://github.com/Mrpatekful/pycin
```

```bash
pip install pycin
```

Altough the package contains all of the existing cinema location as Cinema DTO constants, this information may be outdated. The `fetch_cinemas` method always returns up-to-date cinema data.

```python
from pycin import fetch_cinemas

cinemas = fetch_cinemas()

print(cinemas)
```

```text
[Cinema(id='1124', name='Alba - Székesfehérvár'), Cinema(id='1133', name='Allee - Budapest'), Cinema(id='1132', name='Aréna - Budapest'), Cinema(id='1131', name='Balaton - Veszprém'), Cinema(id='1139', name='Campona - Budapest'), Cinema(id='1127', name='Debrecen'), Cinema(id='1141', name='Duna Pláza - Budapest'), Cinema(id='1125', name='Győr'), Cinema(id='1129', name='Miskolc'), Cinema(id='1143', name='Nyíregyháza'), Cinema(id='1128', name='Pécs'), Cinema(id='1134', name='Savaria - Szombathely'), Cinema(id='1136', name='Sopron'), Cinema(id='1126', name='Szeged'), Cinema(id='1130', name='Szolnok'), Cinema(id='1137', name='Westend - Budapest'), Cinema(id='1135', name='Zalaegerszeg')]
```

Fetching events in cinema *Alle*, *Westend*, where the screened movie has the id *3196o2r*.

```python
from datetime import datetime
from pycin import fetch_events, ALLE, WESTEND

query = fetch_events([datetime.today()], [ALLE, WESTEND])

result = list(
    query.filter(lambda e: e.movie.id == '3196o2r')
    .select(lambda e: (e.date, e.cinema.name))
)

print(result)
```

```text
[(datetime.datetime(2019, 2, 28, 17, 40), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 19, 50), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 22, 0), 'Allee - Budapest'), (datetime.datetime(2019, 2, 28, 17, 20), 'Alba - Székesfehérvár'), (datetime.datetime(2019, 2, 28, 19, 30), 'Alba - Székesfehérvár')]
```

Finding the unique set of movies, which are played after 8:00 PM on the next week at any Cinema City in Budapest (because default location for `fetch_events` is `BUDAPEST_CINEMAS`).

```python
from pycin import fetch_events
from datetime import datetime, timedelta

next_week = [datetime.today() + timedelta(d) for d in range(7)]

query = fetch_events(next_week)

result = set(
    query.filter(lambda e: e.date.hour > 20)
    .select(lambda e: e.movie.name)
)

print(result)
```

```text
{'Kölcsönlakás', 'Cold Pursuit', 'Happy DeathDay 2U', 'Instant Family', 'Heavy Trip (Hevi Reissu)', 'Sink or Swim (Le grand bain)', 'Alita: Battle Angel', 'Most van most', 'En Liberté (The Trouble with You)', 'Bohemian Rhapsody', 'Vice', 'Apró mesék', 'Green Book', 'Drunk Parents', 'The Prodigy', 'Captain Marvel', 'Glass', 'Fighting with My Family'}
```

The `search_events` may take longer to execute on the first call, but the results are cached, thus making subsequent calls yield results instantaneously.

```python
import logging
from datetime import datetime
from pycin import fetch_events

# Setting up logging to the console.
console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def list_dates(dates, cinemas):
    """Finds screening dates of 2d movies with the
    word `marvel` in their title."""
    query = fetch_events(dates, cinemas)

    return list(
        query.filter(lambda e: '2d' in e.attributes and \
                        'marvel' in e.movie.name.lower())
        .select(lambda e: datetime.strftime(e.date, '%H:%M'))
    )

list_dates([datetime.today()], [ALLE])
# second call is instantaneous because of cached results
result = list_dates([datetime.today()], [ALLE])

print(result)
```

```text
2019-03-12 11:38:16,454 - DEBUG - Query finished in 0.9281s.
2019-03-12 11:38:16,466 - DEBUG - Query finished in 0.0000s.
['13:20', '16:00', '16:50', '18:40', '19:30', '21:20', '22:10']
```
