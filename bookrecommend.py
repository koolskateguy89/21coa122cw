""""
This modules contains functions to be able to recommend books for a member,
this is done by generating popularity scores for a book, which is determined by
a combination of how much the user likes the genre and how many times the book
has been taken out by members.


Score system:
    score of title = genre popularity * title popularity

    genre popularity = reversed(sorted_genres).index(genre) * 6
        i.e. most popular genre = highest points & vice verse
        (we multiply by 6 to give it greater weight in score system)

    title popularity = the sum of book popularities for all books with that title
        book popularity = number of times that book has been withdrawn


Book recommendations are displayed in a bar chart which shows the title and the
popularity of the title.
"""

from tkinter import *
from typing import Callable

import matplotlib.patches as mpatches
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from matplotlib.figure import Figure

import database

frame: LabelFrame = None
id_entry: Entry = None

results_frame: Frame = None
fig: Figure = None
ax: Axes = None
canvas: FigureCanvasTkAgg = None

error_frame: Frame = None
error_label: Label = None


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
    global error_frame
    global error_label

    if frame is not None:
        id_entry.focus_set()
        return frame

    bg = "black"

    frame = LabelFrame(parent, text="Book Recommend", padx=5, pady=2, bg=bg,
                       fg="#f8f8ff")

    Button(frame, text="Back", fg="crimson",
           command=lambda: _back(back_to_menu)).pack(pady=10)

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

    Button(frame, text="Recommend", command=_recommend).pack(pady=2)

    results_frame = LabelFrame(frame, text="Recommendations", bg=bg, fg='white',
                               padx=5, pady=5, relief=RAISED)
    _generate_results_view()

    error_frame = LabelFrame(frame, text="Error", bg='red', fg='white',
                             relief=RAISED)
    error_label = Label(error_frame, bg=bg, fg='white')
    error_label.pack()

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
    Generate the widgets which will directly display the recommendations, ready
    to be added to the main frame.
    """
    global fig
    global ax
    global canvas

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=results_frame)
    canvas.draw()

    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, results_frame, pack_toolbar=False)
    toolbar.update()

    toolbar.pack(side=BOTTOM)
    canvas.get_tk_widget().pack(side=TOP, fill=X)


def _recommend():
    """
    Work out what titles to recommend to the member with given ID, and display
    the result or any errors.
    """
    hide_results()

    member_id = id_entry.get()

    if len(member_id) != 4:
        _show_error(f"Invalid member ID: '{member_id}'")
        return

    sorted_genres: list[str] = recommend_genres(member_id)

    genre_popularities: dict[str, int] = {genre: (pop + 1) * 6 for pop, genre in enumerate(reversed(sorted_genres))}

    titles_with_scores: dict[str, int] = {}
    # generate scores for each title
    for genre in sorted_genres:
        titles: list[tuple[str, int]] = recommend_titles_for_genre(genre)
        genre_score = genre_popularities[genre]

        for title, pop in titles:
            titles_with_scores[title] = pop * genre_score

    # sort titles by score (popularity)
    sorted_titles: list[tuple[str, int]] = sorted(titles_with_scores.items(),
                                                  key=lambda item: item[1],
                                                  reverse=True)

    if len(sorted_titles) < 3:
        _show_error(f"Cannot recommend books for '{member_id}'")
        return
    # can only show at most 10 titles
    elif len(sorted_titles) > 10:
        sorted_titles = sorted_titles[:10]

    # see https://stackoverflow.com/a/69878556/17381629
    _plot(*zip(*sorted_titles))
    display_results()


def display_results():
    """
    Display recommendations on screen.
    """
    results_frame.pack(fill=BOTH, pady=10)


def hide_results():
    """
    Hide recommendations and error message.
    """
    results_frame.pack_forget()
    error_frame.pack_forget()


def _show_error(msg):
    """
    Show the error frame with the given error message

    :param msg: the error message
    """
    error_label.configure(text=msg)
    error_frame.pack(pady=5)


def _reset_figure():
    """
    Reset figure by clearing axes and re-setting axes settings.
    """
    ax.clear()
    # axes.clear also removes settings so we have to re-set them
    ax.set_title('Recommendations for member')
    ax.set_xlabel('Book')
    ax.set_ylabel('Popularity')
    ax.tick_params(labelbottom=False)  # don't show x-axis values


bar_colours = [
    'red',
    'darkorange',
    'yellow',
    'green',
    'cyan',
    'navy',
    'indigo',
    'pink',
    'magenta',
    'purple',
]


def _add_legend(titles: list[str]):
    """
    Add legend to axes as titles are too long to show on the x-axis.

    :param titles: the recommended titles
    """
    patches = [mpatches.Patch(color=bar_colours[idx], label=title)
               for idx, title in enumerate(titles)]
    ax.legend(handles=patches)


def _plot(titles: list[str], popularities: list[int]):
    """
    Plot given book recommendations onto a bar chart.

    :param titles: the book titles to plot
    :param popularities: the popularities to plot
    """
    _reset_figure()

    _add_legend(titles)

    x_axis = list(range(len(titles)))

    # make bar chart
    bars = ax.bar(x_axis, popularities, width=.5)

    # set bar colour according to legend to show which title the bar represents
    for idx, bar in enumerate(bars):
        bar.set_color(bar_colours[idx])

    canvas.draw()


def recommend_genres(member_id: str) -> list[str]:
    """
    Calculate the given member's favourite genres and return them sorted by how
    many times they have withdrawn a book of that genre, i.e. how much the
    member likes the genre.

    :param member_id: the ID of the member to recommend for
    :return: the recommended genres for the member
    """
    member_logs: list[dict] = database.logs_for_member_id(member_id)

    # key = genre
    # value = no. of books involved in transactions
    genres: dict[str, int] = {}
    for log in member_logs:
        book = database.search_book_by_id(log['book_id'])
        genre = book['genre']

        if genres.get(genre) is None:
            genres[genre] = 1
        else:
            genres[genre] += 1

    sorted_genres = sorted(genres.items(), key=lambda item: item[1],
                           reverse=True)
    sorted_genres: list[str] = [genre for (genre, _) in sorted_genres]

    return sorted_genres


def recommend_titles_for_genre(genre: str) -> list[tuple[str, int]]:
    """
    Calculate the most popular titles for a given genre. Popularity is given by
    the number of times a book/title has been withdrawn.

    :param genre: the genre to check for
    :return: a sorted list of (title, popularity) for the genre
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

    titles_with_popularity: list[tuple[str, int]] = []
    # calculate the popularity of each title
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
    Return the number of times the book with given ID has been taken out, i.e.
    the book's popularity.

    :param book_id: the ID of the book to check
    :return: the popularity of the book
    """
    book_logs = database.logs_for_book_id(book_id)
    popularity = len(book_logs)
    return popularity
