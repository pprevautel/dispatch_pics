import os
from datetime import date


class Logger:
    def __init__(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        self._path = os.path.join(file_path, 'logs')
        if not os.path.exists(self._path):
            os.mkdir(self._path)

    def log(self, error_msg):
        today = date.today()

        filename = 'log-{}'.format(today.strftime('%Y-%m-%d'))
        file_path = os.path.join(self._path, filename)
        f = os.open(file_path, 'a')

        message = '[{}] {}'.format(today.strftime('%H:%M:%S'), error_msg)
        f.write(message + '\n')
        f.close()