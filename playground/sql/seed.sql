-- PostgreSQL official tutorial seed data (Chapters 2-3)
-- https://www.postgresql.org/docs/current/tutorial-start.html

DROP VIEW IF EXISTS myview;
DROP TABLE IF EXISTS capitals CASCADE;
DROP TABLE IF EXISTS geo_cities CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS empsalary CASCADE;
DROP TABLE IF EXISTS weather CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

CREATE TABLE weather (
    city    varchar(80),
    temp_lo int,
    temp_hi int,
    prcp    real,
    date    date
);

CREATE TABLE cities (
    name     varchar(80),
    location point
);

INSERT INTO weather VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');
INSERT INTO weather VALUES ('San Francisco', 43, 57, 0.0, '1994-11-29');
INSERT INTO weather VALUES ('Hayward', 37, 54, NULL, '1994-11-29');

INSERT INTO cities VALUES ('San Francisco', '(-194.0, 53.0)');

-- Chapter 2.8 temperature correction
UPDATE weather
SET temp_hi = temp_hi - 2, temp_lo = temp_lo - 2
WHERE date > '1994-11-28';

CREATE VIEW myview AS
    SELECT name, temp_lo, temp_hi, prcp, date, location
    FROM weather, cities
    WHERE city = name;

CREATE TABLE empsalary (
    empno       int,
    salary      int,
    depname     text,
    enroll_date date
);

INSERT INTO empsalary VALUES
(1, 5000, 'sales', '1991-09-01'),
(2, 3900, 'personnel', '1992-07-01'),
(3, 4800, 'sales', '1993-10-01'),
(4, 4800, 'sales', '1994-10-01'),
(5, 3500, 'personnel', '1995-01-01'),
(7, 4200, 'develop', '1996-02-01'),
(8, 6000, 'develop', '1996-10-01'),
(9, 4500, 'develop', '1997-01-01'),
(10, 5200, 'develop', '1998-11-01'),
(11, 5200, 'develop', '1999-05-01');

CREATE TABLE branches (
    name    text PRIMARY KEY,
    balance real
);

CREATE TABLE accounts (
    name        text PRIMARY KEY,
    branch_name text REFERENCES branches(name),
    balance     real
);

INSERT INTO branches VALUES ('san_francisco', 10000);
INSERT INTO branches VALUES ('los_angeles', 5000);
INSERT INTO accounts VALUES ('Alice', 'san_francisco', 1000);
INSERT INTO accounts VALUES ('Bob', 'san_francisco', 500);
INSERT INTO accounts VALUES ('Wally', 'los_angeles', 750);

CREATE TABLE geo_cities (
    name       text,
    population real,
    elevation  int
);

CREATE TABLE capitals (
    state char(2) UNIQUE NOT NULL
) INHERITS (geo_cities);

INSERT INTO geo_cities VALUES ('Las Vegas', 1200000, 2174);
INSERT INTO geo_cities VALUES ('Mariposa', 4000, 1953);
INSERT INTO geo_cities VALUES ('Madison', 250000, 845);
INSERT INTO capitals VALUES ('Sacramento', 500000, 25, 'CA');
INSERT INTO capitals VALUES ('Olympia', 50000, 95, 'WA');
