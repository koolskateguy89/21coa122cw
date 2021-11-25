"""
This module provides the functionality for searching for books, this is done by
using the database module to query the book database.

The search function allows for searching for books according to its id, genre,
title, author or member. It also allows casing to be ignored and to search for
books whose attribute contains the given query.
"""

from tkinter import *
from tkinter import ttk
from types import SimpleNamespace

import database
from database import date_to_str

frame: LabelFrame = None

attr: StringVar = None
query_entry: Entry = None
ignore_case: IntVar = None
contains: IntVar = None

results_wrapper: Frame = None
tree: ttk.Treeview = None


def get_frame(parent) -> LabelFrame:
    """
    Create and decorate the frame for searching for books.

    :param parent: the parent of the frame
    :return: the fully decorated frame
    """
    global frame
    global attr
    global query_entry
    global ignore_case
    global contains
    global results_wrapper

    bg, fg = 'black', 'white'

    frame = LabelFrame(parent, text="Book Search", padx=5, pady=5, bg=bg,
                       fg=fg)

    # embed a frame for user input so its widgets can be side-by-side
    # without affecting rest of layout
    input_frame = Frame(frame, bg=bg)
    input_frame.pack(pady=7)

    attr = StringVar()
    attr.set('title')  # default: search by title
    ttk.Combobox(input_frame, state="readonly", values=database.BOOK_HEADERS,
                 width=13, textvariable=attr).grid(row=0, column=0, padx=5)

    query_entry = Entry(input_frame, bg=fg, fg=bg, width=30, borderwidth=1)
    query_entry.focus_set()
    # search when enter is pressed
    query_entry.bind('<Return>', lambda event: _search())

    query_entry.grid(row=0, column=1, padx=5)

    ignore_case = IntVar()
    Checkbutton(frame, text="Ignore case", bg=fg, fg=bg,
                activebackground='white', activeforeground=bg,
                variable=ignore_case).pack(pady=5)

    contains = IntVar()
    Checkbutton(frame, text="Contains", bg=fg, fg=bg,
                activebackground=fg, activeforeground=bg,
                variable=contains).pack(pady=5)

    Button(frame, text="Search", font='sans 12 bold', command=_search) \
        .pack(pady=5)

    _generate_results_view()

    return frame


def on_show():
    """
    Hide results and set focus on the title entry when this frame is shown.
    """
    hide_results()
    query_entry.focus_set()


def _generate_results_view():
    """
    Generate the widgets which will directly display the results, ready to be
    added to the main frame.
    """
    global results_wrapper
    global tree

    headers = ('ID', 'Genre', 'Title', 'Author', 'Purchase Date', 'Member')

    results_wrapper = Frame(frame)
    tree = ttk.Treeview(results_wrapper, columns=headers, show='headings')
    tree.tag_configure('highlight', background='yellow', font=('Arial Bold', 9))
    tree.grid(row=0, column=0, sticky=NSEW)

    for header in headers:
        tree.column(header, width=90)
        tree.heading(header, text=header)

    tree.column('ID', anchor=CENTER, width=30)

    sb = Scrollbar(results_wrapper, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.grid(row=0, column=1, sticky=NS)


def _search():
    """
    Perform a search then display the results on screen.
    """
    _clear_results()

    results: list[SimpleNamespace] = search_by_param(attr.get(),
                                                     query_entry.get(),
                                                     ignore_case.get(),
                                                     contains.get())

    for book in results:
        tags = ('highlight',) if _should_highlight(book) else ()

        # mutate some values to give librarian a better experience
        book = {**vars(book),
                # display appropriate string representation of date
                'purchase_date': date_to_str(book.purchase_date),
                # if book is available, don't show anyone as member
                'member': member if (member := book.member) != '0' else ''
                }

        tree.insert('', index=END, values=tuple(book.values()), tags=tags)

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


def search_by_param(attr, query, ignore_case=False, contains=False) -> \
        list[SimpleNamespace]:
    """
    Search for books whose attribute 'attr' match the given query.
    Search for all books who meet a filter of query

    Whether the attribute matches the query depends on the values of ignore_case
    and contains.

    If ignore_case is True, the casing of the attribute and query are both
    ignored.

    If contains is True, they match if the attribute contains the query; else
    they match is the attribute is equal to the query.

    :param attr: the attribute of the book to search for
    :param query: the value to check the book attribute against
    :param ignore_case: whether to ignore casing or not
    :param contains: whether to check if the attribute contains the query or if
                        they are equal
    :return: list of books with the given title
    """

    if attr == 'purchase_date':
        return search_by_date_str(query, contains)

    # convert book attribute to str as 'id' is stored as int
    get_value = lambda book: str(getattr(book, attr)) if not ignore_case else \
        str(getattr(book, attr)).casefold()
    is_valid = lambda value, query: value == query if not contains else \
        query in value

    if ignore_case:
        query = query.casefold()

    return [book for book in database.books.values()
            if is_valid(get_value(book), query)]


def search_by_date_str(date: str, contains=False) -> list[SimpleNamespace]:
    """
    Return the books whose purchase date (in DD/MM/YYYY format) match the given
    date.

    :param date: date to search for (not necessarily a full date)
    :param contains: whether to check if book date contains query or not
    :return:
    """
    is_valid = lambda value, query: value == query if not contains else \
        query in value

    return [book for book in database.books.values()
            if is_valid(date_to_str(book.purchase_date), date)]


def search_by_title(title, ignore_case=False, contains=False) -> \
        list[SimpleNamespace]:
    """
    Return all books with the given title, ignoring casing if specified and
    including books whose title contains the given title.

    :param title: the search param
    :param ignore_case: whether to ignore casing or not
    :param contains: if True, return books that contain the given query, else
                     return books whose title is exactly the query
    :return: list of books with the given title
    """
    return search_by_param('title', title, ignore_case, contains)


def _should_highlight(book: SimpleNamespace) -> bool:
    """
    Return whether a given book should be highlighted due to it being on loan
    for more than 60 days.
    
    :param book: the book to check
    :return: whether the book should be highlighted
    """
    logs: list[dict] = database.logs_for_book_id(book.id)

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
    highlight, normal = f(search_by_title(title="Sinful Duty"))
    assert len(highlight) == 2 and len(normal) == 1, \
        "search failed for 'Sinful Duty'"

    # len(highlight) = 0, len(normal) = 3
    highlight, normal = f(
        search_by_title(title="Soldier of Impact")
    )
    assert len(highlight) == 0 and len(normal) == 3, \
        "search failed for 'Soldier of Impact'"

    # len(highlight) = 1, len(normal) = 2
    highlight, normal = f(search_by_title(title="Avengers"))
    assert len(highlight) == 1 and len(normal) == 2, \
        "search failed for 'Avengers'"

    assert (l := search_by_param('id', 10))[0].genre == 'Crime' \
           and len(l) == 1, "search by id failed for id 1"

    print('booksearch.py has passed all tests!')


if __name__ == "__main__":
    main()
