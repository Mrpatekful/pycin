
from datetime import datetime
from pycin.pycin import search_events, ALLE, ALBA


def main():
    query = search_events([datetime.today()], [ALLE, ALBA])

    result = list(
        query.filter(lambda e: e.movie.id == '3196o2r')
        .select(lambda e: (e.date, e.cinema.name))
    )

    print(result)


if __name__ == '__main__':
    main()
