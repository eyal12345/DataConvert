from tkinter import *
from tkinter import ttk
from src.client.share_methods import ShareTools

class URLProcess:

    def __init__(self, frame) -> None:
        self.frame = frame
        self.written = 3
        self.status = None
        self.sub_url = None
        self.per_url = None
        self.per_depth = None
        self.added = None
        self.so_far = None
        self.overall = None

    @ShareTools.update_coordinates_buttons
    def pipeline_frame(self) -> None:
        # create a text-label which is displaying the depth level of the root url that him extract now
        self.create_status_label()
        # create a text-label which is displaying the current father url that him extract now
        self.create_sub_url_label()
        # create a progress-bar for the progress all of sub-urls for each url
        self.create_per_url_progress()
        # create a progress-bar for the progress all of urls for each depth
        self.create_per_depth_progress()
        # create a text-label which is displaying how many urls added each extract of father url
        self.create_added_url_label()
        # create a text-label which is displaying how many urls accumulated so far from extract of each father url
        self.create_so_far_url_label()
        # create a text-label which is displaying how many urls accumulated in overall up to iteration depth
        self.create_overall_url_label()

    @ShareTools.increase_selected_row
    def create_status_label(self) -> None:
        self.status = Label(self.frame, text=f'initializes a process', width=40)
        self.status.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_sub_url_label(self) -> None:
        self.sub_url = Label(self.frame, text=f'', width=40)
        self.sub_url.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_per_url_progress(self) -> None:
        Label(self.frame, text=f'progress per url', width=40).grid(row=self.written, column=0, padx=15, columnspan=4)
        self.written = self.written + 1
        self.per_url = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', maximum=1, length=300)
        self.per_url.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_per_depth_progress(self) -> None:
        Label(self.frame, text=f'progress per depth', width=40).grid(row=self.written, column=0, padx=15, columnspan=4)
        self.written = self.written + 1
        self.per_depth = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', maximum=1, length=300)
        self.per_depth.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_added_url_label(self) -> None:
        self.added = Label(self.frame, text="waiting for new sources", width=40)
        self.added.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_so_far_url_label(self) -> None:
        self.so_far = Label(self.frame, text="number of sources in total so far is 0 ", width=40)
        self.so_far.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_overall_url_label(self) -> None:
        self.overall = Label(self.frame, text="overall there is no sources yet", width=40)
        self.overall.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)
