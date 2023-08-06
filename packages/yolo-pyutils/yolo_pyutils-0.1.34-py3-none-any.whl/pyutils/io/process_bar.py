import sys


class SimpleProgressBar:
    def __init__(self, description='', max=0, state=0, step=2):
        self.max = max
        self.state = state
        self.description = description
        self.step = step
        self.closed = False

    def __print(self, state):
        print("\r", end="")
        print("{}: {} {}".format(self.description, state, "/ {}".format(self.max) if self.max > 0 else ""),
              "▋" * (state // self.step), end="")

    def update(self, state=None):
        if state is not None:
            self.__print(state)
            if 0 < self.max == state:
                self.close()
            sys.stdout.flush()

    def close(self):
        if not self.closed:
            print("")
            self.closed = True
