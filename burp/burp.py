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
        self.table_name = ""
    
    
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
        if self.db_instance.check_exists(os.path.join(os.getcwd(), self.db_name)):
            # print(f"The database with name {table_name} already exists")
            print(f"The database with name {db_name} already exists")
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
    
    def _table_name_id_exists(self, id:int):
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
        if self.tables[self.table_name].get(id) is None:
            raise KeyError(f"The id {id} does not exist in the table")
        return True
    
    
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
            print(f"A table with name {table_name} already exists")
        self.tables[table_name] = {}
        if auto_increment:
            self.auto_inc_status = True

        filepath = os.path.join(self.settings.folder + table_name + self.settings.extension)
        if self.db_instance.check_exists(filepath):
            # print(f"The database with name {table_name} already exists")
            return f"The table with name {table_name} already exists"
        self.table_name = table_name
        try:
            self._create_table_file_and_save()
            print(f"The new database with name {table_name} has been created")
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__} - {e}")
    
    
    def add_one(self, table_name: str, data: dict):
        """Add Data to the table

        Args:
            table_name (str): name of the table to add the data to
            data (dict): data to be added

        Raises:
            ValueError: A table with that name already exists
            KeyError: The given structure does not match the predefined structure 
        """
        if self.tables.get(table_name) is  None:
            print(f"A table with name {table_name} does not exists")
        # if list(data.keys()) != list(self.tables[table_name].keys()):
        #     raise KeyError(f"The schema of the given data does not match with the predefined schema")
        self.tables[table_name][self.auto_inc_id] = data
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
        print(self.tables)
        return f"Deleted the id {id} successfully"
    
    
    def update(self, id: int, data: dict):
        """ Update the data 

        Args:
            id (int): ID of the object to update
            data (dict): data which is to be updated 
        """
        if not self._table_name_id_exists(id):
            print("ID or table not found")
        for key, value in data.items():
            self.tables[self.table_name][id][key] = value
        return self.tables[self.table_name][id]
    
    
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
            print("Table name does not exist")
        if self.tables.get(self.table_name) is None:
            print("Table name not found")
        status = self.db_instance.save_data(self.tables[self.table_name], self.table_name, self.db_name, self.settings.extension)
        if status:
            return "Data saved successfull"
        
        
    def _auto_increment_id(self):
        if self.auto_inc_status:
            self.auto_inc_id += 1
    
    
    # This is will not work for now
    def _append_data_to_db(self, table_name: str):
        if self.tables.get(table_name) is None:
            raise KeyError(f"The table name: {table_name} does not exist")
        self.db_instance.add_single_data(self.db_name, table_name, self.settings.extension, self.auto_inc_id-1, self.tables[table_name][self.auto_inc_id-1], self.settings.encoding)
        
            

        
        