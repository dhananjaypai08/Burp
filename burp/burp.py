from persist import DataPersister, DataPersistSettings
import os

class Burp:
    """
    Main class for the burp database
    1 folder = 1 database
    1 file = 1 table
    """
    
    def __init__(self):
        self.settings = DataPersistSettings()
        self.COMMON_ENCODINGS = ["utf-8", "utf-16", "latin-1", "ascii"]
        self.db_name = None
        self.db_instance = None
        self.filepath = None
        self.tables = {}
        self.auto_inc_id = 0
        self.auto_inc_status = False
        self.starter_file = "base"
        self.table_name = None
    
    
    def create_database(self, db_name: str, encoding=None, save="auto"):
        """

        Args:
            db_name (str): name of the database
            encoding (str, optional): encoding options for data persistence. Defaults to None.
            save (str, optional): options for persisting to permanent storage. Defaults to "auto".

        Raises:
            ValueError: Not a command encoding format. 
            ValueError: Database name already exists.
        """
        if encoding:
            if encoding not in self.COMMON_ENCODINGS:
                raise ValueError("Please provide a valid common encoding format")
            self.settings.encoding = encoding
        self.settings.folder = db_name
        self.db_name = db_name
        status = self._create_db_instance()
        if not status:
            raise ConnectionError(f"Something went wrong while trying to create a db instance with name {db_name}")
        return self.db_instance
    
       
    def _create_db_instance(self):
        try:
            self.db_instance = DataPersister(self.settings)
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__} - {e}")
            return False
        return True

    
    def _create_table_file_and_save(self):
        """create a new table

        Returns:
            str: file path
        """
        filepath = self.db_instance.create_table_file(self.table_name, self.db_name)
        self.filepath = filepath
        return self.filepath
    
    
    def create_table(self, table_name: str, auto_increment=True):
        """ Create a new table 

        Args:
            table_name (str): table name 
            schema (dict): structure of the input data 
            auto_increment (bool, optional): Auto increment the unique ID. Defaults to True.

        Raises:
            ValueError: _description_
            TypeError: _description_
        """
        
        if self.tables.get(table_name)  is not None:
            raise ValueError(f"A table with name {table_name} already exists")
        self.tables[table_name] = {}
        if auto_increment:
            self.auto_inc_status = True

        filepath = os.path.join(self.settings.folder + table_name + self.settings.extension)
        if self.db_instance.check_exists(filepath):
            raise ValueError(f"The database with name {table_name} already exists")
        self.table_name = table_name
        try:
            self._create_table_file_and_save()
            print(f"The new database with name {table_name} has been created")
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__} - {e}")
    
    
    def add(self, table_name: str, data: dict):
        """Add Data to the table

        Args:
            table_name (str): name of the table to add the data to
            data (dict): data to be added

        Raises:
            ValueError: A table with that name already exists
            KeyError: The given structure does not match the predefined structure 
        """
        if self.tables.get(table_name) is  None:
            raise ValueError(f"A table with name {table_name} does not exists")
        # if list(data.keys()) != list(self.tables[table_name].keys()):
        #     raise KeyError(f"The schema of the given data does not match with the predefined schema")
        self.tables[table_name][self.auto_inc_id] = data
        self._auto_increment_id()
        self._append_data_to_db(table_name)
    
    
    def _auto_increment_id(self):
        if self.auto_inc_status:
            self.auto_inc_id += 1
    
    
    def _append_data_to_db(self, table_name: str):
        if self.tables.get(table_name) is None:
            raise KeyError(f"The table name: {table_name} does not exist")
        self.db_instance.add_data(self.db_name, table_name, self.settings.extension, self.auto_inc_id-1, self.tables[table_name][self.auto_inc_id-1], self.settings.encoding)
            

        
        