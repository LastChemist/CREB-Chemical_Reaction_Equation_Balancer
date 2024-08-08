import json
import os


class Handler:
    def __init__(self, file_path: str) -> None:
        self.content = {"equation_solution": "", "error_msg": ""}
        self.file_path: str = rf"{file_path}\data.json"
        if not os.path.isfile(self.file_path):
            self.write(content=self.content)
    
