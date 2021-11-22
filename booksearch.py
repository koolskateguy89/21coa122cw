"""
This module provides the functionality for searching for books, this is done by
using the database module to query the book database.

The search function allows casing to be ignored and to search for books whose
title contains the given search query.
"""

from tkinter import *
from tkinter.ttk import Treeview
from typing import Callable

import database
from database import date_to_str

frame: LabelFrame = None

title_entry: Entry = None
ignore_case: IntVar = None
contains: IntVar = None

results_wrapper: Frame = None
tree: Treeview = None


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
    global ignore_case
    global contains
    global results_wrapper

    if frame is not None:
        title_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Search", padx=5, pady=5, bg=bg,
                       fg='white')

    Button(frame, text="Back", fg='crimson',
           command=lambda: _back(back_to_menu)).pack()

    # embed a frame for a label and title_entry so they can be side-by-side
    # without affecting rest of layout
    title_frame = Frame(frame, bg=bg)

    Label(title_frame, text="Enter book title:", bg=bg, fg='white').grid(
        row=0, column=0)
    title_entry = Entry(title_frame, bg='white', fg=bg, width=30, borderwidth=1)
    title_entry.focus_set()
    # search when enter is pressed
    title_entry.bind('<Return>', lambda event: _search())
    # go back when Esc is pressed
    title_entry.bind('<Escape>', lambda event: _back(back_to_menu))

    title_entry.grid(row=0, column=1)
    title_frame.pack(pady=7)

    ignore_case = IntVar()
    Checkbutton(frame, text="Ignore case", bg='white', fg=bg,
                activebackground='white', activeforeground=bg,
                variable=ignore_case).pack(pady=5)

    contains = IntVar()
    Checkbutton(frame, text="Contains", bg='white', fg=bg,
                activebackground='white', activeforeground=bg,
                variable=contains).pack(pady=5)

    Button(frame, text="Search", font='sans 12 bold', command=_search) \
        .pack(pady=5)

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


def _search():
    """
    Perform a search then display the results on screen.
    """
    _clear_results()

    title = title_entry.get()

    results: list[dict] = _search_by_title(title, ignore_case.get(),
                                           contains.get())

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
    results_wrapper.pack(pady=10)


def hide_results():
    """
    Hide search results.
    """
    results_wrapper.pack_forget()


def _clear_results():
    """
    Removes all items from the tree
    """
    tree.delete(*tree.get_children())


def _search_by_title(title, ignore_case=False, contains=False) -> list[dict]:
    """
    Return all books with the given title, ignoring casing if specified.

    :param title: the search param
    :param ignore_case: whether to ignore casing or not
    :param contains: if True, return books that contain the given query, else
                     return books whose title is exactly the query
    :return: list of books with the given title
    """
    get_book_title = lambda book: book['title'] if not ignore_case else \
        book['title'].casefold()
    is_valid_title = lambda title, query: title == query if not contains else \
        query in title

    if ignore_case:
        title = title.casefold()

    return [book for book in database.books.values()
            if is_valid_title(get_book_title(book), title)]


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
def main():
    """
    Main method which contains test code for this module.
    """
    f = lambda results: (
        [book for book in results if _should_highlight(book)],
        [book for book in results if not _should_highlight(book)]
    )

    # len(highlight) = 2, len(normal) = 1
    highlight, normal = f(_search_by_title(title="Sinful Duty"))
    assert len(highlight) == 2 and len(normal) == 1, \
        "search failed for 'Sinful Duty'"

    # len(highlight) = 0, len(normal) = 3
    highlight, normal = f(
        _search_by_title(title="Soldier of Impact")
    )
    assert len(highlight) == 0 and len(normal) == 3, \
        "'search failed for 'Soldier of Impact'"

    # len(highlight) = 1, len(normal) = 2
    highlight, normal = f(_search_by_title(title="Avengers"))
    assert len(highlight) == 1 and len(normal) == 2, \
        "search failed for 'Avengers'"

    print('booksearch.py has passed all tests!')


if __name__ == "__main__":
    main()
