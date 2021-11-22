"""
This module is the entry point for the application. It starts the tkinter
mainloop.

This module graphically defines the menu for the librarian to be able to access
other program functionalities.

This works using by stacking multiple Frames on top of each other and raising
a specific frame to the top of the stacking order, displaying it and effectively
hiding the others.
See: https://stackoverflow.com/a/7557028
"""
from tkinter import *
from tkinter import ttk

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


def on_tab_selected(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    module = modules[tab_text]
    module.on_show()


def main():
    """
    Setup and display the program's GUI.
    """
    root = Tk()
    root.title('Library Management System')
    root.geometry('800x600')
    root.attributes('-topmost', True)  # always on top

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TNotebook', background='black')

    notebook = ttk.Notebook(root)
    notebook.bind('<<NotebookTabChanged>>', on_tab_selected)
    notebook.pack(fill=BOTH, expand=True)

    for text, module in modules.items():
        frame = module.get_frame(notebook)
        frame.pack(fill=BOTH, expand=True)
        notebook.add(frame, text=text)

    root.mainloop()


if __name__ == "__main__":
    main()
