import json, os
from collections import deque

class SensoryBuffer:
    def __init__(self, maxlen: int = 5):
        self.buf = deque(maxlen=maxlen)

    def add(self, features: dict):
        self.buf.append(features)

    def recent(self):
        return list(self.buf)
