from datetime import datetime
import os

class BookLogger:
    def __init__(self, file_path: str, verbose: bool=True):
        self.file_path = file_path
        self.verbose = verbose
        
    def log(self, message: str):
        mode = 'a' if os.path.exists(self.file_path) else 'w'
        with open(self.file_path, mode) as file:
            file.write(f'{datetime.now()}: {message}')

        print(f'Logged: {message}')