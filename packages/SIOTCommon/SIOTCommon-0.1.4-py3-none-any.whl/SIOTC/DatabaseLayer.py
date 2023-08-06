from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, scoped_session
import os

dir_path = '/home/ubuntu/config/'
filename = 'db_config.txt'
file_path = os.path.join(dir_path, filename)

with open(file_path, 'r') as f:
    # Write the connection string to the file
    first_line = f.readline()

global_session = None

def GetSession():
    global global_session

    # Check if a session already exists
    if global_session is not None:
        return global_session

    # Create a new session if it doesn't exist
    Base = automap_base()
    engine = create_engine('postgresql://postgres:3485780@localhost:5432/sweiotdb', echo=True)
    Base.prepare(engine, reflect=True, schema='public')
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)

    # Store the session in the global variable
    global_session = session

    return session, Base

def GetModel(table_name):
    session, Base = GetSession()
    table_model = getattr(Base.classes, table_name, None)
    if table_model is None:
        raise ValueError(f"Table model not found for table name: {table_name}")
    return table_model

def GetModel(table_name, session, Base):
    table_model = getattr(Base.classes, table_name, None)
    if table_model is None:
        raise ValueError(f"Table model not found for table name: {table_name}")
    return table_model

# map models, unessecary
def Users(Base):
    Users = Base.classes.users
    return Users

def GetKeys(Base):
    Keys = Base.classes.rsakeys
    return Keys

def Roles(Base):
    Roles = Base.classes.role
    return Roles

def Producers(Base):
   Producers = Base.classes.producers
   return Producers

def Orders(Base):
   Orders = Base.classes.orders
   return Orders

def Firmwares(Base):
   Firmwares = Base.classes.firmwares
   return Firmwares

def Devices(Base):
   Devices = Base.classes.devices
   return Devices

def Customers(Base):
   Customers = Base.classes.customers
   return Customers

def Config(Base):
   Configs = Base.classes.config
   return Configs

def Batch(Base):
   Batches = Base.classes.batch
   return Batches

# Create table object from model metadata
def CreateTableObject(name, metadata):
   return Table(name, metadata, autoload=True)

   
