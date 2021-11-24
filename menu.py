"""
This module is the entry point for the application. It starts the tkinter
mainloop.

This module graphically defines the menu for the librarian to be able to access
other program functionalities.
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

menu: LabelFrame = None
notebook: ttk.Notebook = None

bg, fg = 'black', 'white'


def _on_tab_selected(event):
    """
    Call module on_show method when its frame is shown, or show the main menu
    if that tab is selected.

    :param event: the tkinter VirtualEvent
    """
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, 'text')
    module = modules.get(tab_text)

    if module is not None:
        module.on_show()
    else:
        _show_frame(menu)


def _show_module(module):
    """
    Show the tab for the given module in the notebook and show the notebook.

    :param module: the module to show
    """
    idx = list(modules.values()).index(module)
    notebook.select(idx)
    _show_frame(notebook)


def _show_frame(frame):
    """
    Show the given frame by raising it to the top of the stacking order.

    :param frame: the frame to show
    """
    frame.tkraise()


def _menu_button(text, module) -> Button:
    """
    Return a standardised Button that acts as a menu option.
    :param text: the button text
    :param module: the module the button will open
    :return: a decorated button
    """
    return Button(menu, text=text, command=lambda: (_show_module(module)),
                  bg=bg, fg=fg, width=48, height=2, borderwidth=2)


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
    # root.attributes('-topmost', True)  # always on top

    container = Frame(root)
    container.pack(side=TOP, fill=BOTH, expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    menu = LabelFrame(container, text='Main Menu', bg=bg, fg=fg)
    menu.configure(padx=5, pady=10)
    setup_frame(menu)

    title_label = Label(menu, text='Library Management System', bg=bg, fg=fg)
    title_label.pack(pady=20)
    # underline the title label
    font = Font(title_label, title_label.cget('font'))
    font.configure(underline=True)
    title_label.configure(font=font)

    # set notebook background to bg
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TNotebook', background=bg)

    notebook = ttk.Notebook(container)
    notebook.bind('<<NotebookTabChanged>>', _on_tab_selected)
    setup_frame(notebook)

    # add a menu button and tab for each module
    for text, module in modules.items():
        _menu_button(text, module).pack(pady=5)

        frame = module.get_frame(notebook)
        notebook.add(frame, text=text)

    # add a tab to facilitate going back to the main menu
    notebook.add(Frame(notebook, bg=bg), text='   Main Menu')

    _show_frame(menu)

    root.mainloop()


if __name__ == "__main__":
    main()
