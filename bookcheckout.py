"""
This module provides functionality to check out books. It asks the librarian for
the borrower's member ID and the ID of the book(s) they wish to withdraw.

It checks all inputs are valid, displaying any errors and warnings. If the book
is available, its status is updated in the database and the logfile is updated
with a new entry to signify that the book has been withdrawn.

If the member is currently holding any books for more than 60 days, a warning
message is shown to the librarian about these books.

Written by F120840 between 8th November and 16th December 2021.
"""

from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from typing import List, Tuple, Optional

import database

tree: ttk.Treeview
tree_button: Button

member_entry: Entry
ids_entry: Entry

warning_frame: LabelFrame
error_frame: LabelFrame
success_frame: LabelFrame


def get_frame(parent, bg, fg) -> LabelFrame:
    """
    Create and decorate the frame for checking out books.

    :param parent: the parent of the frame
    :param bg: the background color
    :param fg: the foreground color
    :return: the fully decorated frame
    """
    global member_entry
    global ids_entry

    global warning_frame
    global error_frame
    global success_frame

    frame = LabelFrame(parent, text='Book Checkout', padx=5, pady=5, bg=bg,
                       fg=fg)
    # put columns 0 and 1 in the middle (horizontally)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    _create_available_frame(frame, bg).grid(row=0, column=0, sticky=NS)

    checkout_frame = Frame(frame, bg=bg)
    checkout_frame.grid(row=0, column=1, sticky=NS)

    input_frame = Frame(checkout_frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text='Enter member ID:', bg=bg, fg=fg, width=21,
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

    Button(checkout_frame, text='Checkout', command=_checkout).pack(pady=10)

    warning_frame = LabelFrame(checkout_frame, text='Warning', padx=1,
                               bg='yellow')
    Label(warning_frame, bg=bg, fg=fg, wraplength=300).pack()

    error_frame = LabelFrame(checkout_frame, text='Error', padx=1, bg='red')
    Label(error_frame, bg=bg, fg=fg, wraplength=300).pack()

    success_frame = LabelFrame(checkout_frame, text='Success', padx=1,
                               bg='green')
    Label(success_frame, bg=bg, fg=fg, wraplength=300).pack()

    return frame


def on_show():
    """
    Hide status, set focus on the member ID entry and update book tree when this
    frame is shown.
    """
    _hide_status()
    member_entry.focus_set()
    _update_book_tree()


def _create_available_frame(parent, bg) -> Frame:
    """
    Create and decorate the frame to show all currently available books.

    :param parent: the root frame to put this frame inside
    :param bg: background color of the frame
    :return: the frame
    """
    global tree
    global tree_button

    frame = Frame(parent, bg=bg)

    label = Label(frame, text='Available Books:', font='Lucida 12 bold', bg=bg,
                  fg='white')
    label.grid(row=0, columnspan=2, pady=13)
    # underline the label
    font = Font(label, label.cget('font'))
    font.configure(underline=True)
    label.configure(font=font)

    # there's no need to show memberID as all books will be available
    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date')

    tree = ttk.Treeview(frame, columns=headers, show='headings')
    tree.grid(row=1, column=0)

    for header in headers:
        tree.column(header, width=90)
        tree.heading(header, text=header)
    tree.column('ID', anchor=CENTER, width=30)
    tree.column('Purchase Date', anchor=CENTER)

    sb = Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=1, column=1, sticky=NS)

    tree_button = Button(frame, wraplength=300, command=_checkout_selected)
    # configure tree_button grid options to make re-adding easier
    tree_button.grid(row=2, columnspan=2, pady=20)
    tree_button.grid_remove()

    # when a book is selected, update tree_button's text to say the book IDs
    tree.bind('<<TreeviewSelect>>', _update_tree_button)

    return frame


def _update_book_tree():
    """
    Update book tree to show all available books.
    """
    # clear tree
    tree.delete(*tree.get_children())

    # we only want to show available books
    available_books = database.search_books_by_param('member', '0')

    for book in available_books:
        book_dict = vars(book)
        tree.insert('', index=END, values=tuple(book_dict.values()))


def _get_selected_book_ids() -> List[int]:
    """
    Get the IDs of the books currently selected in the tree.

    :return: the IDs of the selected books
    """
    # get the iids of the items currently selected in the tree
    selected = tree.selection()
    return [tree.item(iid)['values'][0] for iid in selected]


def _update_tree_button(*_):
    """
    Update the tree button to say the IDs of the books currently selected in the
    tree.

    :param _: unused varargs to allow this to be used as any callback
    """
    book_ids = _get_selected_book_ids()
    text = 'Checkout ' + ','.join(map(str, book_ids))
    tree_button.configure(text=text)

    if book_ids:
        tree_button.grid()
    else:
        tree_button.grid_remove()


def _checkout():
    """
    Checkout given book(s) to given member and notify librarian of status.
    """
    _hide_status()

    member_id = member_entry.get()
    ids = ids_entry.get().split(',')

    if len(ids) != len(set(ids)):
        _show_status('Duplicate book IDs entered', error=True)
        return

    try:
        ids = [int(book_id) for book_id in ids]
    except ValueError:
        _show_status('A book ID is invalid (not a number)', error=True)
        return

    _checkout0(member_id, ids)


def _checkout0(member_id, ids: List[int]):
    """
    Checkout given book(s) to given member and notify librarian of status.

    :param member_id: the ID of the member who is taking books out
    :param ids: the IDs of the books to checkout
    """
    error, warning, success = checkout_book(member_id, *ids)

    if error is not None:
        _show_status(error, error=True)

    if warning is not None:
        _show_warning(warning)

    if success is not None:
        _show_status(success)

    # update the tree so it doesn't show any books that were just checked out
    _update_book_tree()
    # hide tree_button because nothing will be selected
    tree_button.grid_remove()


def _checkout_selected():
    """
    Checkout the books currently selected in the tree to given member and notify
    librarian of status.
    """
    _hide_status()

    member_id = member_entry.get()
    ids = _get_selected_book_ids()

    _checkout0(member_id, ids)


def _show_warning(msg):
    """
    Make the warning frame visible with the given warning message.

    :param msg: the warning message
    """
    warning_label = warning_frame.pack_slaves()[0]
    warning_label.configure(text=msg)
    warning_frame.pack(pady=5)


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

    frame.pack(pady=5)


def _hide_status():
    """
    Hide the status frames.
    """
    warning_frame.pack_forget()
    error_frame.pack_forget()
    success_frame.pack_forget()


def checkout_book(member_id: str, *book_ids: int) -> Tuple[Optional[str],
                                                           Optional[str],
                                                           Optional[str]]:
    """
    Withdraw given book(s) to a given member, and update the database and
    logfile.

    :param member_id: the ID of the member to withdraw book(s) to
    :param book_ids: the ID(s) of the book(s) the member wants to check out
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
            return error(f'No book with ID: {book_id}')

        if (member := book.member) != '0':
            return error(f'Book {book_id} is already on loan, to: {member}')

        book.member = member_id
        database.logs.append(database.new_log(book_id, member_id))

        withdrawn.append(str(book_id))

    # get the IDs of the books the member has had on loan for more than 60 days
    logs = database.logs_for_member_id(member_id)
    held_book_ids = sorted(log['book_id'] for log in logs
                           if database.is_log_on_loan(log) and
                           database.is_more_than_60_days_ago(log['checkout'])
                           )

    warning_msg = None

    if held_book_ids:
        if len(held_book_ids) == 1:
            warning_msg = f'Book {held_book_ids[0]} is being held for more ' \
                          'than 60 days'
        else:
            warning_msg = f"Books {','.join(map(str, held_book_ids))} are " \
                          "being held for more than 60 days"

    return None, warning_msg, _success(withdrawn)


def _success(withdrawn: List[str]) -> Optional[str]:
    """
    Update database files if books have been withdrawn, and generate a success
    message for checkout_book.

    :param withdrawn: the ids of withdrawn books
    :return: 'success message' of checkout_book
    """
    if not withdrawn:
        return None

    database.update_logfile()
    database.update_database()

    if len(withdrawn) == 1:
        ...
        return f'Book {withdrawn[0]} withdrawn'
    else:
        return f"Books {','.join(withdrawn)} withdrawn"


def test():
    """
    Main method which contains test code for this module.
    """
    # Temporarily modify database methods so files aren't modified while testing
    temp = database.update_database, database.update_logfile
    database.update_database = database.update_logfile = lambda: None

    assert checkout_book('suii', 7, 8) == \
           (None,
            'Books 4,45,48,49,59,60,73,75 are being held for more than 60 days',
            'Books 7,8 withdrawn')

    assert checkout_book('util', 5) == ('Book 5 is already on loan, to: coaa',
                                        None, None)

    assert checkout_book('test', 15) == (None, None, 'Book 15 withdrawn')

    assert _success([]) is None, '_success failed for empty list'
    assert _success(['1']) == 'Book 1 withdrawn', \
        '_success failed for non-empty list'

    print('bookcheckout.py has passed all tests!')

    database.update_database, database.update_logfile = temp


if __name__ == "__main__":
    test()
