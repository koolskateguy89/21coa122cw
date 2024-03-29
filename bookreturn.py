"""
This module provides functionality for the librarian to return books. It asks
for the ID(s) of the book(s) to return and displays an appropriate error or
success message if books have been successfully returned.

The librarian can enter a member's ID and the books that member currently has
on loan are displayed. The librarian can then select from these books to return.

When a book is returned, the most recent transaction log for that book is
updated to include a return date to signify that the book has been returned.

If a book is being returned more than 60 days after it was checked out, the
librarian is warned.

Written by F120840 between 8th November and 16th December 2021.
"""

from datetime import datetime
from tkinter import *
from tkinter import ttk
from typing import List, Tuple, Optional

import database

ids_entry: Entry

error_frame: LabelFrame
warning_frame: LabelFrame
success_frame: LabelFrame

# member_var needs to be global as when it's local, its trace seems to be
# removed for some reason
member_var: StringVar
member_entry: Entry
tree_frame: Frame
tree: ttk.Treeview
tree_button: Button


def get_frame(parent, bg, fg) -> LabelFrame:
    """
    Create and decorate the frame for returning books.

    :param parent: the parent of the frame
    :param bg: the background color
    :param fg: the foreground color
    :return: the fully decorated frame
    """
    global ids_entry
    global error_frame
    global warning_frame
    global success_frame

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
    Label(error_frame, bg=bg, fg=fg, wraplength=300).pack()

    warning_frame = LabelFrame(return_frame, text='Warning', padx=1, pady=5,
                               bg='yellow', fg=bg)
    # configure the warning frame's grid options to be before the success frame
    warning_frame.grid(row=101, pady=5)
    Label(warning_frame, bg=bg, fg=fg, wraplength=300).pack()

    success_frame = LabelFrame(return_frame, text='Error', padx=1, pady=5,
                               bg='green', fg=bg)
    # configure the success frame's grid options to be after the warning frame
    success_frame.grid(row=102, pady=5)
    Label(success_frame, bg=bg, fg=fg, wraplength=300).pack()

    # hide status frames as they were made visible to configure their grid
    # options
    _hide_status()

    return frame


def on_show():
    """
    Hide status and set focus on the member ID entry when this frame is shown.
    """
    _hide_status()
    member_entry.focus_set()


def _return(*_):
    """
    Return given book(s) and notify librarian of status.

    :param _: unused varargs to allow this to be used as any callback
    """
    _hide_status()
    ids = ids_entry.get().split(',')

    if len(ids) != len(set(ids)):
        _show_status('Duplicate book IDs entered', error=True)
        return

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
    global member_var
    global member_entry
    global tree_frame
    global tree
    global tree_button

    member_id_frame = Frame(parent, bg=bg)

    Label(member_id_frame, text='Member ID:', bg=bg, fg='white').pack()

    member_var = StringVar(member_id_frame)
    # show the books the member has on loan when memberID entry is modified
    member_var.trace_add('write', _books_on_loan_for_member)
    member_entry = Entry(member_id_frame, borderwidth=3,
                         textvariable=member_var)
    member_entry.pack()

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

    member = member_entry.get()

    books_on_loan = database.search_books_by_param('member', member)
    for book in books_on_loan:
        book_dict = vars(book)
        tree.insert('', index=END, values=tuple(book_dict.values()))

    if books_on_loan:
        tree_frame.place(x=30, y=100)


def _get_selected_book_ids() -> List[int]:
    """
    Return the IDs of the books currently selected in the tree.

    :return: the IDs of the selected books
    """
    # get the iids of the items currently selected in the tree
    selected = tree.selection()
    return [int(tree.set(iid, 'ID')) for iid in selected]


def _return_selected():
    """
    Return the book(s) currently selected in the tree.
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
    text = 'Return ' + ','.join(map(str, book_ids))
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
    warning_label = warning_frame.pack_slaves()[0]
    warning_label.configure(text=msg)
    warning_frame.grid()


def _show_status(msg, error=False):
    """
    Configure the relevant status frame to show the given message and display
    it.

    :param msg: the status message
    :param error: whether the status is an error or not
    """
    frame = error_frame if error else success_frame

    label = frame.pack_slaves()[0]
    label.configure(text=msg)

    frame.grid()


def _hide_status():
    """
    Hide the status frames.
    """
    error_frame.grid_remove()
    warning_frame.grid_remove()
    success_frame.grid_remove()


def return_book(*book_ids: int) -> Tuple[Optional[str], Optional[str],
                                         Optional[str]]:
    """
    Try to return given books, update the database and logfile if successful.

    :param book_ids: the id(s) of the book(s) to return
    :return: (error message, warning message, success message)
    """

    returned: List[str] = []
    overdue: List[str] = []

    for book_id in book_ids:
        book = database.search_book_by_id(book_id)

        if book is None:
            return (f'No book with ID: {book_id}', _warning(overdue),
                    _success(returned))

        if book.member == '0':
            return (f'Book {book_id} already returned', _warning(overdue),
                    _success(returned))

        book.member = '0'

        # the log that was the checkout of this book is the most recent one
        most_recent_log = database.most_recent_log_for_book_id(book.id)

        # update the log, indicating the book has been returned
        most_recent_log['return'] = datetime.now()

        returned.append(str(book_id))
        if database.is_more_than_60_days_ago(most_recent_log['checkout']):
            overdue.append(str(book_id))

    return None, _warning(overdue), _success(returned)


def _success(returned: List[str]) -> Optional[str]:
    """
    Update database files if books have been returned and generate the success
    message for def return_book given a list of returned books.

    :param returned: the ids of returned books
    :return: 'success message' of def return_book
    """
    if not returned:
        return None

    database.update_logfile()
    database.update_database()

    if len(returned) == 1:
        return f"Book {returned[0]} returned"
    else:
        return f"Books {','.join(returned)} returned"


def _warning(overdue: List[str]) -> Optional[str]:
    """
    Return the warning message for def return_book given a list of overdue
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
    # Temporarily modify database methods so files aren't modified while testing
    temp = database.update_database, database.update_logfile
    database.update_database = database.update_logfile = lambda: None

    assert return_book() == (None, None, None), \
        'return_book failed for no input'

    assert _success([]) is None, '_success failed for empty list'

    assert return_book(1) == (None,
                              'Book 1 was returned after 60 days',
                              'Book 1 returned')

    print('bookreturn.py has passed all tests!')

    database.update_database, database.update_logfile = temp


if __name__ == "__main__":
    test()
