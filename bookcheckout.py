"""
This module provides functionality to checkout books. It asks the librarian for
the borrowers' member ID and the ID of the book(s) they wish to withdraw.

It checks all inputs are valid, displaying any errors and warnings. If the book
is available, its status is updated in the database and the logfile is updated
with a new entry to signify that the book has been withdrawn.

If the member is currently holding any books more than 60 days, a warning
message is shown to the librarian about these books.
"""

from tkinter import *
from typing import Callable

import database

frame: LabelFrame = None
member_entry: Entry = None
ids_entry: Entry = None

warning_frame: LabelFrame = None
warning_label: Label = None
status_frame: LabelFrame = None
status_label: Label = None


def get_frame(parent, back_to_menu: Callable) -> LabelFrame:
    """
    Lazily create the frame for checking out books and set focus on
    the member ID entry.

    :param parent: the parent of the frame
    :param back_to_menu: function that returns back to menu
    :return: the fully decorated frame
    """
    global frame
    global member_entry
    global ids_entry

    global warning_frame
    global warning_label
    global status_frame
    global status_label

    if frame is not None:
        member_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Checkout", padx=5, pady=5, bg=bg,
                       fg="#f8f8ff")

    Button(frame, text="Back", fg="crimson",
           command=lambda: _back(back_to_menu)).pack(pady=10)

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter member ID:", bg=bg, fg='white', width=21,
          anchor=W).grid(row=0, column=0, pady=7)
    member_entry = Entry(input_frame, borderwidth=3)
    member_entry.focus_set()
    member_entry.grid(row=0, column=1)
    member_entry.bind("<Escape>", lambda event: back_to_menu())

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg='white',
          width=21, anchor=W).grid(row=1, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=1, column=1)
    # checkout book when Enter is pressed
    ids_entry.bind('<Return>', lambda event: _checkout())
    # go back when Esc is pressed
    ids_entry.bind('<Escape>', lambda event: back_to_menu())

    Button(frame, text="Checkout", command=_checkout).pack(pady=10)

    warning_frame = LabelFrame(frame, text="Warning", padx=1, bg='yellow')
    warning_label = Label(warning_frame, bg=bg, fg='white', wraplength=450,
                          justify=CENTER)
    warning_label.pack()

    status_frame = LabelFrame(frame, padx=1, fg='white')
    status_label = Label(status_frame, bg=bg, fg='white')
    status_label.pack()

    return frame


def _back(back_to_menu: Callable):
    """
    Hide status and go back to main menu.

    :param back_to_menu: the function that changes the frame to the menu frame
    """
    _hide_status()
    back_to_menu()


def _checkout():
    """
    Checkout given book(s) to given member and notify librarian of status.
    """
    _hide_status()

    member_id = member_entry.get()
    ids = ids_entry.get().split(',')

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        _show_status('Error', 'A book ID is invalid (not a number)', 'red')
        return

    error, warning, success = checkout_book(member_id, *ids)

    if error is not None:
        _show_status('Error', error, 'red')

    if warning is not None:
        _show_warning(warning)

    if success is not None:
        _show_status('Success', success, 'green')


def _show_warning(msg):
    """
    Make the warning frame visible with the given warning message.

    :param msg: the warning message
    """
    warning_label.configure(text=msg)
    warning_frame.pack(pady=5)


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
    Hide the warning and status frames.
    """
    warning_frame.pack_forget()
    status_frame.pack_forget()


def checkout_book(member_id: str, *book_ids: int) -> tuple[str | None,
                                                           str | None,
                                                           str | None]:
    """
    Withdraw given book(s) to a given member, update the database and logfile.

    :param member_id: the id of the member who wants to withdraw book(s)
    :param book_ids: the id(s) of the book(s) the member wants to checkout
    :return: (error message, warning message, success message)
    """
    withdrawn = []
    error = lambda msg: (msg, None, _success(withdrawn))

    if len(member_id) != 4:
        return error(f"Error: Invalid member ID: '{member_id}'")

    if not book_ids:
        return error('No books to checkout')

    for book_id in book_ids:
        book = database.search_book_by_id(book_id)

        if book is None:
            return error(f"No book with ID: {book_id}")

        if (member := book['member']) != '0':
            return error("Book %s already on loan, to '%s'" %
                         (book_id, member))

        book['member'] = member_id
        log = database.new_log(book_id, member_id)
        database.logs.append(log)

        withdrawn.append(str(book_id))

    logs = database.logs_for_member_id(member_id)

    held_book_ids = [str(log['book_id']) for log in logs
                     if database.log_is_on_loan(log) and
                     database.is_more_than_60_days_ago(log['checkout'])]

    warning_msg = None

    if held_book_ids:
        warning_msg = f"Book(s) {{{','.join(held_book_ids)}}} are being held" \
                      " for more than 60 days"

    return None, warning_msg, _success(withdrawn)


def _success(withdrawn: list[str]) -> str | None:
    """
    Update database files if books have been withdrawn.

    :param withdrawn: the ids of withdrawn books
    :return: 'success message' of checkout_book
    """
    if not withdrawn:
        return None

    database.update_logfile()
    database.update_database()

    return f"Book(s) {{{','.join(withdrawn)}}} withdrawn"


# tests
def main():
    """
    Main method which contains test code for this module.
    """
    # Modify database methods so files aren't modified while testing
    database.update_database = lambda: None
    database.update_logfile = lambda: None

    print(f"{checkout_book('suii', *[7, 8]) = }")

    print(f"{checkout_book('util', 5) = }")

    print(f"{checkout_book('coaa', 11) = }")

    assert _success([]) is None, '_success failed for empty list'
    assert _success(['1']) == 'Book(s) {1} withdrawn', \
        '_success failed for non-empty list'

    print('bookcheckout.py has passed all tests!')


if __name__ == "__main__":
    main()
