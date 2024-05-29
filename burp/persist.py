import os 
import json 
import pickle
from typing import (
    List,
    Optional,
    Dict
)
import msvcrt

class DataPersistSettings:
    """
    Base class for data persistence settings.
    """
    DEFAULT_FOLDER = 'data' # describes the database name
    DEFAULT_EXTENSION = '.json'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, folder=None, extension=None, encoding=None):
        """
        Initializes settings with optional overrides.
        """
        self.folder = folder or self.DEFAULT_FOLDER
        self.extension = extension or self.DEFAULT_EXTENSION
        self.encoding = encoding or self.DEFAULT_ENCODING
      

class DataPersister:
    """
    Base class for data persisters.
    """

    def __init__(self, settings):
        """
        Initializes the persister with settings.
        """
        self.settings = settings
        self.file_creation = "" # for creating a first instance of the file
        self.db_filepath = ""
        self.filepath = None
        # Permissions for directory and file (octal format)
        self.directory_permissions = 0o755  # Read, write, and execute for owner, read and execute for group and others
        self.file_permissions = 0o664      # Read and write for owner, read for group and others
        self.indent = 4

    
    def create_table_file(self, filename, foldername, 
                        data = {}
                        ):
        """
        First creates a file with the table name with empty data 
        Saves data to a file based on settings.
        

        Raises:
            OSError: If an error occurs while creating the folder or saving the data.
        """
        db_filepath = os.path.join(foldername, filename + self.settings.extension)
        db_filepath = os.path.join(os.getcwd(), db_filepath)
        if not self.check_exists(db_filepath):
            # Create the folder if it doesn't exist
            os.makedirs(os.path.join(os.getcwd(), foldername), exist_ok=True)  # exist_ok=True prevents errors if folder exists
            print(os.path.join(os.getcwd(), foldername))
            #os.chmod(db_filepath, self.file_permissions)
            #os.chmod(os.path.join(os.getcwd(), foldername), self.directory_permissions)
        try:
            with open(db_filepath, 'w') as persistent_file:
                json.dump(data, persistent_file)

        except Exception as e:
            raise Exception(f"Error saving data to file: {db_filepath} with error {e}")
        else:
            print(f"The table {db_filepath} already exists")
        print(db_filepath)
        self.db_filepath = db_filepath
        return db_filepath
    
     
    def check_exists(self, path):
        """
        Checks if a file or folder exists at the specified path.

        Args:
            path: The path to the file or folder.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return os.path.exists(path)
    
    def save_data(self, data: Dict,
                  file_name: str,
                  folder_name: str,
                  extension: str,
                  encoding: str = None,
                  )-> str: 
        """
        Saves the data

        Args:
            folder_name: The path to the folder.
            file_name: The file name.
            extension: The extension of the file defaults = 'json'.
            encoding: Optional 

        Returns:
            str: file path to the saved data locally.
        """
        if not encoding:
            encoding = self.settings.encoding
        filepath = os.path.join(os.getcwd(), folder_name, file_name + extension)
        self.filepath = filepath
        print(self.filepath)
        if not self.check_exists(self.filepath):
            print(f"The given file path:  {filepath} does not exist")
        else:
            print("File already exists")
        # try:
        #     # Open the file in read mode
        #     # Handle cases where the file is missing or corrupt
        #     #os.chmod(self.filepath, self.file_permissions)
        #     # print(f"Permission to the file {filepath} is granted")
        #     with open(self.filepath, 'r+') as persistent_file:
        #         existing_data = json.load(persistent_file)
        #         if not existing_data:
        #             existing_data = {}
        #         existing_data.update(data)
                
        # except (FileNotFoundError, json.JSONDecodeError):
        #     print(f"The file not found {filepath}")
        # print(existing_data)
        print(data)
        try:
            with open(self.filepath, 'w') as persistent_file:
                print("Locking the file")
                msvcrt.locking(persistent_file.fileno(), msvcrt.LK_NBLCK, 100)  # Acquire lock with timeout in 100ms
                print("File locked")
                json.dump(data, persistent_file, indent=self.indent)
                msvcrt.locking(persistent_file.fileno(), msvcrt.LK_UNLCK, 100) # Unlock the file
                print("File unlocked")
        # Load existing data as a dictionary  
        except BlockingIOError:  # Handle lock acquisition timeout
            print("Failed to acquire lock on file. Retrying...")
            # Implement retry logic or error handling as needed

        finally:
            # Release the lock after writing (assuming successful acquisition)
            print(f"The status of the file is : {persistent_file.closed}")

        return self.filepath
    
    def delete_file(self, file_name: str, folder_name: str, extension: str):
        filepath = os.path.join(os.getcwd(), folder_name, file_name + extension)
        # Delete the file
        try:
            os.remove(filepath)
            print(f"File '{filepath}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{filepath}' not found.")
            
    def load_data(self, folder_name: str, file_name: str, extension: str):
        filepath = os.path.join(os.getcwd(), folder_name, file_name + extension)
        self.filepath = filepath
        if self.check_exists(filepath):
            print("Loading data...")
            try:
                with open(self.filepath, 'r') as persistent_file:
                    existing_data = json.load(persistent_file)
                    print("Loaded data")
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"The file not found {filepath}")
            existing_data, max_id = self.convert_to_int(existing_data)
            return existing_data, max_id
        else:
            raise FileNotFoundError(f"The file path {filepath} not found")
        

    def convert_to_int(self, data: dict):
        new_data = {}
        max_id = None
        for key, value in data.items():
            int_key = int(key)
            new_data[int_key] = value
            if max_id is None or max_id < int_key:
                max_id = int_key
        return new_data, max_id
    
    #Not in use as of now
    def add_single_data(self, 
                           folder_name: str,
                           filename: str,
                           extension: str,
                           id: int,
                           data: dict,
                           encoding= None
                           ):
        """
        Updates a JSON file with new data.

        Args:
            filepath (str): Path to the JSON file.
            new_data (dict): New data to add or update in the file.

        Raises:
            OSError: Error opening or writing to the file.
            json.JSONDecodeError: Error decoding existing JSON data.
        """
        if not encoding:
            encoding = self.settings.encoding
        curr_data = {id: data}
        filepath = os.path.join(os.getcwd(), folder_name, filename + extension)
        self.filepath = filepath
        print(self.filepath)
        if not self.check_exists(self.filepath):
            # Create the folder if it doesn't exist
            #os.makedirs(self.filepath, mode=self.file_permissions, exist_ok=True)  # exist_ok=True prevents errors if folder exists
            print(f"The given file path:  {filepath} does not exist")
        else:
            print("File already exists")
        try:
            # Open the file in read mode
            # Handle cases where the file is missing or corrupt
            #os.chmod(self.filepath, self.file_permissions)
            # print(f"Permission to the file {filepath} is granted")
            with open(self.filepath, 'r') as persistent_file:
                # Load existing data as a dictionary
                existing_data = json.load(persistent_file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}
        existing_data.update(curr_data)
        print(existing_data)
        # if not existing_data:
        #     merged_data = data
        # else:
        #     # Update existing data with new data using dictionary merging
        #     merged_data = {**existing_data, **data}
        # print(merged_data)
        # Open the file again in write mode (truncates existing content)
        with open(self.filepath, 'w') as persistent_file:
            json.dump(existing_data, persistent_file, indent=self.indent)