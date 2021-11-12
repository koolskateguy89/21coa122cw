"""
This modules provides functionality for the librarian to return books. It asks
for the ID of the books they wish to return and either displays an appropriate
error message or a mesage letting them know the books have been successfully
returned.
"""
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from typing import Callable

import database
import utils

frame: LabelFrame = None
ids_entry: Entry = None


def get_frame(parent, back_to_menu: Callable) -> LabelFrame:
    """
    Lazily create the frame for checking out books and set focus on
    the member ID entry.

    :param parent: the parent of the frame
    :param back_to_menu: function that returns back to menu
    :return: the fully decorated frame
    """
    global frame
    global ids_entry

    if frame is not None:
        ids_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Return", padx=5, pady=5, bg=bg, fg="white")

    back_button = Button(frame, text="Back", fg="crimson", command=back_to_menu)
    back_button.pack(pady=10)

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg='white') \
        .grid(row=0, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=0, column=1)
    # return book when Enter is pressed
    ids_entry.bind('<Return>', lambda event: _return())
    # go back when Esc is pressed
    ids_entry.bind('<Escape>', lambda event: back_to_menu())

    return_button = Button(frame, text="Return", command=_return)
    return_button.pack(pady=10)

    return frame


def _return():
    """
    Return given book(s) and notify librarian of status.
    """
    ids = ids_entry.get().split(',')

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        messagebox.showerror('Error', 'A book ID is invalid (not a number)')
        return

    error, success = return_book(*ids)

    if error is not None:
        messagebox.showerror('Error', error)

    if success is not None:
        messagebox.showinfo('Success', success)


def return_book(*book_ids: int) -> tuple[str or None, str or None]:
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
            if utils.log_is_on_loan(_log):
                log = _log
                break

        # update the log, indicating the book has been returned
        if log is not None:
            log['return'] = datetime.now()

        returned.append(str(book_id))

    return None, _success(returned)


def _success(returned: list[str]) -> str or None:
    """
    Update database files if books have been returned.

    :param returned: the ids of returned books
    :return: 'success message' of return_book
    """
    if len(returned) == 0:
        return None

    database.update_logfile()
    database.update_database()

    return f"Book(s) {{{','.join(returned)}}} returned"


# tests
if __name__ == "__main__":
    # Modify database methods so files aren't modified while testing
    database.update_database = lambda: None
    database.update_logfile = lambda: None

    assert return_book() == (None, None), 'return_book failed for no input'

    assert _success([]) is None, '_success failed for empty list'

    print('return_book(1):', return_book(1))

    print('bookreturn.py has passed all tests!')
