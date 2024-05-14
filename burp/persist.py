import os 
import json 
import pickle

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
    
    
    def add_data(self, 
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