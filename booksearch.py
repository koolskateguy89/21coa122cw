"""
This module provides the functionality for searching for books, this is done by
using the database module to query the book database.
"""

from tkinter import *
from tkinter.ttk import Treeview, Style
from typing import Callable

import database
from database import date_to_str

frame: LabelFrame = None
title_entry: Entry = None
results_wrapper: Frame = None
tree: Treeview = None
style: Style = None


def get_frame(parent, back_to_menu: Callable) -> LabelFrame:
    """
    Lazily create the frame for searching for books and set focus on
    the title entry.

    :param parent: the parent of the frame
    :param back_to_menu: function that returns back to menu
    :return: the fully decorated frame
    """
    global frame
    global title_entry
    global results_wrapper

    if frame is not None:
        title_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Search", padx=5, pady=5, bg=bg,
                       fg="white")
    # put everything in the middle (horizontally)
    frame.grid_columnconfigure(0, weight=1)

    Button(frame, text="Back", fg="crimson",
           command=lambda: _back(back_to_menu)).grid(row=0, column=0)

    # embed a frame for a label and title_entry so they can be side-by-side
    # without affecting rest of layout
    title_frame = Frame(frame, bg=bg)

    Label(title_frame, text="Enter book title:", bg=bg, fg="white").grid(
        row=0, column=0)
    title_entry = Entry(title_frame, bg="white", fg=bg, width=30, borderwidth=1)
    title_entry.focus_set()
    # search when enter is pressed
    title_entry.bind('<Return>', lambda event: _search())
    # go back when Esc is pressed
    title_entry.bind('<Escape>', lambda event: _back(back_to_menu))

    title_entry.grid(row=0, column=1)
    title_frame.grid(row=2, column=0, pady=10)

    Button(frame, text="Search", command=_search).grid(row=3, column=0)

    _generate_results_view()

    return frame


def _back(back_to_menu: Callable):
    """
    Hide results and go back to main menu.

    :param back_to_menu: the function that changes the frame to the menu frame
    """
    hide_results()
    back_to_menu()


def _generate_results_view():
    """
    Generate the widgets which will directly display the results, ready to be
    added to the main frame.
    """
    global results_wrapper
    global tree

    _fix_treemap_color()

    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date', 'Member')

    results_wrapper = Frame(frame)
    tree = Treeview(results_wrapper, columns=headers, show='headings')
    tree.tag_configure('highlight', background='yellow', font=('Arial Bold', 9))
    tree.grid(row=0, column=0, sticky='nsew')

    for header in headers:
        tree.column(header, width=90)
        tree.heading(header, text=header)

    tree.column('ID', anchor=CENTER, width=30)

    sb = Scrollbar(results_wrapper, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=0, column=1, sticky='ns')


def _fix_treemap_color():
    """
    Fix a Tkinter big, see https://stackoverflow.com/a/57009674/17381629.
    """
    global style

    fixed_map = lambda option: \
        [elm for elm in style.map('Treeview', query_opt=option)
         if elm[:2] != ('!disabled', '!selected')]

    style = Style()
    style.map('Treeview', foreground=fixed_map('foreground'),
              background=fixed_map('background'))


def _search():
    """
    Perform a search then display the results on screen.
    """
    _clear_results()

    title = title_entry.get()
    results: list[dict] = _search_by_title(title)

    for book in results:
        tags = ('highlight',) if _should_highlight(book) else ()

        # mutate some values to give librarian a better experience
        book = {**book,
                # display appropriate string representation of date
                'purchase_date': date_to_str(book['purchase_date']),
                # if book is available, don't show anyone as member
                'member': member if (member := book['member']) != '0' else ''
                }

        tree.insert('', END, values=tuple(book.values()), tags=tags)

    display_results()


def display_results():
    """
    Display search results on screen.
    """
    results_wrapper.grid(row=4, column=0, pady=10)


def hide_results():
    """
    Hide search results.
    """
    results_wrapper.grid_forget()


def _clear_results():
    """
    Removes all items from the tree
    """
    tree.delete(*tree.get_children())


def _search_by_title(title) -> list[dict]:
    """
    Return all books with the given title.

    :param title: the search param
    :return: list of books with the given title
    """
    result: dict[int, dict] = database.search_books_by_param('title', title)

    return list(result.values())


def _should_highlight(book: dict) -> bool:
    """
    Return whether a given book should be highlighted due to it being on loan
    for more than 60 days.
    
    :param book: the book to check
    :return: whether the book should be highlighted
    """
    logs: list[dict] = database.logs_for_book_id(book['id'])

    for log in logs:
        if (database.log_is_on_loan(log) and
                database.is_more_than_60_days_ago(log['checkout'])):
            return True

    return False


# tests
if __name__ == "__main__":
    f = lambda results: (
        [book for book in results if _should_highlight(book)],
        [book for book in results if not _should_highlight(book)]
    )

    # len(highlight) = 6, len(normal) = 4
    _highlight, _normal = f(_search_by_title(title="Sinful Duty"))
    assert len(_highlight) == 6 and len(_normal) == 4, \
        'search failed for Sinful Duty'

    # len(highlight) = 8, len(normal) = 2
    _highlight, _normal = f(
        _search_by_title(title="Secret of the Misshapen Headmaster")
    )
    assert len(_highlight) == 8 and len(_normal) == 2, \
        'search failed for Secret of the Misshapen Headmaster'

    # len(highlight) = 9, len(normal) = 11
    _highlight, _normal = f(_search_by_title(title="Avengers"))
    assert len(_highlight) and len(_normal) == 9, 'search failed for Avengers'

    print('booksearch.py has passed all tests!')
