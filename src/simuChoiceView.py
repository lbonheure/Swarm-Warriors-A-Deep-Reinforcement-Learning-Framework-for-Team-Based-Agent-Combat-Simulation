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
        
        self.rb_var = tk.IntVar(self, 0)
        self.r_simu = tk.Radiobutton(self, text="Random simulation", value=0, variable=self.rb_var)
        self.ia_simu = tk.Radiobutton(self, text="trained simulation", value=1, variable=self.rb_var)
        self.ok_button = tk.Button(self, text="OK", command=self._confirm)
        
        self.listener = None
        
    def set_listener(self, l: Listener):
        """
        Set the view listener
        :param l: the listener
        """
        self.listener = l
        
    def show(self):
        """
        Show the window
        """
        self.r_simu.pack(padx=5, pady=5)
        self.ia_simu.pack(padx=5, pady=5)
        self.ok_button.pack(padx=5, pady=5)


    def _confirm(self):
        if self.rb_var.get() == 0:
            self.listener.run_random_simu()
        else:
            self.listener.run_trained_simu()
        self.destroy()