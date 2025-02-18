from tkinter import *
from tkinter import ttk
from src.client.share_methods import ShareTools

class FormatProcess:

    def __init__(self, frame) -> None:
        self.frame = frame
        self.written = 10
        self.status = None
        self.convert = None

    @ShareTools.update_coordinates_buttons
    def pipeline_frame(self) -> None:
        # create a text-label which is displaying the status of a convert progress
        self.create_status_label()
        # create a progress-bar for the process of the convert data to required format
        self.create_convert_progress()

    @ShareTools.increase_selected_row
    def create_status_label(self) -> None:
        self.status = Label(self.frame, text=f'initializes a process', width=40)
        self.status.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)

    @ShareTools.increase_selected_row
    def create_convert_progress(self) -> None:
        Label(self.frame, text=f'progress for convert', width=40).grid(row=self.written, column=0, padx=15, columnspan=4)
        self.written = self.written + 1
        self.convert = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', maximum=1, length=300)
        self.convert.grid(row=self.written, column=0, padx=15, pady=10, columnspan=4)
