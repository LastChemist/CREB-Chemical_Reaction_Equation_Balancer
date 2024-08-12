import json
import os


class Handler:
    """
    A class to handle reading, writing, updating, and removing JSON data files.

    Attributes:
        content : dict
            The content to be written to the JSON file.
        file_path : str
            The path to the JSON file.

    Methods:
        write(content: dict = {"equation_solution": "", "error_msg": ""}) -> None:
            Writes the given content to the JSON file.
        read() -> None:
            Reads the content from the JSON file.
        update(key: str, value) -> None:
            Updates the content in the JSON file with the given key-value pair.
        removeJsonDataFile() -> None:
            Removes the JSON data file if it exists.
    """

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes for the Handler object.
        """
        self.content = {"equation_solution": "", "error_msg": ""}
        self.file_path: str = rf"src\data.json"
        if not os.path.isfile(self.file_path):
            self.write(content=self.content)

    def write(self, content: dict = {"equation_solution": "", "error_msg": ""}) -> None:
        """
        Writes the given content to the JSON file.

        Parameters:
            content : dict
                The content to be written to the JSON file.
        """
        with open(self.file_path, "w") as file:
            json.dump(content, file)

    def read(self) -> None:
        """
        Reads the content from the JSON file.
        """
        with open(self.file_path, "r") as file:
            self.content = json.load(file)

    def update(self, key: str, value) -> None:
        """
        Updates the content in the JSON file with the given key-value pair.

        Parameters:
            key : str
                The key to be updated in the JSON file.
            value
                The value to be assigned to the key.
        """
        self.read()
        self.content[key] = value
        self.write(content=self.content)

    def removeJsonDataFile(self) -> None:
        """
        Removes the JSON data file if it exists.
        The data.json is a temporary file, so after a successful execution
        of equation balance it would be removed.
        """
        # the data.json is a temporary file, so after a successful execution
        # of equation balance it would be removed
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
