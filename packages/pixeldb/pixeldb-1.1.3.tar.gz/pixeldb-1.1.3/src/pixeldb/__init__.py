# PxlDB v1.1.3 (By PxlmastrXD)
import pickle


def version():
  print('PxlDB v1.1')


def create(dbname):
  with open(dbname, 'wb') as f:
    idb = {}
    pickle.dump(idb, f)
    print('Database created.')


class opendb:

  def __init__(self, database):
    with open(database, 'rb') as f:
      opendatabase = pickle.load(f)
    self.database = opendatabase
    self.openedfile = database

  def set(self, key, value):
    self.database[key] = value
    with open(self.openedfile, 'wb') as f:
      pickle.dump(str(self.database), f)

  def get(self, key):
    return (self.database[key])
