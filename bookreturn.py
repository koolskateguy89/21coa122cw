"""
This modules provides functionality for the librarian to return books. It asks
for the ID of the books they wish to return and either displays an appropriate
error message or a message letting them know the books have been successfully
returned.

When a book is returned, the most recent transaction log for that book is
updated with a return date to signify that the book has been returned.
"""

from datetime import datetime
from tkinter import *

import database

ids_entry: Entry = None
status_frame: LabelFrame = None
status_label: Label = None


def get_frame(parent) -> LabelFrame:
    """
    Create and decorate the frame for checking out books.

    :param parent: the parent of the frame
    :return: the fully decorated frame
    """
    global ids_entry
    global status_frame
    global status_label

    bg = 'black'

    frame = LabelFrame(parent, text="Book Return", padx=5, pady=5, bg=bg,
                       fg='white')

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg,
          fg='white').grid(row=0, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=0, column=1)
    # return book when Enter is pressed
    ids_entry.bind('<Return>', lambda event: _return())

    return_button = Button(frame, text="Return", command=_return)
    return_button.pack(pady=10)

    status_frame = LabelFrame(frame, padx=1, pady=5, fg='white')
    status_label = Label(status_frame, bg=bg, fg='white')
    status_label.pack()

    return frame


def on_show():
    """
    Hide status and set focus on the book IDs entry when this frame is shown.
    """
    _hide_status()
    ids_entry.focus_set()


def _return():
    """
    Return given book(s) and notify librarian of status.
    """
    ids = ids_entry.get().split(',')

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        _show_status('Error', 'A book ID is invalid (not a number)', 'red')
        return

    error, success = return_book(*ids)

    if error is not None:
        _show_status('Error', error, 'red')

    if success is not None:
        _show_status('Success', success, 'green')


def _show_status(title, msg, colour):
    """
    Make the status frame visible and configure it to show the given message.

    :param title: the status type
    :param msg: the status message
    :param colour: status frame background colour
    """
    status_frame.configure(text=title, bg=colour)
    status_label.configure(text=msg)
    status_frame.pack(pady=5)


def _hide_status():
    """
    Hide the status frame.
    """
    status_frame.pack_forget()


def return_book(*book_ids: int) -> tuple[str | None, str | None]:
    """
    Try to return given books, update the database and logfile if successful.

    :param book_ids: the id(s) of the book(s) to return
    :return: (error message, success message)
    """
    returned = []

    for book_id in book_ids:
        book = database.search_book_by_id(book_id)

        if book is None:
            return f"No book with ID: {book_id}", _success(returned)

        if book['member'] == '0':
            return f"Book {book_id} already returned", _success(returned)

        book['member'] = '0'

        book_logs: list[dict] = database.logs_for_book_id(book_id)

        # get the log that was the checkout of this book
        log = None
        for _log in book_logs:
            if database.log_is_on_loan(_log):
                log = _log
                break

        # update the log, indicating the book has been returned
        if log is not None:
            log['return'] = datetime.now()

        returned.append(str(book_id))

    return None, _success(returned)


def _success(returned: list[str]) -> str | None:
    """
    Update database files if books have been returned.

    :param returned: the ids of returned books
    :return: 'success message' of return_book
    """
    if not returned:
        return None

    database.update_logfile()
    database.update_database()

    return f"Book(s) {{{','.join(returned)}}} returned"


# tests
def main():
    """
    Main method which contains test code for this module.
    """
    # Modify database methods so files aren't modified while testing
    database.update_database = lambda: None
    database.update_logfile = lambda: None

    assert return_book() == (None, None), 'return_book failed for no input'

    assert _success([]) is None, '_success failed for empty list'

    print(f'{return_book(1) = }')

    print('bookreturn.py has passed all tests!')


if __name__ == "__main__":
    main()
