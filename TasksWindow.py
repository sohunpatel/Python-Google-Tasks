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

SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']


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
        service = start_tasks_api()
        tasklists = get_tasklists(service)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        for tasklist in tasklists:
            self.page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.page.set_border_width(10)
            tasks = get_tasks(service, tasklist['id'])
            if tasks is not None:
                for task in tasks:
                    if task is None:
                        break
                    self.page.add(Gtk.Label(label=task['title']))
            self.notebook.append_page(self.page, Gtk.Label(label=tasklist['title']))
