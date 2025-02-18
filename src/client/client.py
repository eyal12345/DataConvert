from tkinter import *
from tkinter import messagebox
from src.client.share_methods import ShareTools

class Client(Frame):

    def __init__(self, manager, frame) -> None:
        super().__init__()
        self.manager = manager
        self.frame = frame
        self.index = 0
        self.rows = 0
        self.radio_var = None
        self.label = None
        self.feature = None
        self.select = None
        self.exit = None

    @ShareTools.clear_all_widgets
    def pipeline_frame(self) -> None:
        # create a radio buttons which is display all feature options to conversion
        self.create_radio_buttons()
        # create a select button that give to user to choose one item to conversion
        self.create_select_button()
        # create an exit button which is exit from app and ask the user if he sure
        self.create_exit_button()

    def create_radio_buttons(self) -> None:
        Label(self.frame, text="Select one option to convert:").grid(row=0, column=0, columnspan=4, padx=15, pady=10, sticky=W)
        # options for features choice
        options = ["URL", "Item 2", "Item 3"]
        # Create a variable to track the selected radio button
        self.radio_var = StringVar(value=options[self.index])
        # Create a radio buttons dynamically based on the list of options
        for index, option in enumerate(list(options)):
            self.feature = Radiobutton(self.frame, text=option, variable=self.radio_var, command=lambda index=index: self.update_select_choice(index), value=options[index])
            self.feature.grid(row=index + 1, column=0, padx=15, sticky=W)

    def update_select_choice(self, index) -> None:
        self.index = index

    def select_button_clicked(self) -> None:
        feature = self.radio_var.get()
        if feature == 'URL':
            self.manager.show_frame('URL')
        else:
            messagebox.showinfo(title='Info', message=f'{feature} feature not define yet')

    @ShareTools.get_widget_row(next_row=True)
    def create_select_button(self) -> None:
        self.select = Button(self.frame, text='Select', command=self.select_button_clicked, width=20)
        self.select.grid(row=self.rows, column=0, columnspan=2, padx=15, pady=10, sticky=W + E)

    @ShareTools.get_widget_row(next_row=False)
    def create_exit_button(self) -> None:
        self.exit = Button(self.frame, text='Exit', command=self.exit_app, width=20)
        self.exit.grid(row=self.rows, column=2, columnspan=2, padx=15, pady=10, sticky=W + E)

    def exit_app(self) -> None:
        result = messagebox.askquestion(title='Quit', message='Do you want to quit?')
        if result == 'yes':
            self.frame.destroy()
