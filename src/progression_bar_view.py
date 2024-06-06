import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg


class ProgressBarView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.geometry('300x120')
        self.title('Training progress')
        
        #self.start_button = ttk.Button(self, text='Progress', command=self.progress)
        #self.stop_button = ttk.Button(self, text='Stop', command=self.stop)
        self.progressVar = tk.IntVar(self, 0)
        self.progressString = tk.StringVar(self, f"Current Progress: {0}%")
        self.pb = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=280, maximum=100, variable=self.progressVar)
        self.value_label = ttk.Label(self, textvariable=self.progressString)
        
        
    def show(self):
        print("see progress bar")
        self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        self.value_label.grid(column=0, row=1, columnspan=2)
        #self.start_button.grid(column=0, row=2, padx=10, pady=10, sticky=tk.E)
        #self.stop_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)


    def update_progress(self, value):
        self.progressVar.set(value)
        self.progressString.set(f"Current Progress: {value}%")
        if value >= 100:
            msg.showinfo(message="Training done!")
            self.destroy()