
from datetime import datetime, timedelta
from pycin import search_events, ALLE, ALBA, logger
import logging


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
        .select(lambda e: e.attributes)
    )

    print(result)

    # Setting up logging to the console.
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    def list_movies(dates, cinemas):
        """Finds screening dates of 2d movies with the 
        word `marvel` in their title."""
        query = search_events(dates, cinemas)

        return list(
            query.filter(lambda e: '2d' in e.attributes and \
                            'marvel' in e.movie.name.lower())
            .select(lambda e: datetime.strftime(e.date, '%H:%M'))
        )

    list_movies([datetime.today()], [ALLE])
    result = list_movies([datetime.today()], [ALLE])

    print(result)


if __name__ == '__main__':
    main()
