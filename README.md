# Python API for the Hungarian Cinema City

## Description

This framework provides a Python interface for the CinemaCity data API. To fetch location or date data of the screenings, call `search_events(cinemas, dates)` with the required cinemas and dates. The possible cinemas are wrapped into a `Cinema` namedtuple object, and are available as constants in the package (e.g. `ALLE` or `DUNA_PLAZA`). The dates have to be provided as datetime objects. By executing the `search_events` query, the returned object is a `Query`, that holds the available events. These events are stored as an iterable inside the `Query` object. To search for an event with a specific attribute (e.g. an event with a particular movie) the `filter()` method should be used. This method has an optional parameter, which is a function, that serves as a predicate to filter the events. Note that the return value of this function is another `Query` object, thus the method can be chained. To retrieve a specific field from the event, use the `select()` method, which also accepts a function as a parameter and maps this function to the contained iterator. The returned list is the output of this method for each event element.

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

Fetching the events in the cinema *Alle*, where the screened movie is a horror.

```python

query = search_events()

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
