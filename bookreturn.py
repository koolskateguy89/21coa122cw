"""
This modules provides functionality for the librarian to return books. It asks
for the ID of the books they wish to return and either displays an appropriate
error message or a message letting them know the books have been successfully
returned.

When a book is returned, the most recent transaction log for that book is
updated with a return date to signify that the book has been returned.
"""

# TODO:

"""
Enter user ID,
display the books they have on loan,
and pick which books to return
"""

from datetime import datetime
from tkinter import *
from tkinter import ttk

from database import date_to_str

import database

ids_entry: Entry = None

error_frame: LabelFrame = None
error_label: Label = None

success_frame: LabelFrame = None
success_label: Label = None

member_id: StringVar = None
tree_frame: Frame = None
tree: ttk.Treeview = None


def get_frame(parent) -> LabelFrame:
    """
    Create and decorate the frame for checking out books.

    :param parent: the parent of the frame
    :return: the fully decorated frame
    """
    global ids_entry
    global error_frame
    global error_label
    global success_frame
    global success_label

    bg, fg = 'black', '#f8f8ff'

    frame = LabelFrame(parent, text="Book Return", padx=5, pady=5, bg=bg, fg=fg)

    _create_search_frame(frame, bg)

    input_frame = Frame(frame, bg=bg)
    input_frame.grid(column=1)

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg=fg) \
        .grid(row=0, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=0, column=1)
    # return book when Enter is pressed
    ids_entry.bind('<Return>', lambda event: _return())

    return_button = Button(frame, text="Return", command=_return)
    return_button.grid(column=1, pady=10)

    error_frame = LabelFrame(frame, text="Error", padx=1, pady=5, bg='red',
                             fg=bg)
    # configure the error frame's grid options
    error_frame.grid(row=100, column=1, pady=5);
    error_frame.grid_remove()
    error_frame.grid_remove()
    error_label = Label(error_frame, bg=bg, fg=fg)
    error_label.pack()

    success_frame = LabelFrame(frame, text="Error", padx=1, pady=5, bg='green',
                               fg=bg)
    # configure the success frame's grid options
    success_frame.grid(row=101, column=1, pady=5);
    success_frame.grid_remove()
    success_label = Label(success_frame, bg=bg, fg=fg)
    success_label.pack()

    return frame


def on_show():
    """
    Hide status and set focus on the book IDs entry when this frame is shown.
    """
    _hide_status()
    ids_entry.focus_set()


def _create_search_frame(root, bg):
    global member_id
    global tree_frame
    global tree

    frame = Frame(root, bg=bg)
    frame.grid(row=0, column=0, rowspan=101)

    Label(frame, text="Member ID:", bg=bg, fg='white').pack()

    member_id = StringVar()
    # TODO: comment about update tree as typing or smthn
    member_id.trace_add('write', _member_books_on_loan)
    member_id_entry = Entry(frame, borderwidth=3, textvariable=member_id)
    # TODO: comment about update tree when enter is pressed
    member_id_entry.bind('<Return>', _member_books_on_loan)
    member_id_entry.pack()

    tree_frame = Frame(frame, bg=bg)
    #tree_frame.pack()

    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date', 'Member')
    tree = ttk.Treeview(tree_frame, columns=headers, show='headings')
    tree.grid(row=0, column=0, sticky=NSEW)

    for header in headers:
        tree.column(header, width=40)
        tree.heading(header, text=header)

    sb = Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=0, column=1, sticky=NS)


def _member_books_on_loan(*args):
    print(f'{args = }')

    # hide and clear tree
    tree_frame.pack_forget()
    tree.delete(*tree.get_children())

    member = member_id.get()

    books_on_loan = database.search_books_by_param('member', member).values()
    for book in books_on_loan:
        book = {**vars(book),
                'purchase_date': date_to_str(book.purchase_date),
                }

        tree.insert('', index=END, values=tuple(book.values()))

    if books_on_loan:
        tree_frame.pack()
    ...


def _return():
    """
    Return given book(s) and notify librarian of status.
    """
    _hide_status()
    ids = ids_entry.get().split(',')

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        _show_status('A book ID is invalid (not a number)', error=True)
        return

    error, success = return_book(*ids)

    if error is not None:
        _show_status(error, error=True)

    if success is not None:
        _show_status(success)


def _show_status(msg, error=False):
    """
    Configure the relevant status frame to show the given message and display
    it.

    :param msg: the status message
    :param error: True if the status is an error
    """
    if error:
        label, frame = error_label, error_frame
    else:
        label, frame = success_label, success_frame

    label.configure(text=msg)
    frame.grid()


def _hide_status():
    """
    Hide the status frames.
    """
    error_frame.grid_remove()
    success_frame.grid_remove()


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

        if book.member == '0':
            return f"Book {book_id} already returned", _success(returned)

        book.member = '0'

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
