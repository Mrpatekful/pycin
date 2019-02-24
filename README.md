# Python API for the Hungarian Cinema City

## Description

Each query has to originate from a `_CinemaQueryResult` object, which can be obtained by
either `fetch_cinemas()` or `fetch_common_cinemas()` method. The latter only lists the most popular cinemas of Budapest. By calling `_CinemaQueryResult.fetch_events()` the returned `_EventQueryResult` object contains the events of the cinames in that particular `_CinemaQueryResult` object. To obtain the cinemas or the events in the cinemas, call `_QueryResult.select()`. `_QueryResult.where()` method applies a filter on the object and returns a new one, based on a predicate function.

## Example usage

Fetching the available cinemas.

```python

from pycin import fetch_cinemas


cinemas = fetch_cinemas()

print(cinemas.select())
```

Output:

```
[Cinema(id='1124', name='Alba - Székesfehérvár'), Cinema(id='1133', name='Allee - Budapest'), Cinema(id='1132', name='Aréna - Budapest'), Cinema(id='1131', name='Balaton - Veszprém'), Cinema(id='1139', name='Campona - Budapest'), Cinema(id='1127', name='Debrecen'), Cinema(id='1141', name='Duna Pláza - Budapest'), Cinema(id='1125', name='Győr'), Cinema(id='1129', name='Miskolc'), Cinema(id='1143', name='Nyíregyháza'), Cinema(id='1128', name='Pécs'), Cinema(id='1134', name='Savaria - Szombathely'), Cinema(id='1136', name='Sopron'), Cinema(id='1126', name='Szeged'), Cinema(id='1130', name='Szolnok'), Cinema(id='1137', name='Westend - Budapest'), Cinema(id='1135', name='Zalaegerszeg')]
```

If there are no arguments provided for the `select()` method it returns the `_cinemas` field. The output of this function can be customized by feeding the name of the parameters of the `Cinema` namedtuple objects.

```python
print(cinemas.select('name'))
```

Output:

```
[('Alba - Székesfehérvár',), ('Allee - Budapest',), ('Aréna - Budapest',), ('Balaton - Veszprém',), ('Campona - Budapest',), ('Debrecen',), ('Duna Pláza - Budapest',), ('Győr',), ('Miskolc',), ('Nyíregyháza',), ('Pécs',), ('Savaria - Szombathely',), ('Sopron',), ('Szeged',), ('Szolnok',), ('Westend - Budapest',), ('Zalaegerszeg',)]
```

Fetching the events in the cinema *Alle*, where the screened movie is a horror.

```python

from pycin import ALLE

result = (
    cinemas.where(lambda c: c.id == ALLE.id)
        .fetch_events()
        .where(lambda e: 'horror' in e.movie.attributes)
        .movies
)

print(result)
```

Outputs:

```
[Movie(id='3208d2r', name='Boldog Halálnapot 2', attributes=['16-plus', '2d', 'dubbed', 'dubbed-lang-hu', 'horror', 'mystery', 'thriller'], length=100), Movie(id='3265d2r', name='A csodagyerek', attributes=['16-plus', '2d', 'dubbed', 'dubbed-lang-hu', 'horror', 'thriller'], length=92)]
```
