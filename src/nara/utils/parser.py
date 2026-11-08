import shlex
import argparse

class Parser:

    def __init__(self, *args, **kwargs):
        self.setup()

    def setup(self):
        self.setParser()
        self.m_subparsers = {}

    def addArgument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def newArgParser(self, *args, **kwargs):
        return Parser(*args, **kwargs)

    def newParser(self, *args, **kwargs):
        return argparse.ArgumentParser(**kwargs)

    def setParser(self, **kwargs):
        self.parser = self.newParser(
            exit_on_error=False, **kwargs
        )

    def addSubParser(self, *args, **kwargs):
        return self.parser.add_subparsers(*args, **kwargs)

    def split(self, text):
        return shlex.split(text)

    def parse(
        self,
        text=None,
        pref=None,
        only_known=True,
    ):
        functor = self.parser.parse_args
        if only_known:
            functor = self.parser.parse_known_args
        if text:
            text = shlex.split(text)
            if pref:
                text.insert(0, pref)
            return functor(text)
        return functor()
