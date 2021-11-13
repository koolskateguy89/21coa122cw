import random
from datetime import datetime, timedelta

import database
import utils

import math

NOW = datetime.now()


# https://stackoverflow.com/a/553320/17381629
def random_date_between(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)


def dates_between(start_date, end_date, n: int):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    inc = math.floor(days_between_dates / n)
    inc_delta = timedelta(days=inc)

    dates = [None] * n
    for i in range(n):
        dates[i] = start_date + (inc_delta * i)

    return dates


def random_date_after(after: datetime) -> datetime:
    first_year = after.year

    if first_year == 2021:
        return random_date_between(after, NOW)

    d = random.randint(1, 28)
    m = random.randint(1, 12)
    y = random.randint(first_year, 2020)

    return utils.str_to_date(f"{d}/{m}/{y}")


def change_log_dates():
    # key: book id;  value: list of logs for that book
    logs = {}
    for log in database.logs:
        book_id = log['book_id']
        if logs.get(book_id) is None:
            logs[book_id] = [log]
        else:
            logs[book_id].append(log)

    for (book_id, logs) in logs.items():
        print(book_id)

        book = database.search_book_by_id(book_id)
        purchase_date = book['purchase_date']

        for log in logs:
            checkout = random_date_after(purchase_date)
            while checkout < purchase_date:
                checkout = random_date_after(purchase_date)

            return_date = random_date_after(purchase_date)
            while return_date < checkout:
                return_date = random_date_after(purchase_date)

            log['checkout'] = checkout
            log['return'] = return_date

    database.update_logfile()




def make_logs():
    members = ['coai', 'suii', 'coaa', 'util', 'arad', 'book']

    # gonna have to sort logs by check-in date
    logs = []
    l = []

    for book_id, book in database.books.items():
        # number of logs per book
        # keep generating until not same as previous
        while (n := random.randint(3, 7)) == len(l):
            pass

        l = [None] * n
        purchase = book['purchase_date']

        dates: list = [None] * n
        dates = dates_between(purchase, NOW, n)

        #for date in dates: print(utils.date_to_str(date))

        for i in range(n-1):
            member = random.choice(members)

            checkout_date = dates[i]
            return_date = dates[i+1]

            book['member'] = member
            book['member'] = '0'

            log = {
                'book_id': book_id,
                'checkout': checkout_date,
                'return': return_date,
                'member': member
            }
            logs.append(log)

        # randomly choose whether book is still on loan or not
        def add_final_log(is_on_loan: bool):
            member = random.choice(members)

            checkout_date = dates[-1]
            return_date = random_date_after(checkout_date)

            if is_on_loan:
                book['member'] = member

            log = {
                'book_id': book_id,
                'checkout': checkout_date,
                'return': None if is_on_loan else return_date,
                'member': member
            }
            logs.append(log)
        add_final_log(bool(random.getrandbits(1)))

    def key(log_):
        return utils.date_to_str(log_['checkout']) + str(log_['book_id'])

    logs.sort(key=key)

    print()
    print('logs:', len(logs))

    database.logs = logs

    database.update_database()
    database.update_logfile()


if __name__ == "__main__":
    make_logs()
    #change_log_dates()
