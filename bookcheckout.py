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

import database

member_entry: Entry = None
ids_entry: Entry = None

warning_frame: LabelFrame = None
warning_label: Label = None

error_frame: LabelFrame = None
error_label: Label = None

success_frame: LabelFrame = None
success_label: Label = None


def get_frame(parent) -> LabelFrame:
    """
    Create and decorate the frame for checking out books.

    :param parent: the parent of the frame
    :return: the fully decorated frame
    """
    global member_entry
    global ids_entry

    global warning_frame
    global warning_label
    global error_frame
    global error_label
    global success_frame
    global success_label

    bg, fg = 'black', '#f8f8ff'

    frame = LabelFrame(parent, text="Book Checkout", padx=5, pady=5, bg=bg,
                       fg=fg)

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter member ID:", bg=bg, fg=fg, width=21,
          anchor=W).grid(row=0, column=0, pady=7)
    member_entry = Entry(input_frame, borderwidth=3)
    member_entry.focus_set()
    member_entry.grid(row=0, column=1)

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg=fg,
          width=21, anchor=W).grid(row=1, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=1, column=1)
    # checkout book when Enter is pressed
    ids_entry.bind('<Return>', lambda event: _checkout())

    Button(frame, text="Checkout", command=_checkout).pack(pady=10)

    warning_frame = LabelFrame(frame, text="Warning", padx=1, bg='yellow')
    warning_label = Label(warning_frame, bg=bg, fg=fg, wraplength=450,
                          justify=CENTER)
    warning_label.pack()

    error_frame = LabelFrame(frame, text="Error", padx=1, bg='red')
    error_label = Label(error_frame, bg=bg, fg=fg, wraplength=450,
                        justify=CENTER)
    error_label.pack()

    success_frame = LabelFrame(frame, text="Success", padx=1, bg='green')
    success_label = Label(success_frame, bg=bg, fg=fg, wraplength=450,
                          justify=CENTER)
    success_label.pack()

    return frame


def on_show():
    """
    Hide status and set focus on the member ID entry when this frame is shown.
    """
    _hide_status()
    member_entry.focus_set()


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
        _show_status('A book ID is invalid (not a number)', error=True)
        return

    error, warning, success = checkout_book(member_id, *ids)

    if error is not None:
        _show_status(error, error=True)

    if warning is not None:
        _show_warning(warning)

    if success is not None:
        _show_status(success)


def _show_warning(msg):
    """
    Make the warning frame visible with the given warning message.

    :param msg: the warning message
    """
    warning_label.configure(text=msg)
    warning_frame.pack(pady=5)


def _show_status(msg, error=False):
    """
    Configure the relevant status frame to show the given message and display
    it.

    :param msg: the status message
    :param error: whether the status is an error or not
    """
    if error:
        label, frame = error_label, error_frame
    else:
        label, frame = success_label, success_frame

    label.configure(text=msg)
    frame.pack(pady=5)


def _hide_status():
    """
    Hide the status frames.
    """
    warning_frame.pack_forget()
    error_frame.pack_forget()
    success_frame.pack_forget()


def checkout_book(member_id: str, *book_ids: int) -> tuple[str | None,
                                                           str | None,
                                                           str | None]:
    """
    Withdraw given book(s) to a given member, update the database and logfile.

    :param member_id: the ID of the member who wants to withdraw book(s)
    :param book_ids: the ID(s) of the book(s) the member wants to checkout
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

        if (member := book.member) != '0':
            return error(f"Book {book_id} is already on loan, to '{member}'")

        book.member = member_id
        log = database.new_log(book_id, member_id)
        database.logs.append(log)

        withdrawn.append(str(book_id))

    logs = database.logs_for_member_id(member_id)

    held_book_ids = [str(log['book_id']) for log in logs
                     if database.log_is_on_loan(log) and
                     database.is_more_than_60_days_ago(log['checkout'])]
    held_book_ids.sort(key=int)

    warning_msg = None

    if held_book_ids:
        warning_msg = f"Book(s) {{{','.join(held_book_ids)}}} are being held " \
                      "for more than 60 days"

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
