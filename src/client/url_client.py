from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from src.client.share_methods import ShareTools
from src.server.url_server import URLServer
from src.server.format_server import FormatServer
from functools import partial
import subprocess
import threading
import argparse
import datetime
import os

class URLClient(Frame):

    def __init__(self, manager, frame) -> None:
        super().__init__()
        self.manager = manager
        self.frame = frame
        self.rows = 0
        self.entry1 = None
        self.entry2 = None
        self.entry3 = None
        self.prev_format = None
        self.path = None
        self.datasets = None
        self.full_path = None
        self.args = None
        self.display = None
        self.export = None
        self.convert = None
        self.restart = None
        self.back = None

    @ShareTools.clear_all_widgets
    def pipeline_frame(self) -> None:
        # get cli arguments parameters by user choice if exists
        self.load_user_choices() if not self.args else None
        # create text-field for root url and put him the user's argument if exist
        self.create_url_component()
        # create drop-down list for depth and put him the user's argument if exist
        self.create_depth_component()
        # create drop-down list for format and put him the user's argument if exist
        self.create_format_component()
        # create display button which show requested file format
        self.create_display_button()
        # create run button which is exporting data by all defined settings and building part of path to result file
        self.create_export_button()
        # create display button which is creating file in required format and displaying him to user
        self.create_convert_button()
        # create restart button which is config widgets and attributes accordingly
        self.create_restart_button()
        # create back button which is return to the previous page
        self.create_back_button()

    def load_user_choices(self) -> None:
        try:
            parser = argparse.ArgumentParser(description='Enter root link with max depth for scanning')
            parser.add_argument('-r', '--root', help="Main page from start scan", type=str, required=False)
            parser.add_argument('-d', '--depth', help="Max depth for scanning", type=int, required=False)
            parser.add_argument('-f', '--format', help="File result format for display", type=str, required=False)
            self.args = vars(parser.parse_args())
        except SystemExit as err:
            self.args = None

    def save_user_choices(self) -> None:
        self.args['root'] = self.entry1.get()
        self.args['depth'] = int(self.entry2.get())
        self.args['format'] = self.entry3.get()

    def create_url_component(self) -> None:
        ttk.Label(self.frame, text="root url:").grid(row=0, column=0, padx=15, pady=10, sticky=W)
        # put root value by user's choice
        root = self.args['root']
        fix_root = root if root else ''
        # create entry with default value
        self.entry1 = ttk.Entry(self.frame, width=40)
        self.entry1.grid(row=0, column=1, columnspan=3, padx=15, pady=10, sticky=W)
        self.entry1.insert(0, fix_root)

    def create_depth_component(self) -> None:
        ttk.Label(self.frame, text="depth:").grid(row=1, column=0, padx=15, pady=10, sticky=W)
        # options for url depths
        options = ["0", "1", "2", "3"]
        # put depth value depending on the user's choice
        depth = self.args['depth']
        fix_depth = min(len(options) - 1, depth) if depth else 0
        # create combobox with default value
        self.entry2 = ttk.Combobox(self.frame, values=options, width=5)
        self.entry2['values'] = tuple(options)
        self.entry2.grid(row=1, column=1, padx=15, pady=10, sticky=W)
        self.entry2.set(fix_depth)
        # bind the selection event to the on_combobox_selection function
        self.entry2.bind("<<ComboboxSelected>>", self.on_combobox_selection_depth)

    def on_combobox_selection_depth(self, event=None) -> None:
        # retrieve the selected value from the combobox
        pass

    def create_format_component(self) -> None:
        ttk.Label(self.frame, text="format:").grid(row=2, column=0, padx=15, pady=10, sticky=W)
        # options for convert data
        options = ["txt", "csv", "json", "yml", "xml", "xlsx", "db"]
        # put format type by user's choice
        format = self.args['format']
        fix_format = format if format else 'txt'
        # save found values in the attributes accordingly
        self.prev_format = fix_format
        # create combobox with default value
        self.entry3 = ttk.Combobox(self.frame, values=options, width=5)
        self.entry3.grid(row=2, column=1, padx=15, pady=10, sticky=W)
        self.entry3.set(fix_format)
        # bind the selection event to the on_combobox_selection function
        self.entry3.bind("<<ComboboxSelected>>", self.on_combobox_selection_format)

    def on_combobox_selection_format(self, event=None) -> None:
        # get format argument from the UI
        format = self.entry3.get()
        # retrieve the selected value from the combobox
        if self.path and self.datasets:
            # configure widgets accordingly
            if self.prev_format != format:
                self.display.config(state=DISABLED)
                self.convert.config(state=NORMAL)
            elif self.full_path:
                self.display.config(state=NORMAL)
                self.convert.config(state=DISABLED)

    @ShareTools.get_widget_row(next_row=True)
    def create_display_button(self) -> None:
        self.display = Button(self.frame, text='Display', command=partial(self.on_button_click_display), state=DISABLED, width=20)
        self.display.grid(row=self.rows, column=0, columnspan=4, padx=15, pady=10, sticky=W+E)

    def on_button_click_display(self) -> None:
        # Create and start new thread for the long-running task
        thread = threading.Thread(target=self.display_app)
        thread.start()

    @ShareTools.get_widget_row(next_row=True)
    def create_export_button(self) -> None:
        self.export = Button(self.frame, text='Export', command=partial(self.on_button_click_export), width=20)
        self.export.grid(row=self.rows, column=0, columnspan=2, padx=15, pady=10, sticky=W)

    def on_button_click_export(self) -> None:
        # Create and start new thread for the long-running task
        thread = threading.Thread(target=self.export_app)
        thread.start()

    def display_app(self) -> None:
        try:
            # get format argument from the UI
            format = self.entry3.get()
            # initialize cmd command
            cmd_command = ''
            # open associated file of the format
            if format in ["txt", "csv", "json", "yml", "xml"]:
                cmd_command = f'notepad.exe "{self.full_path}"'
            elif format in ["xlsx"]:
                cmd_command = f'start excel "{self.full_path}"'
            elif format in ["db"]:
                sqlite_path = self.get_sqlite_path()
                cmd_command = [
                    "start", "cmd", "/k",
                    f'{sqlite_path}\\sqlite3.exe', self.full_path, ".mode column", ".header on", "SELECT * FROM RESULTS;"
                ]
            subprocess.run(cmd_command, shell=True, check=True)
        except IndexError as err:
            messagebox.showerror(title='Error', message=str(err))

    def get_sqlite_path(self) -> str | None:
        path_directories = os.environ.get('PATH').split(os.pathsep)
        sqlite_path = [path for path in path_directories if os.path.exists(path + r'\sqlite3.exe')]
        if sqlite_path:
            return sqlite_path[0]
        else:
            raise IndexError("sqlite3 not installed on your system environment variable paths")

    def export_app(self) -> None:
        try:
            # configure widgets accordingly
            self.export.config(state=DISABLED)
            # get root and depth arguments from the UI
            root = self.entry1.get()
            depth = int(self.entry2.get())
            # extract all sub-server from root item
            path, datasets = URLServer(self.frame, root, depth).run_progress()
            # configure widgets accordingly
            self.convert.config(state=NORMAL)
            self.restart.config(state=NORMAL)
            # save found values in the attributes accordingly
            self.path = path
            self.datasets = datasets
        except IOError as err:
            self.export.config(state=NORMAL)
            messagebox.showerror(title='Error', message=err)
        except (TclError, RuntimeError) as err:
            pass

    @ShareTools.get_widget_row(next_row=False)
    def create_convert_button(self) -> None:
        self.convert = Button(self.frame, text='Convert', command=partial(self.on_button_click_convert), state=DISABLED, width=20)
        self.convert.grid(row=self.rows, column=2, columnspan=2, padx=15, pady=10, sticky=E)

    def on_button_click_convert(self) -> None:
        # Create and start a new thread for the long-running task
        thread = threading.Thread(target=self.convert_app)
        thread.start()

    def create_folder_source(self) -> None:
        folder = '/'.join(self.path.split('/')[:-1])
        if not os.path.exists(folder):
            os.makedirs(folder)

    def convert_app(self) -> None:
        try:
            # configure widgets accordingly
            self.convert.config(state=DISABLED)
            # get format argument from the UI
            format = self.entry3.get()
            # create folder for result file if not exists
            self.create_folder_source() if self.path and self.datasets else None
            # create full path with current timestamp
            timestamp = datetime.datetime.now().strftime('%m-%d-%Y %H-%M-%S')
            self.full_path = self.path.replace('/', '\\') + "_" + timestamp + "." + format
            # remove the format process frame
            self.destroy_process_frame(17)
            # create results file by user's format
            FormatServer(self.frame, self.full_path, self.datasets).run_progress()
            # configure widgets accordingly
            self.display.config(state=NORMAL)
            # save found values in the attributes accordingly
            self.prev_format = format
        except IOError as err:
            messagebox.showerror(title='Error', message=err)
        except (TclError, RuntimeError) as err:
            pass

    @ShareTools.get_widget_row(next_row=True)
    def create_restart_button(self) -> None:
        self.restart = Button(self.frame, text='Restart', command=self.restart_app, state=DISABLED, width=20)
        self.restart.grid(row=self.rows, column=0, columnspan=2, padx=15, pady=10, sticky=W)

    def destroy_process_frame(self, index) -> None:
        delete = self.frame.winfo_children()[index:]
        for widget in delete:
            widget.destroy()

    def restart_app(self) -> None:
        result = messagebox.askquestion(title='Restart', message='Do you want to restart?')
        if result == 'yes':
            # configure widgets accordingly
            self.display.config(state=DISABLED)
            self.export.config(state=NORMAL)
            self.convert.config(state=DISABLED)
            self.restart.config(state=DISABLED)
            # remove the url process frame
            self.destroy_process_frame(11)
            # initialize attributes accordingly
            self.path = None
            self.datasets = None

    @ShareTools.get_widget_row(next_row=False)
    def create_back_button(self) -> None:
        self.back = Button(self.frame, text='Back', command=self.back_app, width=20)
        self.back.grid(row=self.rows, column=2, columnspan=2, padx=15, pady=10, sticky=E)

    def back_app(self) -> None:
        result = messagebox.askquestion(title='Back', message='Do you want to back?')
        if result == 'yes':
            self.save_user_choices()
            self.manager.show_frame('Select')
