"""
Miscellaneous utility functions that help with general functionalities.
"""

from datetime import datetime, timedelta

DATE_FORMAT = '%d/%m/%Y'
SIXTY_DAYS = timedelta(days=60)
NOW = datetime.now()


def str_to_date(s: str) -> datetime:
    """
    Convert a string to a datetime object according to a DD/MM/YYYY format.

    :param s: the date string
    :return: the datetime object
    """
    return datetime.strptime(s, DATE_FORMAT)


def date_to_str(d: datetime) -> str:
    """
    Convert a datetime object to a string with DD/MM/YYYY format as it is more
    appropriate than the default format 'YYYY-MM-DD HH:MM:SS'.

    :param d: the datetime object
    :return: the date string
    """
    return datetime.strftime(d, DATE_FORMAT)


def is_more_than_60_days_ago(date: datetime) -> bool:
    """
    Check if the given date was more than 60 days ago.

    :param date: the date to check
    :return: whether the given date was more than 60 days ago or not
    """
    return NOW - date > SIXTY_DAYS


def log_is_on_loan(log: dict) -> bool:
    """
    Check if given log is incomplete, thus if the book it represents is on loan.

    :param log: the log to check
    :return: whether the log's book is on loan, according only to the log
    """
    return log.get('return') is None


# tests
if __name__ == "__main__":
    # test date functions
    _s = "12/01/2021"
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

    assert log_is_on_loan(_log_on_loan), 'log_is_on_loan failed for on loan'
    assert not log_is_on_loan(_log_not_on_loan), \
        'log_is_on_loan failed for not on loan'

    print('utils.py has passed all tests!')
