import asyncio
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from signin import SigninPage
from rightsidebar_new import RightSidebar
from leftsidebar import SidebarLeft
from content import Content
from navbar import Navbar

from fileApp import FileApp, Group

import logging

# Configure the logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Save logs to a file
        # logging.StreamHandler()  # Print logs to the console
    ]
)

import threading

class MyThread(threading.Thread):
    def __init__(self, handler, event_filter_getter, group, poll_interval=2):
        super().__init__()
        # self.target_function = target_function
        self.handler = handler
        self.event_filter_getter = event_filter_getter
        self.group = group
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            event_filter = self.event_filter_getter()
            for event in event_filter.get_new_entries():
                self.handler(self.group, event)
            time.sleep(self.poll_interval)
            logging.error(f'listening to {event_filter}')
            if self._stop_event.is_set():
                break


class App(tk.Tk):
    def __init__(self, file_app):
        tk.Tk.__init__(self)
        self.title("React App")
        self.geometry("1000x600")

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.file_app = file_app
        self.loop = None
        self.thread_ = None
        self.threads = []

        self.signin_page = SigninPage(self.container, self.show_main_content, self.file_app)
        self.signin_page.pack(fill=tk.BOTH, expand=True)

        self.show_signin_page()

    def show_signin_page(self):
        # self.main.pack_forget()
        self.signin_page.pack(fill=tk.BOTH, expand=True)

    def show_main_content(self, file_app):
        self.file_app = file_app
        print('groups from main: ', file_app.groups.keys())
        self.signin_page.pack_forget()

        self.main = Main(self.container, self.file_app, self)
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.main.load_groups()
        self.after(500, self.start_asyncio_loop)
    
    def start_adding_events(self):
        # self.create_task(self.file_app.new_invite_event_filter, '', self.main.handle_new_invite)
        # self.create_task(self.file_app.new_invite_event_filter, '', self.main.handle_new_invite)
        for group in self.file_app.groups.values():
            print(f'Adding events for: {group.name}^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            self.create_task(group.new_member_event_filter, group, self.main.handle_new_member)
            self.create_task(group.new_proposal_event_filter, group, self.main.handle_new_proposal)
            self.create_task(group.proposal_accepted_event_filter, group, self.main.handle_proposal_accepted)
            self.create_task(group.proposal_rejected_event_filter, group, self.main.handle_proposal_rejected)



    def create_task(self, event_filter_getter,group, handler, poll_interval=1):
        def polling():
            while True:
                event_filter = event_filter_getter()
                for event in event_filter.get_new_entries():
                    handler(group, event)
                time.sleep(poll_interval)
                # print(f'listening to ', event_filter)
                logging.error(f'listening to {event_filter}')
        t = threading.Thread(target=polling)
        t.start()
        print(f"Started Thread for {group.name}XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        self.threads.append(t)


    def start_asyncio_loop(self):
        print('starting async loop!!!!!!!!!!!!')
        self.thread_ = threading.Thread(target=self.start_adding_events)
        # self.start_adding_events()
        self.thread_.start()

        # self.loop.create_task(subscribe_func())

    def on_closing(self):
        self.file_app.save_state()
        self.destroy()
        if self.threads:
            for t in self.threads:
                if t:
                    t.stop()


class Main(tk.Frame):
    def __init__(self, parent, file_app, _app, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.configure(background='#25274d')
        self._app = _app
        self.file_app = file_app
        self.curr_group_address = ''
        self.curr_group = None

        self.sidebar_left = SidebarLeft(self, file_app)
        self.sidebar_left.pack(side=tk.LEFT, anchor=tk.NW)

        self.sidebar_right = RightSidebar(self, file_app)
        self.sidebar_right.pack(side=tk.RIGHT, anchor=tk.NE)

        self.navbar = Navbar(self, file_app)
        self.navbar.pack(side=tk.TOP, fill=tk.X)

        self.content = Content(self, file_app)
        self.content.pack(fill=tk.BOTH, expand=True)

    def load_groups(self):
        self.sidebar_left.update_group_list()

    def new_group(self, group_name):
        group = None
        for grp in self.file_app.groups.values():
            if grp.name == group_name:
                group = grp
                break
        else:
            return
        
        self._app.create_task(group.new_member_event_filter, group, self.handle_new_member)
        self._app.create_task(group.new_proposal_event_filter, group, self.handle_new_proposal)
        self._app.create_task(group.proposal_accepted_event_filter, group, self.handle_proposal_accepted)
        self._app.create_task(group.proposal_rejected_event_filter, group, self.handle_proposal_rejected)
        
        
    
    def update_curr_group(self, group_address):
        self.curr_group_address = group_address
        self.curr_group = self.file_app.groups[group_address]
        self.content.update_content_view()
        self.sidebar_right.update_view()
    

    def invite_accepted(self, group_name):
        self.sidebar_left.update_group_list()
        self.new_group(group_name)


    def handle_user_registerd(self, event):
        self.file_app.handle_user_registered(event)
    
    def handle_new_invite(self, event):
        self.file_app.handle_new_invite(event)

    def handle_new_member(self, group, event):
        group.handle_new_member(event)
        if self.curr_group == group:
            self.sidebar_right.update_view()

    def handle_new_proposal(self, group, event):
        # print('print got new proposal')
        print('PRINT GOT NEW PROPOSAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        group.handle_new_proposal(event)
        if self.curr_group == group:
            self.sidebar_right
    
    def handle_proposal_accepted(self, group, event):
        print(f'Proposal accepted for group {group.name}FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        logging.error(f'print proposal accepted for group {group.name}')
        group.handle_proposal_accepted(event)
        if self.curr_group == group:
            self.sidebar_right.update_view()
            self.content.update_content_view()

    def handle_proposal_rejected(self, group, event):
        group.handle_proposal_rejected(event)
        if self.curr_group == group:
            self.sidebar_right.update_view()
    



if __name__ == '__main__':
    file_app = FileApp()
    app = App(file_app)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
