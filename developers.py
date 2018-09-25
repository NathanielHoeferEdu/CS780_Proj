"""Module containing the classes for evaluating developer comments."""

class DevProcessing:
    pass

class Developer:
    pass

class Diff:
    def __init__(self, diff):
        self.diff = diff

    @property
    def diff(self):
        return self.diff

    def comments(self):
        return [""]