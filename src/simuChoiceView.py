import tkinter as tk


class SimuChoiceView(tk.Toplevel):
    class Listener:
        def run_random_simu(self):
            pass
        
        def run_trained_simu(self):
            pass
    
    def __init__(self, master):
        super().__init__(master)
        
        self.geometry('300x120')
        self.title('Choose a type of simulation')
        
        #self.start_button = ttk.Button(self, text='Progress', command=self.progress)
        #self.stop_button = ttk.Button(self, text='Stop', command=self.stop)
        self.rb_var = tk.IntVar(self, 0)
        self.r_simu = tk.Radiobutton(self, text="Random simulation", value=0, variable=self.rb_var)
        self.ia_simu = tk.Radiobutton(self, text="trained simulation", value=1, variable=self.rb_var)
        self.ok_button = tk.Button(self, text="OK", command=self._confirm)
        
        self.listener = None
        
    def set_listener(self, l: Listener):
        self.listener = l
        
    def show(self):
        print("see progress bar")
        self.r_simu.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        self.ia_simu.grid(column=0, row=1, columnspan=2)
        self.ok_button.grid(column=0, row=2, columnspan=2)


    def _confirm(self):
        if self.rb_var.get() == 0:
            self.listener.run_random_simu()
        else:
            self.listener.run_trained_simu()
        self.destroy()