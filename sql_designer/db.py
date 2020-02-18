from PySide2.QtSql import QSqlDatabase, QSqlQuery
import datetime


BOOKS_SQL = """
    create table books(id integer primary key, title varchar, author integer,
                       genre integer, year integer, rating integer)
    """
AUTHORS_SQL = """
    create table authors(id integer primary key, name varchar, birthdate text)
    """

INSERT_BOOK_SQL = """
    insert into books(title, year, author, genre, rating)
                values(?, ?, ?, ?, ?)
    """

INSERT_AUTHOR_SQL = """
    insert into authors(name, birthdate) values(?, ?)
    """

def add_book(q, title, year, authorId, genreId, rating):
    q.addBindValue(title)
    q.addBindValue(year)
    q.addBindValue(authorId)
    q.addBindValue(genreId)
    q.addBindValue(rating)
    q.exec_()

def add_author(q, name, birthdate):
    q.addBindValue(name)
    q.addBindValue(str(birthdate))
    q.exec_()
    return q.lastInsertId()

def init_db():
    """
    init_db()
    Initializes the database.
    If tables "books" and "authors" are already in the database, do nothing.
    Return value: None or raises ValueError
    The error value is the QtSql error instance.
    """
    def check(func, *args):
        if not func(*args):
            raise ValueError(func.__self__.lastError())

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(":memory:")

    check(db.open)

    sfiction = 1
    fantasy = 2
    fiction = 3

    q = QSqlQuery()
    check(q.exec_, BOOKS_SQL)
    check(q.exec_, AUTHORS_SQL)

    check(q.prepare, INSERT_AUTHOR_SQL)
    asimovId = add_author(q, "Isaac Asimov", datetime.date(1920, 2, 1))
    greeneId = add_author(q, "Graham Greene", datetime.date(1904, 10, 2))
    pratchettId = add_author(q, "Terry Pratchett", datetime.date(1948, 4, 28))

    check(q.prepare, INSERT_BOOK_SQL)
    add_book(q, "Foundation", 1951, asimovId, sfiction, 3)
    add_book(q, "Foundation and Empire", 1952, asimovId, sfiction, 4)
    add_book(q, "Second Foundation", 1953, asimovId, sfiction, 3)
    add_book(q, "Foundation's Edge", 1982, asimovId, sfiction, 3)
    add_book(q, "Foundation and Earth", 1986, asimovId, sfiction, 4)
    add_book(q, "Prelude to Foundation", 1988, asimovId, sfiction, 3)
    add_book(q, "Forward the Foundation", 1993, asimovId, sfiction, 3)
    add_book(q, "The Power and the Glory", 1940, greeneId, fiction, 4)
    add_book(q, "The Third Man", 1950, greeneId, fiction, 5)
    add_book(q, "Our Man in Havana", 1958, greeneId, fiction, 4)
    add_book(q, "Guards! Guards!", 1989, pratchettId, fantasy, 3)
    add_book(q, "Night Watch", 2002, pratchettId, fantasy, 3)
    add_book(q, "Going Postal", 2004, pratchettId, fantasy, 3)

    return db

if __name__ == '__main__':
    init_db()
