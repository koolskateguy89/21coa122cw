"""
This module is the entry point for the application. It starts the tkinter
mainloop.

This module graphically defines the menu for the librarian to be able to access
other program functionalities.

It has been tested and is working.

Written by Dara Agbola between 8th November and 9th December 2021.
"""

from tkinter import *
from tkinter import ttk
from tkinter.font import Font

import bookcheckout
import bookrecommend
import bookreturn
import booksearch

modules = {
    'Search': booksearch,
    'Checkout': bookcheckout,
    'Return': bookreturn,
    'Recommend': bookrecommend
}
modules_tuple = tuple(modules.values())

menu: LabelFrame
notebook: ttk.Notebook

bg, fg = 'black', '#f8f8ff'


def _on_tab_selected(event):
    """
    Call module on_show method when its frame is shown, or show the main menu if
    that tab is selected.

    :param event: the tkinter VirtualEvent
    """
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, 'text')
    module = modules.get(tab_text)

    if module is None:
        _show_frame(menu)
    else:
        module.on_show()


def _show_module(module):
    """
    Show the tab for the given module in the notebook.

    :param module: the module to show
    """
    idx = modules_tuple.index(module)
    notebook.select(idx + 1)
    _show_frame(notebook)


def _show_frame(frame):
    """
    Show the given frame by raising it to the top of the stacking order.

    :param frame: the frame to show
    """
    frame.tkraise()


def _menu_button(text, module) -> Button:
    """
    Return a standardised Button that acts as a menu option to provide the
    librarian to the other program functionalities.

    :param text: the button text
    :param module: the module the button will open
    :return: a decorated button
    """
    return Button(menu, text=text, command=lambda: _show_module(module),
                  bg=bg, fg=fg, width=48, height=2, borderwidth=2,
                  font=('Arial', 8))


def main():
    """
    Setup and display the program's GUI.
    """
    global menu
    global notebook

    # puts all container Frames on top of each other
    setup_frame = lambda f: f.grid(row=0, column=0, sticky=NSEW)

    root = Tk()
    root.title('Library Management System')
    root.geometry('800x600')
    root.attributes('-topmost', True)  # always on top

    container = Frame(root)
    container.pack(side=TOP, fill=BOTH, expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    menu = LabelFrame(container, text='Main Menu', bg=bg, fg=fg)
    menu.configure(padx=5, pady=10)
    setup_frame(menu)

    title_label = Label(menu, text='Library Management System', bg=bg, fg=fg,
                        font=('Arial bold', 20))
    title_label.pack(pady=20)
    # underline the title label
    font = Font(title_label, title_label.cget('font'))
    font.configure(underline=True)
    title_label.configure(font=font)

    style = ttk.Style()
    style.theme_use('clam')
    # set notebook background to bg
    style.configure('TNotebook', background=bg)

    notebook = ttk.Notebook(container)
    notebook.bind('<<NotebookTabChanged>>', _on_tab_selected)
    setup_frame(notebook)

    # add a tab to facilitate going back to the main menu
    notebook.add(Frame(notebook, bg=bg), text='Main Menu')

    # add a menu button and tab for each module
    for text, module in modules.items():
        _menu_button(text, module).pack(pady=5)

        frame = module.get_frame(notebook, bg, fg)
        notebook.add(frame, text=text)

    _show_frame(menu)

    root.mainloop()


if __name__ == "__main__":
    main()
