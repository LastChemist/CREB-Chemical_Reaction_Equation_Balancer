import json
import os


class Handler:
    def __init__(self, file_path: str) -> None:
        self.content = {"equation_solution": "", "error_msg": ""}
        self.file_path: str = rf"{file_path}\data.json"
        if not os.path.isfile(self.file_path):
            self.write(content=self.content)

    def write(self, content: dict = {"equation_solution": "", "error_msg": ""})->None:
        with open(self.file_path, "w") as file:
            json.dump(content, file)

    def read(self)->None:
        with open(self.file_path, "r") as file:
            self.content = json.load(file)

    def update(self, key: str, value)->None:
        self.read()
        self.content[key] = value
        self.write(content=self.content)

    def removeJsonDataFile(self)->None:
        # the data.json is a temporary file, so after a successful execution 
        # of equation balance it would be removed
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)