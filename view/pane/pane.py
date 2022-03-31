#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Pane:
    def __init__(self):
        self._index = -1
        self._ui = None

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    # virtual
    def create_page(self):
        pass

    # virtual
    def load(self, ui):
        pass

    # virtual
    def save(self):
        pass
