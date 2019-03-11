
from datetime import datetime, timedelta
from pycin import search_events, ALLE, ALBA


def main():
    # Fetching events for today in Cinema City Alle and Alba.
    query = search_events([datetime.today()], [ALLE, ALBA])

    # Finding the exact time of movie screenings, which
    # have the id `3196o2r`.
    result = list(
        query.filter(lambda e: e.movie.id == '3196o2r')
        .select(lambda e: (e.date, e.cinema.name))
    )

    print(result)

    # Generating the days of next week.
    next_week = [datetime.today() + timedelta(d) for d in range(7)]

    query = search_events(next_week)

    result = set(
        query.filter(lambda e: e.date.hour > 20)
        .select(lambda e: e.movie.name)
    )

    print(result)


if __name__ == '__main__':
    main()
