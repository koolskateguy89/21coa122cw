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

frame: LabelFrame = None

attr: StringVar = None
query_entry: Entry = None
query: StringVar = None
ignore_case: IntVar = None

results_wrapper: Frame = None
tree: ttk.Treeview = None


def get_frame(parent, bg, fg) -> LabelFrame:
    """
    Create and decorate the frame for searching for books.

    :param parent: the parent of the frame
    :param bg: the background color
    :param fg: the foreground color
    :return: the fully decorated frame
    """
    global frame
    global attr
    global query_entry
    global query
    global ignore_case
    global results_wrapper

    frame = LabelFrame(parent, text="Book Search", padx=5, pady=5, bg=bg, fg=fg)

    # embed a frame for user input so its widgets can be side-by-side
    # without affecting rest of layout
    input_frame = Frame(frame, bg=bg)
    input_frame.pack(pady=7)

    attr = StringVar()
    attr.set('title')  # default: search by title
    # search when attr is modified
    attr.trace_add('write', _search)
    ttk.Combobox(input_frame, state="readonly", values=database.BOOK_HEADERS,
                 width=13, textvariable=attr).grid(row=0, column=0, padx=5)

    query = StringVar()
    # search when query entry text is modified
    query.trace_add('write', _search)
    query_entry = Entry(input_frame, bg=fg, fg=bg, width=30, borderwidth=1,
                        textvariable=query)
    query_entry.focus_set()
    query_entry.grid(row=0, column=1, padx=5)

    ignore_case = IntVar()
    # search when ignore_case is modified
    ignore_case.trace_add('write', _search)
    Checkbutton(frame, text="Ignore case", bg=fg, fg=bg,
                activebackground=fg, activeforeground=bg,
                variable=ignore_case).pack(pady=5)

    Button(frame, text="Search", font='sans 12 bold', command=_search) \
        .pack(pady=5)

    _create_results_view()

    return frame


def on_show():
    """
    Set focus on the query entry when this frame is shown.
    """
    query_entry.focus_set()


def _create_results_view():
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


def _search(*_):
    """
    Perform a search then display the results on screen.

    :param _: unused varargs to allow this to be used as any callback
    """
    hide_results()
    _clear_results()

    query_ = query.get().strip()
    if not query_:
        return

    results: list[SimpleNamespace] = search_by_param(attr.get(),
                                                     query_,
                                                     ignore_case.get())

    for book in results:
        tags = ('highlight',) if _should_highlight(book) else ()

        # mutate some values to give librarian a better experience
        book_dict = {**vars(book),
                     # if book is available, don't show anyone as member
                     'member': member if (member := book.member) != '0' else '_'
                     }

        tree.insert('', index=END, values=tuple(book_dict.values()), tags=tags)

    if results:
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


def search_by_param(attr, query, ignore_case=False) -> list[SimpleNamespace]:
    """
    Search for books whose attribute 'attr' match the given query.

    Whether the attribute matches the query depends on the values of
    ignore_case.

    If ignore_case is True, the casing of the attribute and query are both
    ignored.

    The attribute matches the query if it contains the query.

    :param attr: the attribute of the book to search for
    :param query: the value to check the book attribute against
    :param ignore_case: whether to ignore casing or not
    :return: list of books that match the given condition
    """
    query = str(query)

    # convert book attribute to str because 'id' is stored as int
    get_value = lambda book: str(getattr(book, attr)) if not ignore_case else \
        str(getattr(book, attr)).casefold()

    if ignore_case:
        query = query.casefold()

    return [book for book in database.books.values()
            if query in get_value(book)]


def search_by_title(title, ignore_case=False) -> list[SimpleNamespace]:
    """
    Return all books whose titles contain the given title, ignoring casing if
    specified and including books whose title contains the given title.

    :param title: the search param
    :param ignore_case: whether to ignore casing or not
    :return: list of books with the given title
    """
    return search_by_param('title', title, ignore_case)


def _should_highlight(book: SimpleNamespace) -> bool:
    """
    Return whether a given book should be highlighted due to it being on loan
    for more than 60 days.
    
    :param book: the book to check
    :return: whether the book should be highlighted
    """
    logs = database.logs_for_book_id(book.id)

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
           and len(l) == 1, "search by ID failed for ID 1"

    print('booksearch.py has passed all tests!')


if __name__ == "__main__":
    main()
