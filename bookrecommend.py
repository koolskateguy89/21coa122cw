""""
Your program must have functionality to recommend books to its member. The
librarian should provide a member-ID to be able to find out a list of recommended
books for the member. Number of books in the list must be between 3 and 10.
Note the numbers are inclusive.
The system database should have a transaction log, which keeps the loan history
of library books. Based on this log, the system can find out the popular books for
each genre and preferred genres for each member to give the suitable
recommendation.

A Python module which contains functions used to list the
recommended books for a member in the popularity order and appropriately
visualise the list by using the Matplotlib module. You should come up with the
details of the popularity criteria.
"""
from tkinter import *
from tkinter import messagebox
from typing import Callable

import database

# import matplotlib
"""
TODO: basically unique books?
maybe have dict[str, set/list[int]]
    key: title, value: all ids of that book 
"""
"""
a bar chart? y-axis popularity, x-axis book name
"""

# it's pretty much functional, i just need to have more books of x genre

frame: LabelFrame = None
id_entry: Entry = None
results_frame: Frame = None


def get_frame(parent, back_to_menu: Callable) -> LabelFrame:
    """
    Lazily create the frame for recommending books and set focus on the
    member ID entry.

    :param parent: the parent of the frame
    :param back_to_menu: function that returns back to menu
    :return: the fully decorated frame
    """
    global frame
    global id_entry
    global results_frame

    if frame is not None:
        id_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Recommend", padx=5, pady=5, bg=bg,
                       fg="#f8f8ff")

    Button(frame, text="Back", fg="crimson", command=lambda: _back(back_to_menu)) \
        .pack(pady=10)

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter member ID:", bg=bg, fg='white').grid(
        row=0, column=0, pady=7)
    id_entry = Entry(input_frame, borderwidth=3)
    id_entry.focus_set()
    id_entry.grid(row=0, column=1)
    # recommend book when Enter is pressed
    id_entry.bind('<Return>', lambda event: _recommend())
    # go back when Esc is pressed
    id_entry.bind('<Escape>', lambda event: _back(back_to_menu))

    Button(frame, text="Recommend", command=_recommend).pack(pady=10)

    results_frame = LabelFrame(frame, text="Recommendations")

    return frame


def _back(back_to_menu: Callable):
    """
    Hide results and go back to main menu.

    :param back_to_menu: the function that changes the frame to the menu frame
    """
    hide_results()
    back_to_menu()


def _recommend():
    """
    Work out what titles to recommend to the member with given ID, and display
    the results.
    """
    hide_results()

    member_id = id_entry.get()

    if len(member_id) != 4:
        messagebox.showerror('Error', f"Invalid member ID: '{member_id}'")
        return

    titles: list[tuple[str, int]] = recommend_titles(member_id)

    for t, p in titles:
        print(t, p)

    # TODO: matplotlib bar chart
    display_results()


def display_results():
    """
    Display recommendations on screen.
    """
    results_frame.pack(pady=10)


def hide_results():
    """
    Hide recommendations.
    """
    results_frame.pack_forget()


def recommend_titles(member_id: str) -> list[tuple[str, int]]:
    """
    Return the recommended titles along with their popularity.

    :param member_id:
    :return: list of (title, popularity) of books
    """
    member_logs: list[dict] = database.logs_for_member_id(member_id)

    #           genre, number of books involved in transactions
    genres: dict[str, int] = {}
    for log in member_logs:
        book = database.search_book_by_id(log['book_id'])
        genre = book['genre']

        if genres.get(genre) is None:
            genres[genre] = 1
        else:
            genres[genre] += 1

    favourite_genre = sorted(genres.items(), key=lambda item: item[1], reverse=True)[0][0]

    return _most_popular_books_for_genre(favourite_genre)


def _most_popular_books_for_genre(genre: str) -> list[tuple[str, int]]:
    """
    Popularity is measured by how many times a book has been taken out

    :param genre: the genre to check for
    :return:
    """
    books: dict[int, dict] = database.search_books_by_param('genre', genre)

    # popularity is per title not per individual copy of book, so we need to
    # basically put each copy of a title together
    #                    title, ids
    books_by_title: dict[str, set[int]] = {}
    for book_id, book in books.items():
        title = book['title']
        if books_by_title.get(title) is None:
            books_by_title[title] = {book_id}
        else:
            books_by_title[title].add(book_id)

    # calculate the popularity of each title
    titles_with_popularity: list[tuple[str, int]] = []
    for title, ids in books_by_title.items():
        popularity = sum(_book_popularity_id(book_id) for book_id in ids)
        titles_with_popularity.append((title, popularity))

    most_popular_titles: list[tuple[str, int]] = sorted(titles_with_popularity,
                                                        key=lambda tup: tup[1],
                                                        reverse=True)

    if len(most_popular_titles) > 10:
        most_popular_titles = most_popular_titles[:10]

    return most_popular_titles


def _book_popularity_id(book_id: int) -> int:
    """
    Return the number of times the book with given ID has been taken out

    :param book_id: the ID of the book to check
    :return: the popularity of the book
    """
    book_logs = database.logs_for_book_id(book_id)
    popularity = len(book_logs)
    return popularity


# TODO: tests
if __name__ == "__main__":
    # _titles: list[tuple[str, int]] = recommend_books('util')
    # print(books)

    _titles: list[tuple[str, int]] = recommend_titles('book')
    for _title, pop in _titles:
        print(_title, pop)
