import tkinter as tk

from AppView import AppView

class AppController(AppView.Listener):
    def __init__(self) -> None:
        self.appView = AppView()
        self.appView.setListener(self)

    def run(self):
        self.appView.show()
        self.appView.mainloop()


    def test_show_agents(self):
        # test
        agents = {"agent1": (3,3,"blue"), "agent2": (5,10,"green")}
        self.appView.show_agents(agents)