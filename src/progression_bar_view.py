import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showinfo


class ProgressBarView(tk.Toplevel):
    def __init__(self, master, progressVar: tk.IntVar):
        super().__init__(master)
        
        self.geometry('300x120')
        self.title('Training progress')
        
        #self.start_button = ttk.Button(self, text='Progress', command=self.progress)
        #self.stop_button = ttk.Button(self, text='Stop', command=self.stop)
        self.pb = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=280, maximum=1000, variable=progressVar)
        self.pb.bind('Configure', self.update_progress_label)
        self.progressString = tk.StringVar(self, f"Current Progress: {self.pb['value']}%")
        self.value_label = ttk.Label(self, textvariable=self.progressString)
        
        
    def show(self):
        self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        self.value_label.grid(column=0, row=1, columnspan=2)
        #self.start_button.grid(column=0, row=2, padx=10, pady=10, sticky=tk.E)
        #self.stop_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)


    def update_progress_label(self, event):
        self.progressString.set(f"Current Progress: {self.pb['value']}%")


    def progress(self):
        if self.pb['value'] < 100:
            self.pb['value'] += 20
            self.value_label['text'] = self.update_progress_label()
        else:
            showinfo(message='The progress completed!')


    def stop(self):
        self.pb.stop()
        self.value_label['text'] = self.update_progress_label()