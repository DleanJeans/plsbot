import time

class Multimer:
    def __init__(self):
        self.timers = {}
        self.flags = {}

    def set_flag(self, name, enabled):
        self.flags[name] = enabled
    
    def toggle(self, name):
        self.set_flag(name, not self.is_enabled(name))
    
    def is_enabled(self, name):
        return self.flags.get(name, True)

    def start(self, name, seconds):
        timeout = time.time() + seconds
        self.timers[name] = timeout
        if name not in self.flags:
            self.set_flag(name, True)
    
    def over(self, name):
        now = time.time()
        timeout = self.timers.get(name, 0)
        return now >= timeout and self.is_enabled(name)