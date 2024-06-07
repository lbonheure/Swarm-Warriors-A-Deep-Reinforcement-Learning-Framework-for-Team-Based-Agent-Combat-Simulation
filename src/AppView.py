import tkinter as tk

from grid import Grid


class AppView(tk.Tk):
    class Listener:
        def random_move(self):
            pass

        def new_map(self):
            pass

        def save_map(self):
            pass

        def load_map(self):
            pass

        def train_model(self):
            pass

        def run_simu(self):
            pass

        def stop_simu(self):
            pass

        def modify_speed(self, value):
            pass

        def reset(self):
            pass

    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk",
                 useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        # Window configuration
        self.geometry("850x750")
        self.configure(cursor="arrow")
        self.minsize(850, 750)
        self.resizable(True, True)
        self.title("Grid")

        # Widgets in the view
        self.buttons_frame = tk.Frame(self)
        self.move_button = tk.Button(self.buttons_frame, text="Random Move", command=self._call_controller_random_move)
        self.new_map_button = tk.Button(self.buttons_frame, text="New map", command=self._call_controller_new_map)
        self.save_map_button = tk.Button(self.buttons_frame, text="Save map", command=self._call_controller_save_map)
        self.load_map_button = tk.Button(self.buttons_frame, text="Load map", command=self._call_controller_load_map)
        self.train_button = tk.Button(self.buttons_frame, text="Train model", command=self._call_controller_train_model)
        self.run_button = tk.Button(self.buttons_frame, text="Run", command=self._call_controller_run_simu)
        self.stop_button = tk.Button(self.buttons_frame, text="Stop", command=self._call_controller_stop_simu)
        self.speed_label = tk.Label(self.buttons_frame, text="Speed:")
        self.speed_var = tk.IntVar(self.buttons_frame, value=5)
        self.speed_cursor = tk.Scale(self.buttons_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.speed_var)
        self.reset_button = tk.Button(self.buttons_frame, text="Reset", command=self._call_controller_reset)

        # Other attributes
        self.grid = None
        self.listener = None

    def setListener(self, l: Listener):
        """
        Set the listener
        :param l (Listener): the new listener
        """
        self.listener = l

    def get_speed_simu(self):
        """
        Return the variable that contains the speed of the simulation
        :return: dynamic variable containing the speed of the simulation
        """
        return self.speed_var

    def createGrid(self, map=None) -> Grid:
        """
        Create a new grid
        :param map (Map, optional): the map showed by the grid
        :return: the new grid
        """
        if self.grid:
            self.grid.destroy()
        self.grid = Grid(self, map)
        return self.grid

    def show(self):
        """
        Show the view
        """
        self.new_map_button.pack(side="left", padx=10, pady=5)
        self.save_map_button.pack(side="left", padx=10, pady=5)
        self.load_map_button.pack(side="left", padx=10, pady=5)
        self.train_button.pack(side="left", padx=10, pady=5)
        self.move_button.pack(side="left", padx=10, pady=5)
        self.run_button.pack(side="left", padx=10, pady=5)
        self.stop_button.pack(side="left", padx=10, pady=5)
        self.speed_label.pack(side="left", padx=[10, 1], pady=5)
        self.speed_cursor.pack(side="left", padx=[1, 10], pady=5)
        self.reset_button.pack(side="left", padx=10, pady=5)
        self.buttons_frame.pack(side="top")
        self.grid.show()

    def _call_controller_random_move(self):
        self.listener.random_move()

    def _call_controller_new_map(self):
        self.listener.new_map()

    def _call_controller_run_simu(self):
        self.listener.run_simu()

    def _call_controller_stop_simu(self):
        self.listener.stop_simu()

    def _call_controller_modify_speed(self, value):
        self.listener.modify_speed(int(value))

    def _call_controller_train_model(self):
        self.listener.train_model()

    def _call_controller_save_map(self):
        self.listener.save_map()

    def _call_controller_load_map(self):
        self.listener.load_map()

    def _call_controller_reset(self):
        self.listener.reset()
