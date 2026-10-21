-- =============================================================================
-- Pagila Schema Subset — NL2SQL Demo
-- =============================================================================
-- A minimal subset of the Pagila (PostgreSQL port of MySQL Sakila) schema.
-- Used to demonstrate how an NL2SQL agent reasons about a real schema
-- before generating SQL.
--
-- Full Pagila schema: https://github.com/devrimgunduz/pagila
-- Install full schema: psql -U postgres -d pagila -f pagila-schema.sql
--
-- This subset is self-contained for the demo. It creates a lightweight
-- local database you can query without the full 15-table schema.
-- =============================================================================

-- Drop and recreate for clean demo state
DROP TABLE IF EXISTS rental      CASCADE;
DROP TABLE IF EXISTS payment     CASCADE;
DROP TABLE IF EXISTS inventory   CASCADE;
DROP TABLE IF EXISTS film        CASCADE;
DROP TABLE IF EXISTS customer    CASCADE;
DROP TABLE IF EXISTS address     CASCADE;
DROP TABLE IF EXISTS city        CASCADE;
DROP TABLE IF EXISTS category    CASCADE;
DROP TABLE IF EXISTS film_category CASCADE;

-- City lookup
CREATE TABLE city (
    city_id     SERIAL PRIMARY KEY,
    city        VARCHAR(50) NOT NULL,
    country     VARCHAR(50) NOT NULL DEFAULT 'Canada'
);

-- Address
CREATE TABLE address (
    address_id  SERIAL PRIMARY KEY,
    address     VARCHAR(50) NOT NULL,
    city_id     INTEGER REFERENCES city(city_id),
    postal_code VARCHAR(10)
);

-- Customer
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(45) NOT NULL,
    last_name   VARCHAR(45) NOT NULL,
    email       VARCHAR(50),
    address_id  INTEGER REFERENCES address(address_id),
    active      BOOLEAN DEFAULT TRUE,
    create_date TIMESTAMP DEFAULT NOW()
);

-- Film category
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name        VARCHAR(25) NOT NULL
);

-- Film
CREATE TABLE film (
    film_id         SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    release_year    INTEGER,
    rental_duration SMALLINT DEFAULT 3,
    rental_rate     NUMERIC(4,2) DEFAULT 4.99,
    length          SMALLINT,
    replacement_cost NUMERIC(5,2) DEFAULT 19.99,
    rating          VARCHAR(10) DEFAULT 'G'
);

-- Film to category mapping
CREATE TABLE film_category (
    film_id     INTEGER REFERENCES film(film_id),
    category_id INTEGER REFERENCES category(category_id),
    PRIMARY KEY (film_id, category_id)
);

-- Inventory (copies of films)
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    film_id      INTEGER REFERENCES film(film_id),
    store_id     SMALLINT DEFAULT 1
);

-- Rental
CREATE TABLE rental (
    rental_id    SERIAL PRIMARY KEY,
    rental_date  TIMESTAMP NOT NULL DEFAULT NOW(),
    inventory_id INTEGER REFERENCES inventory(inventory_id),
    customer_id  INTEGER REFERENCES customer(customer_id),
    return_date  TIMESTAMP,
    staff_id     SMALLINT DEFAULT 1
);

-- Payment
CREATE TABLE payment (
    payment_id  SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customer(customer_id),
    staff_id    SMALLINT DEFAULT 1,
    rental_id   INTEGER REFERENCES rental(rental_id),
    amount      NUMERIC(5,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Sample data — enough for meaningful demo queries
-- =============================================================================

INSERT INTO city (city, country) VALUES
    ('Toronto',   'Canada'),
    ('Vancouver', 'Canada'),
    ('Montreal',  'Canada'),
    ('Calgary',   'Canada'),
    ('Ottawa',    'Canada');

INSERT INTO address (address, city_id, postal_code) VALUES
    ('123 King St',    1, 'M5H 1J9'),
    ('456 Granville',  2, 'V6C 1T2'),
    ('789 Sainte-Cat', 3, 'H3B 1A7'),
    ('321 Banff Ave',  4, 'T2P 2K7'),
    ('654 Rideau St',  5, 'K1N 8X6');

INSERT INTO customer (first_name, last_name, email, address_id, active) VALUES
    ('Alice',   'Martin',  'alice@example.com',   1, TRUE),
    ('Bob',     'Singh',   'bob@example.com',     2, TRUE),
    ('Carol',   'Zhang',   'carol@example.com',   3, TRUE),
    ('David',   'Okafor',  'david@example.com',   4, TRUE),
    ('Elena',   'Kovacs',  'elena@example.com',   5, TRUE),
    ('Frank',   'Diallo',  'frank@example.com',   1, FALSE),
    ('Grace',   'Tanaka',  'grace@example.com',   2, TRUE),
    ('Hassan',  'Ali',     'hassan@example.com',  3, TRUE),
    ('Ingrid',  'Svensson','ingrid@example.com',  4, TRUE),
    ('James',   'Patel',   'james@example.com',   5, TRUE);

INSERT INTO category (name) VALUES
    ('Action'), ('Comedy'), ('Drama'), ('Horror'),
    ('Sci-Fi'), ('Documentary'), ('Romance'), ('Thriller');

INSERT INTO film (title, description, release_year, rental_rate, length, rating) VALUES
    ('ACADEMY DINOSAUR',  'Epic drama of a teacher and student',    2006, 0.99, 86,  'PG'),
    ('ACE GOLDFINGER',    'Shark-wrangling documentary',            2006, 4.99, 48,  'G'),
    ('ADAPTATION HOLES',  'Documentary of a waitress and student',  2006, 2.99, 50,  'NC-17'),
    ('AFFAIR PREJUDICE',  'Sensational musical of a teacher',       2006, 2.99, 117, 'G'),
    ('AFRICAN EGG',       'Fateful story of a crocodile',           2006, 2.99, 130, 'G'),
    ('AGENT TRUMAN',      'Thriller on espionage',                  2006, 2.99, 169, 'PG'),
    ('AIRPLANE SIERRA',   'Epic comedy about a student',            2006, 4.99, 62,  'PG-13'),
    ('AIRPORT POLLOCK',   'Documentary on modern art',              2006, 4.99, 54,  'R'),
    ('ALABAMA DEVIL',     'Thoughtful comedy of dentists',          2006, 2.99, 114, 'PG-13'),
    ('ALADDIN CALENDAR',  'Action-packed drama of astronauts',      2006, 4.99, 63,  'NC-17');

INSERT INTO film_category (film_id, category_id) VALUES
    (1,3),(2,6),(3,6),(4,5),(5,3),
    (6,8),(7,2),(8,6),(9,2),(10,1);

INSERT INTO inventory (film_id, store_id) VALUES
    (1,1),(1,1),(2,1),(3,1),(4,1),
    (5,1),(6,1),(7,1),(8,1),(9,1),(10,1);

INSERT INTO rental (rental_date, inventory_id, customer_id, return_date) VALUES
    (NOW() - INTERVAL '30 days', 1, 1,  NOW() - INTERVAL '27 days'),
    (NOW() - INTERVAL '25 days', 2, 2,  NOW() - INTERVAL '22 days'),
    (NOW() - INTERVAL '20 days', 3, 3,  NOW() - INTERVAL '17 days'),
    (NOW() - INTERVAL '15 days', 4, 4,  NOW() - INTERVAL '12 days'),
    (NOW() - INTERVAL '10 days', 5, 5,  NOW() - INTERVAL '7 days'),
    (NOW() - INTERVAL '8 days',  6, 1,  NULL),
    (NOW() - INTERVAL '5 days',  7, 2,  NOW() - INTERVAL '2 days'),
    (NOW() - INTERVAL '3 days',  8, 3,  NULL),
    (NOW() - INTERVAL '2 days',  9, 4,  NULL),
    (NOW() - INTERVAL '1 day',  10, 5,  NULL);

INSERT INTO payment (customer_id, rental_id, amount, payment_date) VALUES
    (1, 1, 0.99, NOW() - INTERVAL '30 days'),
    (2, 2, 4.99, NOW() - INTERVAL '25 days'),
    (3, 3, 2.99, NOW() - INTERVAL '20 days'),
    (4, 4, 2.99, NOW() - INTERVAL '15 days'),
    (5, 5, 2.99, NOW() - INTERVAL '10 days'),
    (1, 6, 2.99, NOW() - INTERVAL '8 days'),
    (2, 7, 4.99, NOW() - INTERVAL '5 days');

-- Useful views for the demo
CREATE OR REPLACE VIEW active_rentals AS
SELECT
    r.rental_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    f.title AS film_title,
    cat.name AS category,
    r.rental_date,
    r.return_date,
    CASE WHEN r.return_date IS NULL THEN 'Not returned' ELSE 'Returned' END AS status
FROM rental r
JOIN inventory i  ON r.inventory_id = i.inventory_id
JOIN film f       ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category cat ON fc.category_id = cat.category_id
JOIN customer c   ON r.customer_id = c.customer_id;

CREATE OR REPLACE VIEW customer_spend AS
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    ci.city,
    COUNT(p.payment_id)   AS total_rentals,
    SUM(p.amount)         AS total_spent,
    MAX(p.payment_date)   AS last_payment
FROM customer c
LEFT JOIN payment p   ON c.customer_id = p.customer_id
LEFT JOIN address a   ON c.address_id = a.address_id
LEFT JOIN city ci     ON a.city_id = ci.city_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, ci.city;
