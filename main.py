from __future__ import print_function

import TasksWindow

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

SCOPES = ['https://www.googleapis.com/auth/tasks']


def main():
    win = TasksWindow.TasksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
