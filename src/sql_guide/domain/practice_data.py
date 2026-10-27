"""Trusted setup for the three practice databases.

The statements are authored here. Learner SQL never becomes setup.
"""

from sql_guide.domain.errors import UnknownPracticeDatabase

_SHOP: tuple[str, ...] = (
    """
    CREATE TABLE books (
        id integer PRIMARY KEY,
        title text NOT NULL,
        year integer NOT NULL,
        pages integer NOT NULL,
        price integer NOT NULL,
        isbn text NOT NULL
    )
    """,
    """
    INSERT INTO books (id, title, year, pages, price, isbn) VALUES
        (1, 'Север', 2019, 320, 400, '978-5-0001'),
        (2, 'Юг', 2021, 180, 350, '978-5-0002'),
        (3, 'Восток', 2019, 90, 200, '978-5-0003')
    """,
    """
    CREATE TABLE authors (
        id integer PRIMARY KEY,
        name text NOT NULL
    )
    """,
    """
    INSERT INTO authors (id, name) VALUES
        (1, 'Анна Ли'),
        (2, 'Марк Ной')
    """,
    """
    CREATE TABLE book_authors (
        book_id integer NOT NULL,
        author_id integer NOT NULL
    )
    """,
    """
    INSERT INTO book_authors (book_id, author_id) VALUES
        (1, 1),
        (2, 2),
        (3, 1)
    """,
    """
    CREATE TABLE orders (
        id integer PRIMARY KEY,
        book_id integer,
        city text,
        copies integer NOT NULL,
        created_at date NOT NULL
    )
    """,
    """
    INSERT INTO orders (id, book_id, city, copies, created_at) VALUES
        (1, 1, 'Казань', 2, DATE '2026-10-20'),
        (2, 1, 'Пермь', 1, DATE '2026-10-21'),
        (3, 3, 'Казань', 4, DATE '2026-10-25'),
        (4, NULL, 'Омск', 1, DATE '2026-10-26'),
        (5, 2, NULL, 1, DATE '2026-10-26')
    """,
)

_LIBRARY: tuple[str, ...] = (
    """
    CREATE TABLE readers (
        id integer PRIMARY KEY,
        name text NOT NULL,
        city text
    )
    """,
    """
    INSERT INTO readers (id, name, city) VALUES
        (1, 'Ира', 'Казань'),
        (2, 'Олег', 'Пермь'),
        (3, 'Нина', NULL)
    """,
    """
    CREATE TABLE copies (
        id integer PRIMARY KEY,
        title text NOT NULL,
        shelf text NOT NULL
    )
    """,
    """
    INSERT INTO copies (id, title, shelf) VALUES
        (1, 'Север', 'А-1'),
        (2, 'Юг', 'А-2'),
        (3, 'Восток', 'Б-1')
    """,
    """
    CREATE TABLE loans (
        id integer PRIMARY KEY,
        reader_id integer NOT NULL,
        copy_id integer,
        due_on date NOT NULL
    )
    """,
    """
    INSERT INTO loans (id, reader_id, copy_id, due_on) VALUES
        (1, 1, 1, DATE '2026-11-01'),
        (2, 2, 1, DATE '2026-11-03'),
        (3, 3, NULL, DATE '2026-11-20')
    """,
)

_TEAM: tuple[str, ...] = (
    """
    CREATE TABLE departments (
        id integer PRIMARY KEY,
        name text NOT NULL
    )
    """,
    """
    INSERT INTO departments (id, name) VALUES
        (1, 'Редакция'),
        (2, 'Склад')
    """,
    """
    CREATE TABLE employees (
        id integer PRIMARY KEY,
        name text NOT NULL,
        department_id integer,
        salary integer NOT NULL
    )
    """,
    """
    INSERT INTO employees (id, name, department_id, salary) VALUES
        (1, 'Аня', 1, 90000),
        (2, 'Борис', 1, 70000),
        (3, 'Вера', 2, 60000),
        (4, 'Глеб', NULL, 50000)
    """,
)

_DATABASES: dict[str, tuple[str, ...]] = {
    "shop": _SHOP,
    "library": _LIBRARY,
    "team": _TEAM,
    "empty": (),
}


def practice_setup(database_id: str) -> tuple[str, ...]:
    """Return the setup statements for one practice database.

    Args:
        database_id: ``shop``, ``library``, ``team``, or ``empty``.

    Returns:
        Trusted statements that create that database's tables.

    Raises:
        UnknownPracticeDatabase: The id is not one of the practice databases.
    """
    try:
        return _DATABASES[database_id]
    except KeyError as exc:
        raise UnknownPracticeDatabase("Unknown practice database") from exc
