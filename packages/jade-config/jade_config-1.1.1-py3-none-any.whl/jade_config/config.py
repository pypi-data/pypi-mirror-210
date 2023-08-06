import shelve
import datetime

class UnableToSetValue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UnableToGetValue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UnableToRemoveKey(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Config:
    '''
    -- Jade Config --\n
    file = config.Config(name, log=False)\n
        Setting log to True enables logging. Setting it to False or ommiting the argument disables logging.\n
        Logging is not reccomended in production due to security vulnerabilities.\n
    Functions:\n
        - setValue(key, value)\n
    '''
    def __init__(self, name, log=False) -> None:
        self.name = name
        self.log = log
        
        db = shelve.open(self.name)
        db.close()

        if log == True:
            self.logAndPrint(f"Logging is True. Log is '{name}.log.txt'")
        self.logAndPrint("Initiated.")
    
    def logAndPrint(self, text):
        now = datetime.datetime.now()
        if self.log == True:
            logFile = open(f"{self.name}.log.txt", "a")
            logFile.write(f"[{self.name}] [{now.month}/{now.day}/{now.year}] [{now.hour}:{now.minute}:{now.second}] {text}\n")
            logFile.close()

        print(f"[{self.name}] {text}")
        

    def setValue(self, key, value):
        '''Sets the value of the file'''
        try:
            db = shelve.open(self.name)
            db[key] = value
            db.close()
            self.logAndPrint(f"Set key '{key}' to value '{value}'")
            return True

        except:
            self.logAndPrint(f"Unable to set value '{value}' to key '{key}'")
            raise UnableToSetValue(f"Unable to set value '{value}' to key '{key}'")

    def getValue(self, key):
        '''Gets the value of a key in the file.'''
        try:
            db = shelve.open(self.name)
            value = db[key]
            db.close()
            self.logAndPrint(f"Got value '{value}' from key '{key}'")
            return value

        except:
            self.logAndPrint(f"Unable to get the value '{value}' from key '{key}'")
            raise UnableToGetValue(f"Unable to get the value '{value}' from key '{key}'")
        
    def removeKey(self, key):
        '''Removes a key from the file'''
        try:
            db = shelve.open(self.name)
            del db[key]
            db.close()
            self.logAndPrint(f"Removed key '{key}'")

        except:
            self.logAndPrint(f"Unable to remove key '{key}'")
            raise UnableToRemoveKey(f"Unable to remove key '{key}'")