"""
This module contains functions that other modules can use to interact with the
book database and logfile. This module also contains utility functions.

Books are represented by SimpleNamespaces, mimicking a class that only has
attributes:
    'id': int
    'genre': str
    'title': str
    'author': str
    'purchase_date': str
    'member': str

The book database is represented as a List[SimpleNamespace].

Logs are represented by dicts:
    'book_id': int
    'checkout': datetime
    'return': datetime/None
    'member': str
  Books that haven't been returned yet have None as 'return'

The logfile is represented as a List[dict].

Written by F120840 between 8th November and 16th December 2021.
"""

import csv
from datetime import datetime
from functools import lru_cache
from types import SimpleNamespace
from typing import List, Generator

DATE_FORMAT = '%d/%m/%Y'
NOW = datetime.now()


# Books

def _read_database() -> List[SimpleNamespace]:
    """
    Read the book database file.

    :return: a list of SimpleNamespaces representing all books
    """
    result = []

    with open('database.txt', newline='') as db:
        reader = csv.DictReader(db, fieldnames=BOOK_HEADERS)
        for book in reader:
            book['id'] = int(book['id'])
            result.append(SimpleNamespace(**book))

    return result


def update_database():
    """
    Update the book database file.
    """
    with open('database.txt', 'w', newline='') as db:
        writer = csv.DictWriter(db, fieldnames=BOOK_HEADERS)
        for book in books:
            writer.writerow(vars(book))


def search_books_by_param(param: str, value) -> List[SimpleNamespace]:
    """
    Return books that match the given parameter.

    :param param: the property of the book to check
    :param value: the value to check the property is equal to
    :return: books that match the parameter
    """
    return [book for book in books if getattr(book, param) == value]


def search_book_by_id(book_id: int) -> SimpleNamespace:
    """
    Return the book with the given ID, or None if there is no book with that ID.

    :param book_id: the book ID to search for
    :return: the book with the given ID
    """
    if 1 <= book_id <= len(books):
        return books[book_id - 1]


def is_book_on_loan(book: SimpleNamespace) -> bool:
    """
    Check if the given book is currently on loan.

    :param book: the book to check
    :return: True if the book is on loan, False is the book is available
    """
    return book.member != '0'


# Logs

def _read_logfile() -> List[dict]:
    """
    Read the logfile.

    :return: a list of dicts representing all logs
    """
    with open('logfile.txt', newline='') as logfile:
        reader = csv.DictReader(logfile, fieldnames=LOG_HEADERS)
        result = list(reader)

    # update types
    for log in result:
        log['book_id'] = int(log['book_id'])
        log['checkout'] = str_to_date(log['checkout'])
        log['return'] = str_to_date(r) if (r := log['return']) else None

    return result


def update_logfile():
    """
    Update the logfile.
    """
    with open('logfile.txt', 'w', newline='') as logfile:
        writer = csv.DictWriter(logfile, fieldnames=LOG_HEADERS)
        for log in logs:
            log = log.copy()  # copy so we don't mutate the original object
            log['checkout'] = date_to_str(log['checkout'])
            if (ret := log['return']) is not None:
                log['return'] = date_to_str(ret)
            writer.writerow(log)


def logs_for_member_id(member_id: str) -> Generator[dict, None, None]:
    """
    Return all logs corresponding to the member with the given ID.

    :param member_id: the member ID
    :return: all logs corresponding to that member, in a generator
    """
    for log in logs:
        if log['member'] == member_id:
            yield log


def most_recent_log_for_book_id(book_id: int) -> dict:
    """
    Return the most recent log that corresponds to a book with given ID. This
    log can be used to determine  whether the book has been on loan for more
    than 60 days or not.

    :param book_id: the ID the book to check for
    :return: the most recent log (dict)
    """
    for log in reversed(logs):
        if log['book_id'] == book_id:
            return log


def new_log(book_id: int, member_id: str) -> dict:
    """
    Create a new log, ready to be appended to logs.

    :param book_id: the ID of the book the log corresponds to
    :param member_id: the ID of the member the log corresponds to
    :return: the log as a dict
    """
    return {
        'book_id': book_id,
        'checkout': datetime.now(),
        'return': None,
        'member': member_id
    }


def is_log_on_loan(log: dict) -> bool:
    """
    Check if the given log has no return date, thus if the book it corresponds
    to is currently on loan - according only to the given log (the book may be
    on loan but a different log would show this).

    :param log: the log to check
    :return: whether the log's book is on loan, according only to the log
    """
    return log['return'] is None


# utils

def is_more_than_60_days_ago(date: datetime) -> bool:
    """
    Check if the given date was more than 60 days ago.

    :param date: the date to check
    :return: whether the given date was more than 60 days ago or not
    """
    return (NOW - date).days > 60


@lru_cache(maxsize=None)
def str_to_date(s: str) -> datetime:
    """
    Convert a string in the DD/MM/YYYY format to a datetime object.

    :param s: the date string
    :return: the datetime object
    """
    return datetime.strptime(s, DATE_FORMAT)


@lru_cache(maxsize=None)
def date_to_str(d: datetime) -> str:
    """
    Convert a datetime object to a string with DD/MM/YYYY format as it is more
    appropriate than the default format 'YYYY-MM-DD HH:MM:SS'.

    :param d: the datetime object
    :return: the date string
    """
    return datetime.strftime(d, DATE_FORMAT)


BOOK_HEADERS = ('id', 'genre', 'title', 'author', 'purchase_date', 'member')
books: List[SimpleNamespace] = _read_database()

LOG_HEADERS = ('book_id', 'checkout', 'return', 'member')
logs: List[dict] = _read_logfile()


def test():
    """
    Main method which contains test code for this module.
    """
    # test book keys
    if books:
        _book = books[0]
        assert sorted(BOOK_HEADERS) == sorted(list(vars(_book).keys())), \
            'BOOK_HEADERS and book keys are inconsistent'

    # test log keys
    if logs:
        _log = logs[0]
        assert sorted(LOG_HEADERS) == sorted(list(_log.keys())), \
            'LOG_HEADERS and log keys are inconsistent'

    # test reading book database
    assert _read_database() == books, '_read_database failed test'
    # test reading logfile
    assert _read_logfile() == logs, '_read_logfile failed test'

    # test creating a new log entry
    _log = new_log(2, 'suii')
    assert _log['book_id'] == 2, 'new_log: [book_id] has incorrect value'
    assert _log['member'] == 'suii', 'new_log: [member] has incorrect value'
    assert _log['checkout'] is not None, 'new_log [checkout] is None'
    assert _log['return'] is None, 'new_log: [return] is not None'

    print(f'{len(books) = }')
    print(f'{len(logs) = }')

    # print('Book 11 title:', search_book_by_id(11).title)
    # print(logs)

    # test date functions
    _s = '12/01/2021'
    _d = str_to_date(_s)
    _s1 = date_to_str(_d)

    assert _s == _s1, 'str_to_date and date_to_str are inconsistent'

    assert is_more_than_60_days_ago(str_to_date('1/1/2000')), \
        'is_more_than_60_days_ago does not function correctly'
    assert not is_more_than_60_days_ago(datetime.now()), \
        'is_more_than_60_days_ago does not function correctly'

    # test dict-related functions
    _log_on_loan = {'return': None}
    _log_not_on_loan = {'return': datetime.now()}

    assert is_log_on_loan(_log_on_loan), 'is_log_on_loan failed for on loan'
    assert not is_log_on_loan(_log_not_on_loan), \
        'is_log_on_loan failed for not on loan'

    print('database.py has passed all tests!')


if __name__ == "__main__":
    test()
