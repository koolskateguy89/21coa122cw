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
from tkinter.font import Font

import bookcheckout
import bookrecommend
import bookreturn
import booksearch

root = Tk()
root.title('Library Management System')
root.geometry('800x600')
root.attributes('-topmost', True)  # always on top

container = Frame(root)
container.pack(side="top", fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

bg = 'black'
fg = 'white'


def back_to_menu():
    """
    Change the frame to the menu fame.
    """
    show_frame(menu)


def menu_button(text: str, module) -> Button:
    """
    Return a standardised Button that acts as a menu option.

    :param text: the button text
    :param module: the module the button will opens
    :return: a decorated button
    """
    return Button(menu, text=text, command=lambda: show_module(module), bg=bg,
                  fg=fg, width=48, height=2, borderwidth=2)


def setup_frame(frame):
    """
    Add frame to the stacking order, ready to be shown.

    :param frame: the frame to add
    """
    frame.grid(row=0, column=0, sticky="nsew")


def show_frame(frame):
    """
    Show the given frame by raising it to the top of the stacking order.

    :param frame: the frame to show
    """
    frame.tkraise()


def show_module(module):
    """
    Show the frame for the given module, providing access to a program
    functionality

    :param module: the module to show
    """
    frame = module.get_frame(container, back_to_menu)
    setup_frame(frame)
    show_frame(frame)


def configure_font(label: Label, **options):
    """
    Configure the font of a given label, according to given options.

    :param label: the label that the font will be configured to
    :param options: font options (family, size, weight, slant, underline,
                    or overstrike)
    """
    font = Font(label, label.cget("font"))
    font.configure(**options)
    label.configure(font=font)


menu = LabelFrame(container, text="Main Menu", bg=bg, fg=fg)
menu.configure(padx=5, pady=10)

title_label = Label(menu, text="Library Management System", bg=bg, fg=fg)
title_label.pack(pady=20)
configure_font(title_label, underline=True)

search_button = menu_button("Search", booksearch)
checkout_button = menu_button("Checkout", bookcheckout)
return_button = menu_button("Return", bookreturn)
recommend_button = menu_button("Recommend", bookrecommend)

search_button.pack(pady=5)
checkout_button.pack(pady=5)
return_button.pack(pady=5)
recommend_button.pack(pady=5)

setup_frame(menu)
show_frame(menu)

if __name__ == "__main__":
    root.mainloop()
