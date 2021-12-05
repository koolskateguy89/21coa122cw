""""
This modules contains functions to be able to recommend books for a member,
this is done by generating popularity scores for a book, which is determined by
a combination of how much the member likes the genre and how many times the book
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

It has been tested and is working.
"""

import random
from tkinter import *
from types import SimpleNamespace

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.patheffects as path_effects

from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from matplotlib.figure import Figure

import database

plt.style.use('Solarize_Light2')
plt.style.use('dark_background')

id_entry: Entry = None

results_frame: Frame = None
fig: Figure = None
ax: Axes = None
canvas: FigureCanvasTkAgg = None

error_frame: Frame = None
error_label: Label = None


def get_frame(parent) -> LabelFrame:
    """
    Create and decorate the frame for recommending books.

    :param parent: the parent of the frame
    :return: the fully decorated frame
    """
    global id_entry
    global results_frame
    global error_frame
    global error_label

    bg = 'black'

    frame = LabelFrame(parent, text="Book Recommend", padx=5, pady=2, bg=bg,
                       fg='#f8f8ff')

    input_frame = Frame(frame, bg=bg)
    input_frame.pack()

    Label(input_frame, text="Enter member ID:", bg=bg, fg='white') \
        .grid(row=0, column=0, pady=7)
    id_entry = Entry(input_frame, borderwidth=3)
    id_entry.focus_set()
    id_entry.grid(row=0, column=1)
    # recommend book when Enter is pressed
    id_entry.bind('<Return>', lambda event: _recommend())

    Button(frame, text="Recommend", command=_recommend).pack(pady=2)

    results_frame = LabelFrame(frame, text="Recommendations", bg=bg, fg='white',
                               padx=5, pady=5, relief=RAISED)
    _generate_results_view()

    error_frame = LabelFrame(frame, text="Error", bg='red', fg='white',
                             relief=RAISED)
    error_label = Label(error_frame, bg=bg, fg='white')
    error_label.pack()

    return frame


def on_show():
    """
    Hide results and set focus on the book ID entry when this frame is shown.
    """
    # hide_results()
    id_entry.focus_set()


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
        _show_error(f"Invalid member ID: '{member_id}'")
        return

    sorted_genres: list[str] = recommend_genres(member_id)

    if not sorted_genres:
        genres = ('Action', 'Crime', 'Fantasy', 'Mystery', 'Romance', 'Sci-Fi',
                  'Tragedy', 'Drama', 'Adventure', 'Horror')
        sorted_genres = [random.choice(genres)]

    genre_popularities: dict[str, int] = {genre: (idx + 1) * 6 for idx, genre in
                                          enumerate(reversed(sorted_genres))}

    titles_with_scores = dict[str, int]()
    # generate scores for each title in each genre
    for genre in sorted_genres:
        titles: list[tuple[str, int]] = recommend_titles_for_genre(genre)
        genre_score = genre_popularities[genre]

        for title, title_pop in titles:
            titles_with_scores[title] = title_pop * genre_score

    # sort titles by score (popularity)
    sorted_titles: list[tuple[str, int]] = sorted(titles_with_scores.items(),
                                                  key=lambda item: item[1],
                                                  reverse=True)

    if len(sorted_titles) < 3:
        _show_error(f"Cannot recommend books for '{member_id}'")
        return

    # can only show at most 10 titles
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
    ax.set_title('Recommended Books')
    ax.set_xlabel('Popularity')
    ax.set_ylabel('Book')
    ax.tick_params(labelleft=False)  # don't show y-axis values


cmIndx = 0
def _get_random_bar_colors(num_colors: int = 10) -> list[tuple[int]]:
    """

    :param num_colors:
    :return: a list of rgba colors (4-tuples)
    """
    global cmIndx
    # matplotlib qualitative colormaps
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html#qualitative
    cms = {
        'Paired': 12,  # brown at the end :/
        'Accent': 8,
        'Dark2': 8,
        'Set1': 9,
        'Set2': 8,
        'tab10': 10,
        'tab20b': 20,
    }

    # filter colormaps as some don't have enough colors for each bar to be a
    # different color
    cms = [cm for cm, n_colors in cms.items() if n_colors >= num_colors]

    #cms = list(cms.keys())

    # TODO: basically try to filter colormaps to not include blacks/whites (mainly blacks) because background is black
    #cms = plt.colormaps()
    #cm = random.choice(cms)
    cm = cms[cmIndx]
    print(cmIndx, cm)
    cmIndx += 1
    if cmIndx >= len(cms):
        print('All')
        cmIndx = 0
    #cm = plt.get_cmap('gist_rainbow')

    # https://stackoverflow.com/a/8391452/17381629
    cNorm = colors.Normalize(vmin=0, vmax=num_colors - 1)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)

    return [scalarMap.to_rgba(i) for i in range(num_colors)]


# TODO: decide to remove/use
def _randomise_colours() -> list[str]:
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
    random.shuffle(bar_colours)
    return bar_colours


def _plot(titles: list[str], popularities: list[int]):
    """
    Plot given book recommendations onto a bar chart.

    :param titles: the book titles to plot
    :param popularities: the popularities to plot
    """
    _reset_figure()

    #bar_colours = _randomise_colours()
    bar_colours = _get_random_bar_colors(len(titles))
    # random.boolean for reverse(bar_colours)

    # len(titles) -> 0 as we want to display the most popular titles at the top
    y_axis = range(len(titles), 0, -1)

    # show y-axis ticks on every book
    ax.set_yticks(y_axis)

    # make horizontal bar chart
    #bars = ax.barh(y_axis, popularities, height=.7)
    bars = ax.barh(y_axis, popularities, height=.7, color=bar_colours)
    min_pop = min(popularities)

    # set bar colour according to legend to show which title the bar represents
    for bar, title, col in zip(bars, titles, bar_colours):
        y = bar.get_y()
        height = bar.get_height()

        #print(title, y + height * .25)

        # TODO: bar.text() book title

        # put title into the middle of the bar
        # ax.text(30, y + height * .25, title, color='black', fontweight='bold')
        text = ax.text(min(50.0, min_pop/4), y + height/2, title, color='white',
                       fontweight='bold', va='center')
        # add a black outline to text so it is visible on all backgrounds
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='black'),
            path_effects.Normal(),
        ])

        # TODO: remove bar_colours from zip?
        #bar.set_color(col)

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
    genres = dict[str, int]()
    for log in member_logs:
        book = database.search_book_by_id(log['book_id'])
        genre = book.genre

        genres[genre] = genres.get(genre, 0) + 1

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
    books: dict[int, SimpleNamespace] = database.search_books_by_param('genre',
                                                                       genre)

    # calculate how popular each title is by summing the popularity of each copy
    title_pops = dict[str, int]()
    for book_id, book in books.items():
        pop = _book_popularity_id(book_id)
        title_pops[book.title] = title_pops.get(book.title, 0) + pop

    most_popular_titles: list[tuple[str, int]] = sorted(title_pops.items(),
                                                        key=lambda tup: tup[1],
                                                        reverse=True)

    # limit to 10 titles
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
