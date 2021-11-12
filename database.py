"""
This module contains functions that other modules can use to interact with the
book database and logfile.

Books are represented by dicts:
    'id': int
    'genre': str
    'title': str
    'author': str
    'purchase_date': datetime.datetime
    'member': str

The book database is represented as a dict[int, dict]
    key = book_id
    value = book (dict)


Logs are also represented by dicts:
    'book_id': int
    'checkout': datetime
    'return': datetime/None
    'member': str
  Books that haven't been returned yet have None as 'return'

The logfile is represented as a list[dict].
"""

import csv

import utils


# Book database

def _read_database() -> dict[int, dict]:
    """
    Read the database file and parse it into a dictionary.

    :return: a dictionary representing the database
    """
    result = {}

    with open('database.txt', newline='') as db:
        reader = csv.DictReader(db, fieldnames=book_headers)
        # skip header
        next(reader)

        for book in reader:
            book['id'] = int(book['id'])
            book['purchase_date'] = utils.str_to_date(book['purchase_date'])

            result[book['id']] = book

    return result


def update_database():
    """
    Update the database file.
    """
    with open('database.txt', 'w', newline='') as db:
        writer = csv.DictWriter(db, fieldnames=book_headers)
        writer.writeheader()
        for book in books.values():
            # write the purchase date in appropriate format to file
            book = {**book,
                    'purchase_date': utils.date_to_str(book['purchase_date'])
                    }
            writer.writerow(book)


# Searching for books

def search_books_by_param(param: str, value: str) -> dict[int, dict]:
    """
    Return books that match the given parameter.

    :param param: the property of the book to check
    :param value: the desired
    :return: books that match the parameter
    """
    return {book_id: book for (book_id, book) in books.items() if book[param] == value}


def search_book_by_id(book_id: int) -> dict:
    """
    Return the book with the given id.

    :param book_id: the book id to search for
    :return: the book with the given id
    """
    return books.get(book_id)


# Logs

def _read_logfile() -> list[dict]:
    """
    Read the log file.

    :return: a list of dicts representing all logs
    """
    result = []

    with open('logfile.txt', newline='') as logfile:
        reader = csv.DictReader(logfile, fieldnames=log_headers)
        # skip header
        next(reader)

        # update types
        for log in reader:
            log['book_id'] = int(log['book_id'])
            log['checkout'] = utils.str_to_date(log['checkout'])

            r = log['return']
            log['return'] = utils.str_to_date(r) if len(r) != 0 else None

            result.append(log)

    return result


def update_logfile():
    """
    Update the logfile.
    """
    with open('logfile.txt', 'w', newline='') as logfile:
        writer = csv.DictWriter(logfile, fieldnames=log_headers)
        writer.writeheader()

        for log in logs:
            log = log.copy()
            log['checkout'] = utils.date_to_str(log['checkout'])
            if log['return'] is not None:
                log['return'] = utils.date_to_str(log['return'])
            writer.writerow(log)


def logs_for_member_id(member_id: str) -> list[dict]:
    """
    Return all logs corresponding to a given member ID.

    :param member_id: the member ID
    :return: all logs corresponding to that member ID
    """
    return [log for log in logs if log['member'] == member_id]


def logs_for_book_id(book_id: int) -> list[dict]:
    """
    Return all logs corresponding to a given book ID.

    :param book_id: the book ID to search for
    :return: all logs for the book
    """
    return [log for log in logs if log['book_id'] == book_id]


def new_log(book_id: int, member_id: str) -> dict:
    """
    Create a new log (dict), ready to be appended to logs.

    :param book_id: the ID of the book the log is for
    :param member_id: the ID of the member the log is for
    :return: the log
    """
    from datetime import datetime
    return {
        'book_id': book_id,
        'checkout': datetime.now(),
        'return': None,
        'member': member_id
    }


book_headers = ['id', 'genre', 'title', 'author', 'purchase_date', 'member']
books: dict[int, dict] = _read_database()

log_headers = ['book_id', 'checkout', 'return', 'member']
logs: list[dict] = _read_logfile()

# tests
if __name__ == "__main__":
    # test book keys
    if len(books) != 0:
        _book = next(iter(books.values()))
        assert sorted(book_headers) == sorted(list(_book.keys())), \
            'book_headers and book keys are inconsistent'

    # test log keys
    if len(logs) != 0:
        _log = logs[0]
        assert sorted(log_headers) == sorted(list(_log.keys())), \
            'log_headers and log keys are inconsistent'

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

    print('len(books):', len(books))
    print('len(logs):', len(logs))

    # print('Book 11 title:', search_book_by_id(11)['title'])
    # print(logs)

    print('database.py has passed all tests!')
