import gi
import googleapiclient.discovery

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/tasks']


def on_button_clicked():
    print("Add")


def start_tasks_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('tasks', 'v1', credentials=creds)
        return service
    except HttpError as err:
        print(err)
        return err


def get_tasklists(service: googleapiclient.discovery.Resource) -> list:
    results = service.tasklists().list(maxResults=10).execute()
    return results.get('items')


def get_tasks(service: googleapiclient.discovery.Resource, tasklist) -> list:
    results = service.tasks().list(tasklist=tasklist).execute()
    return results.get('items')


class TasksWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Tasks")
        self.service = start_tasks_api()
        self.tasklists = get_tasklists(self.service)
        self.notebook = Gtk.Notebook()
        self.pages = []
        self.refresh()

    def refresh(self):
        self.tasklists = get_tasklists(self.service)

        for tasklist in self.tasklists:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            page.set_border_width(10)
            tasks = get_tasks(self.service, tasklist['id'])
            if tasks is not None:
                for task in tasks:
                    if task is None:
                        break
                    page.add(TaskBox(task))
            add_button = Gtk.Button(label="+")
            add_button.connect("clicked", self.new_task)
            page.add(add_button)
            self.pages.append(page)
            self.notebook.append_page(page, Gtk.Label(label=tasklist['title']))

    def new_task(self, button):
        # i = self.notebook.get_current_page()
        # task = dict()
        # self.service.tasks().insert(tasklist=self.tasklists[i]['id'], body=task)
        self.refresh()


class TasklistPage(Gtk.Box):

    def __init__(self, service, tasklist):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_border_width(10)

        self.service = service
        self.tasklist = tasklist
        self.tasks = get_tasks(self.service, self.tasklist)

        for task in self.tasks:
            if task is None:
                break
            self.add(TaskBox(task))

        self.add_button = Gtk.Button(label="+")
        self.add_button.connect("clicked", self.new_task)

    def new_task(self, button):
        i = 0


class TaskBox(Gtk.HBox):

    def __init__(self, task):
        super(TaskBox, self).__init__()
        self.task = task
        self.label = Gtk.Label(label=task['title'])
        self.pack_start(self.label, False, False, 30)
        self.completed = Gtk.CheckButton()
        self.pack_end(self.completed, False, False, 30)

    def get_status(self) -> bool:
        return self.completed.get_active()

    def set_status(self, status: bool) -> None:
        self.completed.set_active(status)
