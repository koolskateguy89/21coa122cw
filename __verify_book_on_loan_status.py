import database


def main():
    logs = database.logs

    logsBookId = dict[int, list[dict]]()
    for log in logs:
        bookId = log['book_id']
        logsBookId.setdefault(bookId, []).append(log)

    for bookId, bookLogs in logsBookId.items():
        book = database.search_book_by_id(bookId)
        isOnLoanMemberID = book.member != '0'

        logsOnLoan = sum(1 for log in bookLogs if database.log_is_on_loan(log))

        if isOnLoanMemberID:
            assert logsOnLoan == 1, f'{bookId} is out but has {logsOnLoan} on loan'
        else:
            assert logsOnLoan == 0, f'{bookId} is not out but has {logsOnLoan} on loan'


if __name__ == '__main__':
    main()
    print('all logs are valid, nice')
