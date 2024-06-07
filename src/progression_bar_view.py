import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg


class ProgressBarView(tk.Toplevel):
    def __init__(self, master, value=200):
        super().__init__(master)
        
        self.geometry('300x120')
        self.title('Training progress')

        self.value = value
        
        self.progressVar = tk.IntVar(self, 0)
        self.progressString = tk.StringVar(self, f"Current Progress: {0}%")
        self.pb = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=280, maximum=self.value, variable=self.progressVar)
        self.value_label = ttk.Label(self, textvariable=self.progressString)
        
    def set_value(self, value):
        self.value = value
        self.pb = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=280, maximum=self.value,
                                  variable=self.progressVar)

    def show(self):
        self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        self.value_label.grid(column=0, row=1, columnspan=2)


    def update_progress(self, value):
        self.progressVar.set(value)
        self.progressString.set(f"Current Progress: {round(value/self.value*100, 1)}%")
        if value >= self.value:
            msg.showinfo(message="Training done!")
            self.destroy()