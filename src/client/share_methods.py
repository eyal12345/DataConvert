from tkinter import *

class ShareTools:

    @staticmethod
    # clear all widgets of previous component
    def clear_all_widgets(func):
        def wrapper(self, *args, **kwargs):
            for widget in self.frame.winfo_children():
                widget.destroy()
            func(self, *args, **kwargs)
        return wrapper

    @classmethod
    # get the match row of the widget in the frame's bottom by the user's design
    def get_widget_row(cls, next_row=None):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if next_row:
                    cols, rows = self.frame.grid_size()
                    self.rows = rows
                func(self, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    # increase by 1 the number of rows
    def increase_selected_row(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.written += 1
        return wrapper

    @staticmethod
    # update coordinates of technical buttons
    def update_coordinates_buttons(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            buttons = [item for item in self.frame.winfo_children() if isinstance(item, Button)]
            index = 0
            for _, button in enumerate(buttons):
                row = self.written
                items = button.grid_info()
                col = items['column']
                col_span = items['columnspan']
                sticky = items['sticky']
                button.grid_forget()
                button.grid(row=row, column=col, columnspan=col_span, padx=15, pady=10, sticky=sticky)
                if col_span == 4:
                    self.written = self.written + 1
                elif col_span == 2:
                    self.written = self.written + 1 if index % 2 == 1 else self.written
                    index = index + 1
        return wrapper
