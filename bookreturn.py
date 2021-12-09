"""
This modules provides functionality for the librarian to return books. It asks
for the IDs of the books they wish to return and displays an appropriate error
message or a message letting them know the books have been successfully
returned.

The librarian can enter a member's ID and the books that member has on loan are
displayed. The librarian can then select one of these books and press a button
to return that book.

When a book is returned, the most recent transaction log for that book is
updated to have a return date to signify that the book has been returned.

If a book is being returned after 60 days of being on loan, the librarian is
warned.

Written by Dara Agbola between 8th November and 9th December 2021.
"""

from datetime import datetime
from tkinter import *
from tkinter import ttk

import database

ids_entry: Entry = None

error_frame: LabelFrame = None
error_label: Label = None
warning_frame: LabelFrame = None
warning_label: Label = None
success_frame: LabelFrame = None
success_label: Label = None

member_id: StringVar = None
tree_frame: Frame = None
tree: ttk.Treeview = None
tree_button: Button = None


def get_frame(parent, bg, fg) -> LabelFrame:
    """
    Create and decorate the frame for checking out books.

    :param parent: the parent of the frame
    :param bg: the background color
    :param fg: the foreground color
    :return: the fully decorated frame
    """
    global ids_entry
    global error_frame
    global error_label
    global warning_frame
    global warning_label
    global success_frame
    global success_label

    frame = LabelFrame(parent, text='Book Return', padx=5, pady=5, bg=bg, fg=fg)
    # put columns 0 and 1 in the middle (horizontally)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    _create_on_loan_frame(frame, bg).grid(row=0, column=0, sticky=NS)

    return_frame = Frame(frame, bg=bg)
    return_frame.grid(row=0, column=1, sticky=NS)

    input_frame = Frame(return_frame, bg=bg)
    input_frame.grid()

    Label(input_frame, text="Enter book IDs (split by ','):", bg=bg, fg=fg) \
        .grid(row=0, column=0)
    ids_entry = Entry(input_frame, borderwidth=3)
    ids_entry.grid(row=0, column=1)
    ids_entry.bind('<Return>', _return)

    Button(return_frame, text='Return', command=_return).grid(pady=10)

    error_frame = LabelFrame(return_frame, text='Error', padx=1, pady=5,
                             bg='red', fg=bg)
    # configure the error frame's grid options to be before the warning frame
    error_frame.grid(row=100, pady=5)
    error_label = Label(error_frame, bg=bg, fg=fg, wraplength=300)
    error_label.pack()

    warning_frame = LabelFrame(return_frame, text='Warning', padx=1, pady=5,
                               bg='yellow', fg=bg)
    # configure the warning frame's grid options to be before the success frame
    warning_frame.grid(row=101, pady=5)
    warning_label = Label(warning_frame, bg=bg, fg=fg, wraplength=300)
    warning_label.pack()

    success_frame = LabelFrame(return_frame, text='Error', padx=1, pady=5,
                               bg='green', fg=bg)
    # configure the success frame's grid options to be after the warning frame
    success_frame.grid(row=102, pady=5)
    success_label = Label(success_frame, bg=bg, fg=fg, wraplength=300)
    success_label.pack()

    # hide status frames
    _hide_status()

    return frame


def on_show():
    """
    Hide status when this frame is shown.
    """
    _hide_status()


def _return(*_):
    """
    Return given book(s) and notify librarian of status.

    :param _: unused varargs to allow this to be used as any callback
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
    error, warning, success = return_book(*ids)

    if error is not None:
        _show_status(error, error=True)

    if warning is not None:
        _show_warning(warning)

    if success is not None:
        _show_status(success)

    # update the tree so it doesn't show any books that were just returned
    _books_on_loan_for_member()
    # hide tree_button because nothing will be selected
    tree_button.grid_remove()


def _create_on_loan_frame(parent, bg) -> Frame:
    """
    Create and decorate the frame to show the books that a member currently has
    on loan.

    :param parent: the root frame to put this frame inside
    :param bg: background color of the frame
    :return: the frame
    """
    global member_id
    global tree_frame
    global tree
    global tree_button

    member_id_frame = Frame(parent, bg=bg)

    Label(member_id_frame, text='Member ID:', bg=bg, fg='white').pack()

    member_id = StringVar()
    # show the books the member has on loan when memberID entry is modified
    member_id.trace_add('write', _books_on_loan_for_member)
    Entry(member_id_frame, borderwidth=3, textvariable=member_id).pack()

    tree_frame = Frame(parent, bg=bg, pady=10)

    # there's no need to show memberID as all books shown will be loaned out to
    # the member
    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date')

    tree = ttk.Treeview(tree_frame, columns=headers, show='headings')
    tree.grid(row=0, column=0)

    for header in headers:
        tree.column(header, width=90)
        tree.heading(header, text=header)
    tree.column('ID', anchor=CENTER, width=30)
    tree.column('Purchase Date', anchor=CENTER)

    sb = Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=0, column=1, sticky=NS)

    select_frame = Frame(tree_frame, bg=bg)
    select_frame.grid(row=1, columnspan=2, pady=10)

    Button(select_frame, text='Select All',
           command=lambda: tree.selection_add(*tree.get_children())) \
        .grid(row=0, column=0, padx=10)
    Button(select_frame, text='Deselect All',
           command=lambda: tree.selection_remove(*tree.selection())) \
        .grid(row=0, column=1, padx=10)

    tree_button = Button(tree_frame, wraplength=250, command=_return_selected)
    # configure tree_button grid options to make re-adding easier
    tree_button.grid(row=2, columnspan=2, pady=20)
    tree_button.grid_remove()

    # when a book is selected, update tree_button's text to say the book IDs
    tree.bind('<<TreeviewSelect>>', _update_tree_button)

    return member_id_frame


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
        book_dict = vars(book)
        tree.insert('', index=END, values=tuple(book_dict.values()))

    if books_on_loan:
        tree_frame.place(x=30, y=100)


def _get_selected_book_ids() -> list[int]:
    """
    Return the IDs of the books currently selected in the tree.

    :return: the IDs of the selected books
    """
    # get the iids of the items currently selected in the tree
    selected = tree.selection()
    return [int(tree.set(iid, 'ID')) for iid in selected]


def _return_selected():
    """
    Return the book currently selected in the tree.
    """
    _hide_status()

    book_ids = _get_selected_book_ids()
    _return0(*book_ids)


def _update_tree_button(*_):
    """
    Update the tree button to say the IDs of the currently selected books.

    :param _: unused varargs to allow this to be used as any callback
    """
    book_ids = _get_selected_book_ids()
    text = f"Return {','.join(map(str, book_ids))}"
    tree_button.configure(text=text)

    if book_ids:
        tree_button.grid()
    else:
        tree_button.grid_remove()


def _show_warning(msg):
    """
    Make the warning frame visible with the given warning message.

    :param msg: the warning message
    """
    warning_label.configure(text=msg)
    warning_frame.grid()


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
    warning_frame.grid_remove()
    success_frame.grid_remove()


def return_book(*book_ids: int) -> tuple[str | None, str | None, str | None]:
    """
    Try to return given books, update the database and logfile if successful.

    :param book_ids: the id(s) of the book(s) to return
    :return: (error message, warning message, success message)
    """

    returned = list[str]()
    overdue = list[str]()

    for book_id in book_ids:
        book = database.search_book_by_id(book_id)

        if book is None:
            return (f'No book with ID: {book_id}', _warning(overdue),
                    _success(returned))

        if book.member == '0':
            return (f'Book {book_id} already returned', _warning(overdue),
                    _success(returned))

        book.member = '0'

        book_logs = database.logs_for_book_id(book_id)

        # get the log that was the checkout of this book
        log = None
        for log_ in book_logs:
            if database.log_is_on_loan(log_):
                log = log_
                break

        # update the log, indicating the book has been returned
        if log is not None:
            log['return'] = datetime.now()
            if database.is_more_than_60_days_ago(log['checkout']):
                overdue.append(str(book_id))

        returned.append(str(book_id))

    return None, _warning(overdue), _success(returned)


def _success(returned: list[str]) -> str | None:
    """
    Update database files if books have been returned.

    :param returned: the ids of returned books
    :return: 'success message' of def return_book
    """
    if not returned:
        return None

    database.update_logfile()
    database.update_database()

    return f"Book(s) {','.join(returned)} returned"


def _warning(overdue: list[str]) -> str | None:
    """
    Return the warning message for def return_book given an amount of overdue
    books.

    :param overdue: the IDs of books that were returned after 60 days
    :return: 'warning message' of def return_book
    """
    if not overdue:
        return None

    if len(overdue) == 1:
        return f'Book {overdue[0]} was returned after 60 days'
    else:
        return f"Books {','.join(overdue)} were returned after 60 days"


def test():
    """
    Main method which contains test code for this module.
    """
    # Modify database methods so files aren't modified while testing
    database.update_database = lambda: None
    database.update_logfile = lambda: None

    assert return_book() == (None, None, None), 'return_book failed for no input'

    assert _success([]) is None, '_success failed for empty list'

    print(f'{return_book(1) = }')

    print('bookreturn.py has passed all tests!')


if __name__ == "__main__":
    test()
