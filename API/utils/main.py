from .persist import DataPersister, DataPersistSettings
import os
from .generator import generate_key, create_fernet_instance

class Burp:
    """
    Main class for the burp database
    """
    def __init__(self, **kwargs):
        self.settings = DataPersistSettings()
        self.COMMON_ENCODINGS = ["utf-8", "utf-16", "latin-1", "ascii"]
        self.db_name = None
        self.db_instance = None
        self.filepath = None
        self.tables = {}
        self.auto_inc_id = 0
        self.auto_inc_status = False
        self.starter_file = "base"
        self.table_name = ""
        self.cur_dir = os.path.join(os.getcwd(), "utils")
        self.encryption_key = None
        self.encrypt = False
        self.fernet_instance = None
        for key, value in kwargs.items():
            if isinstance(key, str):
                raise TypeError(f"Attribute names must be strings, got {key}")
            setattr(self, key, value)
    
    
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
        setattr(self, "db_name", db_name)
        status = self._create_db_instance()
        if not status:
            raise ConnectionError(f"Something went wrong while trying to create a db instance with name {db_name}")
        if self.db_instance.check_exists(os.path.join(self.cur_dir, self.db_name)):
            # print(f"The database with name {table_name} already exists")
            raise KeyError(f"The database with name {db_name} already exists")
        return self.db_instance
    
       
    def _create_db_instance(self):
        """ Creates a new db instance """
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
        filepath = self.db_instance.create_table_file(self.table_name, self.db_name, self.cur_dir)
        setattr(self, "filepath", filepath)
        return self.filepath
    
    
    def _table_name_id_exists(self, uid:int):
        """ Check if the table with self.table name exists
        and whether it contains id object in it

        Args:
            id (int): ID of the user

        Raises:
            KeyError: No table name existing
            KeyError: The id not found in the table
        """
        if self.table_name == "":
            raise KeyError(f"There is not table to search from")
        if self.tables[self.table_name].get(uid) is None:
            raise KeyError(f"The id {uid} does not exist in the table")
        return True
    
    
    def create_table(self, table_name: str, extension: str = None, auto_increment=True, encrypt=False):
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
            raise KeyError(f"A table with name {table_name} already exists")
        self.tables[table_name] = {}
        if auto_increment:
            self.auto_inc_status = True
        if encrypt:
            setattr(self, "encryption_key", generate_key())
            setattr(self, "fernet_instance", create_fernet_instance(self.encryption_key))
            self.encrypt = True
        
        filepath = os.path.join(self.cur_dir, table_name + self.settings.extension)
        if self.db_instance.check_exists(filepath):
            # print(f"The database with name {table_name} already exists")
            return f"The table with name {table_name} already exists"
        if extension:
            self.settings.extension = extension
        setattr(self, "table_name", table_name)
        try:
            self._create_table_file_and_save()
            print(f"The new database table with name {table_name} has been created")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {type(e).__name__} - {e}")
    
    
    def add_one(self, data: dict):
        """Add Data to the table

        Args:
            table_name (str): name of the table to add the data to
            data (dict): data to be added

        Raises:
            ValueError: A table with that name already exists
            KeyError: The given structure does not match the predefined structure 
        """
        if self.table_name is  None:
            raise KeyError(f"A table with name {self.table_name} does not exists")
        # if list(data.keys()) != list(self.tables[table_name].keys()):
        #     raise KeyError(f"The schema of the given data does not match with the predefined schema")
        self.tables[self.table_name][self.auto_inc_id] = data
        self._auto_increment_id()
        #self._append_data_to_db(table_name)
        return self.auto_inc_id-1
    
        
    def delete(self, id: int):
        """ Delete a value from the table 

        Args:
            id (int): id of the doc
        """
        if not self._table_name_id_exists(id):
            print("ID or table not found")
        del self.tables[self.table_name][id]
        # print(self.tables)
        return f"Deleted the id {id} successfully"
    
    
    def update(self, id: int, data: dict):
        """ Update the data 

        Args:
            id (int): ID of the object to update
            data (dict): data which is to be updated 
        """
        if not self._table_name_id_exists(id):
            return "ID or table not found"
        for key, value in data.items():
            self.tables[self.table_name][id][key] = value
        return self.tables[self.table_name][id]
    
    def delete_table(self):
        """ Delete the table

        Returns:
            str: status of the operation
        """
        if self.table_name  is None:
            raise KeyError(f"A table with name {self.table_name} already exists")
        self.db_instance.delete_file(self.table_name, self.db_name, self.settings.extension)
        del self.tables[self.table_name]
        deleted_table = self.table_name
        setattr(self, "table_name", None)
        setattr(self, "auto_inc_status", False)
        setattr(self, "auto_inc_id", 0)
        self.fernet_instance = None
        self.encryption_key = None
        self.encrypt = False
        return f"Table with name: {deleted_table} has been deleted"
    
    
    def get_one(self, id: int):
        """ Get one object from the table

        Args:
            id (int): ID of the object
        Returns:
            dict: object of the data
        """
        self._table_name_id_exists(id)
        return self.tables[self.table_name][id]
    
    
    def get_all(self):
        """ Get all the data in memory
        Returns:
            List[dict] : list of all the objects
        """
        if self.tables.get(self.table_name) is None or self.table_name == "":
            return "Table name does not exists"
        return self.tables[self.table_name]
    
    def save_snapshot(self):
        """ Save a snapshot of the in memory data to a file with structures as db_name/table_name.[extension]

        Returns:
            str: Message 
        """
        if self.table_name == "":
            return "Table name does not exist"
        if self.tables.get(self.table_name) is None:
            raise KeyError("Table with name : {table_name} not found")
        status = self.db_instance.save_data(self.tables[self.table_name], self.table_name, self.db_name, self.cur_dir,
                                            self.settings.extension,
                                            self.encrypt,
                                            self.fernet_instance)
        if status:
            return "Data saved successfull"
        
        
    def _auto_increment_id(self):
        if self.auto_inc_status:
            self.auto_inc_id += 1
            
    
    def load_data(self, db_name: str, table_name: str, encrypt: bool= False, key: str = ""):
        """ Load a persisting db table in memory

        Args:
            db_name (str): database name
            table_name (str): table name

        Returns:
            str: message
        """
        if self.db_instance is None:
            print("Intitiazling a new instance in memory")
            status = self._create_db_instance()
            if status:
                print("New instance initialized")
            else:
                print("Something went wrong")
        if encrypt:
            setattr(self, "encrypt", encrypt)
            setattr(self, "encryption_key", key)
            setattr(self, "fernet_instance", create_fernet_instance(key))
        existing_data, max_uid = self.db_instance.load_data(db_name, table_name, self.settings.extension, self.cur_dir, self.encrypt, self.fernet_instance)
        self.auto_inc_status = True
        self.auto_inc_id = max_uid + 1
        self.tables[table_name] = existing_data
        setattr(self, "table_name", table_name)
        setattr(self, "db_name", db_name)
        print("Initialized the existing database table")
        return "Loaded the data in memory"
    
    
    # This is will not work for now
    def _append_data_to_db(self, table_name: str):
        if self.tables.get(table_name) is None:
            raise KeyError(f"The table name: {table_name} does not exist")
        self.db_instance.add_single_data(self.db_name, table_name, self.settings.extension, self.auto_inc_id-1, self.tables[table_name][self.auto_inc_id-1], self.settings.encoding)
        
            

        
        