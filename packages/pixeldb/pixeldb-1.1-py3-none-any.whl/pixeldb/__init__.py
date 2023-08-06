# PxlDB v1.1 (By PxlmastrXD)
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

  def set(self, key, value):
    self.database[key] = value

  def get(self, key):
    return (self.database[key])
