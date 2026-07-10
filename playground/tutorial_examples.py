TUTORIAL_EXAMPLES = [
    {
        "title": "2.5 Querying",
        "url": "https://www.postgresql.org/docs/current/tutorial-select.html",
        "query": "SELECT * FROM weather",
    },
    {
        "title": "2.5 Expressions",
        "url": "https://www.postgresql.org/docs/current/tutorial-select.html",
        "query": "SELECT city, (temp_hi + temp_lo) / 2 AS temp_avg, date FROM weather",
    },
    {
        "title": "2.6 Joins",
        "url": "https://www.postgresql.org/docs/current/tutorial-join.html",
        "query": (
            "SELECT city, temp_lo, temp_hi, prcp, date, location "
            "FROM weather JOIN cities ON city = name"
        ),
    },
    {
        "title": "2.6 Outer joins",
        "url": "https://www.postgresql.org/docs/current/tutorial-join.html",
        "query": (
            "SELECT * FROM weather "
            "LEFT OUTER JOIN cities ON weather.city = cities.name"
        ),
    },
    {
        "title": "2.7 Aggregates",
        "url": "https://www.postgresql.org/docs/current/tutorial-agg.html",
        "query": "SELECT city, count(*), max(temp_lo) FROM weather GROUP BY city",
    },
    {
        "title": "3.2 Views",
        "url": "https://www.postgresql.org/docs/current/tutorial-views.html",
        "query": "SELECT * FROM myview",
    },
    {
        "title": "3.5 Window functions",
        "url": "https://www.postgresql.org/docs/current/tutorial-window.html",
        "query": (
            "SELECT depname, empno, salary, "
            "avg(salary) OVER (PARTITION BY depname) "
            "FROM empsalary"
        ),
    },
    {
        "title": "3.6 Inheritance",
        "url": "https://www.postgresql.org/docs/current/tutorial-inheritance.html",
        "query": "SELECT name, elevation FROM geo_cities WHERE elevation > 500",
    },
]

SCHEMA_REFERENCE = [
    {
        "name": "weather",
        "columns": ["city", "temp_lo", "temp_hi", "prcp", "date"],
    },
    {
        "name": "cities",
        "columns": ["name", "location"],
    },
    {
        "name": "empsalary",
        "columns": ["empno", "salary", "depname", "enroll_date"],
    },
    {
        "name": "accounts",
        "columns": ["name", "branch_name", "balance"],
    },
    {
        "name": "branches",
        "columns": ["name", "balance"],
    },
    {
        "name": "geo_cities",
        "columns": ["name", "population", "elevation"],
    },
    {
        "name": "capitals",
        "columns": ["name", "population", "elevation", "state"],
    },
    {
        "name": "myview",
        "columns": ["name", "temp_lo", "temp_hi", "prcp", "date", "location"],
    },
]
