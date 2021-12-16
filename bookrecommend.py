"""
This module provides functionality to recommend books for a member. This is done
by generating popularity scores for books, which is determined by a combination
of how much the member likes the book's genre and how many times the book has
been taken out by members.


Score system:
    score of title = genre popularity * title popularity

    genre popularity = reversed(sorted_genres).index(genre) * 6
        i.e. most popular genre -> highest points & vice versa
        (we multiply by 6 to give it greater weight in score system)

    title popularity = the sum of book popularities for all books of that title
        book popularity = number of times that book has been withdrawn


Book recommendations are displayed in a bar chart which shows the book title and
popularity score of each recommended book.

It has been tested and is working.

Written by F120840 between 8th November and 16th December 2021.
"""

import random
from collections import Counter
from tkinter import *
from typing import List, Dict, Tuple, Set

import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from matplotlib.figure import Figure

import database

plt.style.use('Solarize_Light2')
plt.style.use('dark_background')

id_entry: Entry

results_frame: Frame
fig: Figure
ax: Axes
canvas: FigureCanvasTkAgg
toolbar: NavigationToolbar2Tk

error_frame: Frame


def get_frame(parent, bg, fg) -> LabelFrame:
    """
    Create and decorate the frame for recommending books.

    :param parent: the parent of the frame
    :param bg: the background color
    :param fg: the foreground color
    :return: the fully decorated frame
    """
    global id_entry
    global results_frame
    global error_frame

    frame = LabelFrame(parent, text='Book Recommend', padx=5, pady=2, bg=bg,
                       fg=fg)

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text='Enter member ID:', bg=bg, fg=fg) \
        .grid(row=0, column=0, pady=7)
    id_entry = Entry(input_frame, borderwidth=3)
    id_entry.focus_set()
    id_entry.grid(row=0, column=1)
    # recommend book when Enter is pressed
    id_entry.bind('<Return>', lambda event: _recommend())

    Button(frame, text='Recommend', command=_recommend).pack(pady=2)

    results_frame = LabelFrame(frame, text='Recommendations', bg=bg, fg=fg,
                               padx=5, pady=5, relief=RAISED)
    _create_mpl_widgets()

    error_frame = LabelFrame(frame, text='Error', bg='red', fg=fg,
                             relief=RAISED)
    Label(error_frame, bg=bg, fg=fg).pack()

    return frame


def on_show():
    """
    Set focus on the book ID entry when this frame is shown.
    """
    id_entry.focus_set()


def _create_mpl_widgets():
    """
    Initialize the matplotlib widgets which will display the recommendations.
    """
    global fig
    global ax
    global canvas
    global toolbar

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=results_frame)
    toolbar = NavigationToolbar2Tk(canvas, results_frame, pack_toolbar=False)

    toolbar.pack(side=BOTTOM, pady=10)
    canvas.get_tk_widget().pack(side=TOP, fill=X, ipady=10)


def _recommend():
    """
    Work out what titles to recommend to the member with given ID, and display
    the result or any errors.
    """
    hide_results()

    member_id = id_entry.get()

    if len(member_id) != 4:
        _show_error(f'Invalid member ID: {member_id}')
        return

    sorted_genres: List[str] = recommend_genres(member_id)

    genre_scores: Dict[str, int]

    if sorted_genres:
        # give each genre a score according to how many books the member has
        # read of that genre; their favourite genre gets the most points
        genre_scores = {genre: (idx + 1) * 6 for idx, genre in
                        enumerate(reversed(sorted_genres))}
    else:
        # if the member hasn't read any books, pick 2 random genres to recommend
        genres = ('Action', 'Crime', 'Fantasy', 'Mystery', 'Romance', 'Sci-Fi',
                  'Tragedy', 'Drama', 'Adventure', 'Horror')
        sorted_genres = random.sample(genres, 2)
        # as we don't know which genres the member likes the most, we weigh all
        # genres equally
        genre_scores = {genre: 1 for genre in sorted_genres}

    titles_with_scores: Dict[str, int] = {}
    # generate scores for each title in each genre
    for genre in sorted_genres:
        titles: List[Tuple[str, int]] = recommend_titles_for_genre(genre,
                                                                   member_id)
        genre_score = genre_scores[genre]

        for title, title_pop in titles:
            titles_with_scores[title] = title_pop * genre_score

    # sort titles by score (popularity) in descending order
    sorted_results: List[Tuple[str, int]] = sorted(titles_with_scores.items(),
                                                   key=lambda item: item[1],
                                                   reverse=True)

    if len(sorted_results) < 3:
        _show_error(f"Cannot recommend books for '{member_id}'")
        return

    # can only show at most 10 titles
    sorted_results = sorted_results[:10]

    # unpack zipped unpacked sorted_results to get titles and popularities
    # separately
    _plot(*zip(*sorted_results))
    display_results()


def display_results():
    """
    Display recommendations on screen.
    """
    results_frame.pack(fill=BOTH, pady=5)


def hide_results():
    """
    Hide recommendations and error message.
    """
    results_frame.pack_forget()
    error_frame.pack_forget()


def _show_error(msg):
    """
    Show the error frame with the given error message.

    :param msg: the error message
    """
    error_label = error_frame.pack_slaves()[0]
    error_label.configure(text=msg)
    error_frame.pack(pady=5)


def _reset_figure():
    """
    Reset figure by clearing axes and re-setting axes settings.
    """
    ax.clear()
    # axes.clear also removes settings, so we have to re-set them
    ax.set_title('Recommended Books')
    ax.set_xlabel('Recommendation Score')
    ax.set_ylabel('Book')
    ax.tick_params(labelleft=False)  # don't show y-axis values

    # reset the toolbar history
    toolbar.update()


# matplotlib colormaps (14)
# https://matplotlib.org/stable/tutorials/colors/colormaps.html#classes-of-colormaps
INF = float('inf')
COLOR_MAPS = {
    # Perceptually Uniform Sequential
    'viridis': INF,
    'plasma': INF,
    # Sequential (2)
    'spring': INF,
    'summer': INF,
    'autumn': INF,
    # Diverging
    'RdYlBu': INF,
    'RdYlGn': INF,
    'Spectral': INF,
    'coolwarm': INF,
    'bwr': INF,
    # Miscellaneous
    'prism': 6,
    'gist_rainbow': INF,
    'rainbow': INF,
    'gist_ncar': INF,
}


def _get_random_bar_colors(length: int = 10) -> List[Tuple[int]]:
    """
    Return a normalized list of colors from a random colormap, of given length.

    :param length: how many colors to generate
    :return: a list of rgba colors (4-tuples)
    """
    # filter COLOR_MAPS as some don't have enough different colors for each bar
    # to be a different color
    cmaps = tuple(cmap for cmap, cols in COLOR_MAPS.items() if cols >= length)
    cmap = random.choice(cmaps)

    # randomly choose (~50% chance) to reverse the colormap
    if random.random() < 0.5:
        cmap += '_r'

    # be able to generate n=length linearly normalised values between [0.0, 1.0]
    norm = colors.Normalize(vmin=0, vmax=length - 1)
    # sample colormap at (length-1) normalised intervals
    scalar_map = mplcm.ScalarMappable(norm=norm, cmap=cmap)

    return [scalar_map.to_rgba(i) for i in range(length)]


def _plot(titles: List[str], popularities: List[int]):
    """
    Plot given title recommendations onto a bar chart.

    :param titles: the book titles to plot
    :param popularities: the popularities to plot
    """
    _reset_figure()

    bar_colours = _get_random_bar_colors(len(titles))

    # len(titles) -> 0 as we want to display the most popular titles at the top
    y_axis = range(len(titles), 0, -1)
    # show y-axis ticks next to every bar
    ax.set_yticks(y_axis)

    # make horizontal bar chart
    bars = ax.barh(y_axis, popularities, height=.7, color=bar_colours)

    min_pop = min(popularities)
    # add text to each bar saying which title the bar represents
    for bar, title in zip(bars, titles):
        y = bar.get_y()
        height = bar.get_height()

        xx = min(50.0, min_pop * .25)
        yy = y + height * .4

        # put book title into left-center of bar
        text = ax.text(xx, yy, title, color='white', fontweight='bold',
                       va='center')
        # add a black outline to white text, so it is visible on all backgrounds
        text.set_path_effects([
            # draw the black outline
            path_effects.Stroke(linewidth=2.5, foreground='black'),
            # draw the white text
            path_effects.Normal(),
        ])

    canvas.draw()


def recommend_genres(member_id: str) -> List[str]:
    """
    Calculate the given member's favourite genres and return them sorted by how
    many times the member has withdrawn a book of that genre, i.e. how much the
    member likes the genre.

    :param member_id: the ID of the member to recommend for
    :return: the recommended genres for the member
    """
    member_logs = database.logs_for_member_id(member_id)

    # count the no. of books of a genre involved in transaction
    genre_counter = Counter()
    for log in member_logs:
        book = database.search_book_by_id(log['book_id'])
        genre_counter.update([book.genre])

    # sort genres by how many times the member has withdrawn a book of that
    # genre, in descending order
    return sorted(genre_counter, key=genre_counter.get, reverse=True)


def recommend_titles_for_genre(genre: str, member_id: str) -> \
        List[Tuple[str, int]]:
    """
    Calculate the most popular titles for a given genre. Popularity is given by
    the number of times a book/title has been withdrawn.

    :param genre: the genre to check for
    :param member_id: the ID of the member to recommend for
    :return: a sorted list of (title, popularity) for the genre
    """
    books = database.search_books_by_param('genre', genre)

    # get the titles of the books the member has read
    read_titles: Set[str] = _titles_member_has_read(member_id)

    # calculate how popular each title is by summing the popularity of each copy
    title_pops: Dict[str, int] = {}
    for book in books:
        # we don't want to recommend books the member has read
        if book.title in read_titles:
            continue

        pop = _book_id_popularity(book.id)
        title_pops[book.title] = title_pops.get(book.title, 0) + pop

    # sort titles in descending popularity order
    most_popular_titles: List[Tuple[str, int]] = sorted(title_pops.items(),
                                                        key=lambda tup: tup[1],
                                                        reverse=True)

    # limit to 10 most popular titles
    return most_popular_titles[:10]


def _book_id_popularity(book_id: int) -> int:
    """
    Return the number of times the book with given ID has been taken out, i.e.
    the book's popularity.

    :param book_id: the ID of the book to check
    :return: the popularity of the book
    """
    return sum(1 for log in database.logs if log['book_id'] == book_id)


def _titles_member_has_read(member_id: str) -> Set[str]:
    """
    Return the book titles that the given member has read.

    :param member_id: the ID of the member
    :return: a set of the titles the member has read
    """
    logs = database.logs_for_member_id(member_id)
    titles = set()

    for log in logs:
        book = database.search_book_by_id(log['book_id'])
        titles.add(book.title)

    return titles
