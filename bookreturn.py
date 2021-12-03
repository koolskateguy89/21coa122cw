"""
This modules provides functionality for the librarian to return books. It asks
for the ID of the books they wish to return and either displays an appropriate
error message or a message letting them know the books have been successfully
returned.

The librarian can enter a member's ID and the books that member has on loan are
displayed. The librarian can then select one of these books and press a button
to return that book.

When a book is returned, the most recent transaction log for that book is
updated with a return date to signify that the book has been returned.
"""

from datetime import datetime
from tkinter import *
from tkinter import ttk

import database

ids_entry: Entry = None

error_frame: LabelFrame = None
error_label: Label = None

success_frame: LabelFrame = None
success_label: Label = None

member_id: StringVar = None
tree_frame: Frame = None
tree: ttk.Treeview = None
tree_button: Button = None


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
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    _create_on_loan_frame(frame, bg)

    return_frame = Frame(frame, bg=bg)
    return_frame.grid(row=0, column=1, sticky=NS)

    input_frame = Frame(return_frame, bg=bg)
    input_frame.grid()

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg=fg) \
        .grid(row=0, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=0, column=1)

    Button(return_frame, text="Return", command=_return).grid(pady=10)

    error_frame = LabelFrame(return_frame, text="Error", padx=1, pady=5, bg='red',
                             fg=bg)
    # configure the error frame's grid options to be before the success frame
    error_frame.grid(row=100, pady=5)
    error_frame.grid_remove()
    error_label = Label(error_frame, bg=bg, fg=fg)
    error_label.pack()

    success_frame = LabelFrame(return_frame, text="Error", padx=1, pady=5, bg='green',
                               fg=bg)
    # configure the success frame's grid options to be after the error frame
    success_frame.grid(row=101, pady=5)
    success_frame.grid_remove()
    success_label = Label(success_frame, bg=bg, fg=fg)
    success_label.pack()

    return frame


def on_show():
    """
    Hide status when this frame is shown.
    """
    _hide_status()


def _return():
    """
    Return given book(s) and notify librarian of status.
    """
    _hide_status()
    ids = ids_entry.get().split(',')

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        _show_status('Book IDs are invalid (not a number)', error=True)
        return

    _return0(*ids)


def _return0(*ids: int):
    """
    Return given book(s) and display status.

    :param ids: the ID's of the books to return
    """
    error, success = return_book(*ids)

    if error is not None:
        _show_status(error, error=True)

    if success is not None:
        _show_status(success)


def _create_on_loan_frame(parent, bg):
    """
    Create a decorate the frame to show the books that a member currently has on
    loan.

    :param parent: the root frame to put this frame inside
    :param bg: background colour
    """
    global member_id
    global tree_frame
    global tree
    global tree_button

    member_id_frame = Frame(parent, bg=bg)
    member_id_frame.grid(row=0, column=0, sticky=NS)

    Label(member_id_frame, text="Member ID:", bg=bg, fg='white').pack()

    member_id = StringVar()
    # show the books the member has on loan when memberID entry is modified
    member_id.trace_add('write', _books_on_loan_for_member)
    Entry(member_id_frame, borderwidth=3, textvariable=member_id).pack()

    tree_frame = Frame(parent, bg=bg, pady=10)

    # there's no need to show memberID
    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date')

    tree = ttk.Treeview(tree_frame, columns=headers, show='headings')
    tree.grid(row=0, column=0)

    for header in headers:
        tree.column(header, width=70)
        tree.heading(header, text=header)
    tree.column('ID', anchor=CENTER, width=30)

    sb = Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=0, column=1, sticky=NS)

    tree_button = Button(tree_frame, command=_return_tree)
    # configure tree_button grid options to make re-adding easier
    tree_button.grid(row=1, columnspan=2, pady=20)
    tree_button.grid_remove()

    # when a book is selected, update tree_button's text to say the book ID
    tree.bind('<ButtonRelease-1>', _update_tree_button)


def _books_on_loan_for_member(*_):
    """
    Display the books that a given member currently has on loan.

    :param _: unused varargs to allow this to be used as any callback
    """
    # hide and clear tree
    tree_frame.place_forget()
    tree.delete(*tree.get_children())

    member = member_id.get()

    books_on_loan = database.search_books_by_param('member', member).values()
    for book in books_on_loan:
        book = vars(book)
        tree.insert('', index=END, values=tuple(book.values()))

    if books_on_loan:
        tree_frame.place(x=30, y=100)


def _get_selected_book() -> int | None:
    """
    Return the ID of the book currently selected in the tree.

    :return: the ID of the selected book
    """
    # get the selected item in the tree
    selected_item = tree.item(tree.focus())
    book_as_list = selected_item['values']

    return None if not book_as_list else book_as_list[0]


def _update_tree_button(*_):
    """
    Update the tree button to say the ID of the currently selected book.

    :param _: unused varargs to allow this to be used as any callback
    """
    book_id = _get_selected_book()
    if book_id is not None:
        tree_button.configure(text=f'Return {book_id}')
        tree_button.grid()


def _return_tree():
    """
    Return the book currently selected in the tree.
    """
    _hide_status()

    book_id = _get_selected_book()
    _return0(book_id)

    # update the tree so it doesn't show the book that was just returned
    _books_on_loan_for_member()
    # hide tree_button because the selected book has been returns
    tree_button.grid_remove()


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
        for log_ in book_logs:
            if database.log_is_on_loan(log_):
                log = log_
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
