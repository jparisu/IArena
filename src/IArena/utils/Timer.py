import time

class Timer:

    def __init__(self, start_activated=True):
        self.start_time = None
        self.elapsed_time = 0
        self.is_active = False

        if start_activated:
            self.start()

    def start(self):
        if not self.is_active:
            self.start_time = time.time()
            self.is_active = True

    def pause(self):
        if self.is_active:
            self.elapsed_time += time.time() - self.start_time
            self.is_active = False

    def reset(self):
        self.elapsed_time = 0
        if self.is_active:
            self.start_time = time.time()

    def elapsed(self):
        if self.is_active:
            return self.elapsed_time + time.time() - self.start_time
        else:
            return self.elapsed_time
