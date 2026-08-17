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
import requests
import zipfile
import shutil
import io
import os
import re

# formats which hold a table, they are displayed by excel and not by the program which
# windows connects to them, a table in a text editor is unreadable
TABLE_FORMATS = ("csv", "xlsx")
# formats which are plain text, they are displayed by notepad and not by the program which
# windows connects to them, an editor of code opens slowly and holds his own window
TEXT_FORMATS = ("txt", "json", "yml")
# the site which publishes the tool of sqlite and the name of his archive for windows,
# sqlite has no installer, his console tool is a single exe inside an archive
SQLITE_SITE = 'https://sqlite.org/'
SQLITE_PAGE = SQLITE_SITE + 'download.html'
SQLITE_ARCHIVE = re.compile(r'\d{4}/sqlite-tools-win-x64-\d+\.zip')
# the folder of the application which keeps the tool when the machine does not have him,
# so the download happens once and every next display uses the tool which is already here
SQLITE_FOLDER = 'tools/sqlite'
# seconds to wait for the download of the tool, he weighs a few megabytes
SQLITE_TIMEOUT = (5, 30)

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
        fix_format = format if format in options else 'txt'
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
            # the file is opened by his full address, a relative address depends on the
            # folder which the application was started from and the program misses him
            path = os.path.abspath(self.full_path) if self.full_path else ''
            if not path or not os.path.exists(path):
                raise IOError('The result file does not exist, convert him before his display')
            if format == "db":
                # a database is not a file which a program displays, his rows are shown
                # by the tool of sqlite in a console window
                sqlite_path = os.path.join(self.get_sqlite_path(), 'sqlite3.exe')
                cmd_command = [
                    "start", "cmd", "/k",
                    sqlite_path, path, ".mode column", ".header on", "SELECT * FROM RESULTS;"
                ]
                subprocess.run(cmd_command, shell=True, check=True)
            elif format in TABLE_FORMATS:
                # a table belongs to excel, windows does not connect csv to him by himself
                # and answers a request to open him with a window of choosing a program
                subprocess.run(f'start excel "{path}"', shell=True, check=True)
            elif format in TEXT_FORMATS:
                # notepad displays the text as him is, without an editor which windows
                # connects to the extension and opens him in his own project
                subprocess.run(f'notepad.exe "{path}"', shell=True, check=True)
            else:
                self.open_by_format(path)
        except Exception as err:
            # a failure of the display must be seen, otherwise the button looks broken
            messagebox.showerror(title='Error', message=str(err))

    def open_by_format(self, path: str) -> None:
        """
        open the result file with the program which the machine connects to his extension, so
        each format is displayed by the tool which matches him and not all of them as text
        parameters:
            path (str): the full address of the result file
        """
        try:
            os.startfile(path)
        except OSError:
            # no program on this machine is connected to that extension, every format of the
            # export is a text file underneath, so he is readable as plain text
            subprocess.run(f'notepad.exe "{path}"', shell=True, check=True)

    def get_sqlite_path(self) -> str:
        """
        return the folder which holds the console tool of sqlite, the tool is searched in the
        paths of the machine and in the folder of the application, and when he is missing on
        both of them he is downloaded, so a database is displayable also without an install
        returns:
            path (str): the folder which the tool of sqlite is found in
        """
        # a path of the machine may not exist at all, such a path holds no tool
        directories = os.environ.get('PATH', '').split(os.pathsep) + [os.path.abspath(SQLITE_FOLDER)]
        sqlite_path = [path for path in directories if path and os.path.exists(os.path.join(path, 'sqlite3.exe'))]
        return sqlite_path[0] if sqlite_path else self.install_sqlite()

    def install_sqlite(self) -> str:
        """
        download the console tool of sqlite into the folder of the application, the tool is
        not installed on the machine and without him a database has nothing which shows him
        returns:
            path (str): the folder which the tool was downloaded into
        """
        answer = messagebox.askquestion(title='Install', message='sqlite3 is not installed on this '
                                        'machine and a database is displayed by him.\n\n'
                                        'Do you want to download him now from sqlite.org?')
        if answer != 'yes':
            raise IOError('sqlite3 is not installed, so a database cannot be displayed')
        folder = os.path.abspath(SQLITE_FOLDER)
        os.makedirs(folder, exist_ok=True)
        try:
            # the address of the archive holds his version, so him is taken from the page of
            # the downloads himself and not written here, a written version expires with the next
            page = requests.get(SQLITE_PAGE, timeout=SQLITE_TIMEOUT)
            archive = SQLITE_ARCHIVE.search(page.text)
            if not archive:
                raise IOError('The tool of sqlite is not published for this system, so a database '
                              'cannot be displayed, install sqlite3 by yourself and try again')
            content = requests.get(SQLITE_SITE + archive.group(0), timeout=SQLITE_TIMEOUT)
        except requests.exceptions.RequestException as err:
            raise IOError(f'The tool of sqlite could not be downloaded from {SQLITE_SITE}, check '
                          f'the connection to the network and try again')
        with zipfile.ZipFile(io.BytesIO(content.content)) as package:
            # the archive holds his files inside an inner folder, only the tool himself
            # is needed and not the rest of the tools which are published with him
            for member in package.namelist():
                if member.endswith('sqlite3.exe'):
                    with package.open(member) as source, open(os.path.join(folder, 'sqlite3.exe'), 'wb') as target:
                        shutil.copyfileobj(source, target)
                    return folder
        raise IOError('The archive of sqlite does not hold his console tool')

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
        except Exception as err:
            # an unexpected failure must not leave the export button disabled forever
            self.export.config(state=NORMAL)
            messagebox.showerror(title='Error', message=str(err))

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
            self.convert.config(state=NORMAL)
            messagebox.showerror(title='Error', message=err)
        except (TclError, RuntimeError) as err:
            pass
        except Exception as err:
            # an unexpected failure must not leave the convert button disabled forever
            self.convert.config(state=NORMAL)
            messagebox.showerror(title='Error', message=str(err))

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
            # initialize attributes accordingly
            self.path = None
            self.datasets = None
            # save data and back to main frame
            self.save_user_choices()
            self.manager.show_frame('Select')
