import os
from concurrent.futures import ThreadPoolExecutor


class WheelReinventor(object):

    def __init__(self):
        self.pool = None
        self.cache = {}

    def get_details(self, wheel_path):
        if wheel_path.endswith("]"):
            wheel_path = wheel_path[:wheel_path.rindex("[")]
        if wheel_path in self.cache:
            return self.cache[wheel_path]
        if not os.path.isfile(wheel_path):
            raise OSError
        if self.pool is None:
            self.pool = ThreadPoolExecutor()
