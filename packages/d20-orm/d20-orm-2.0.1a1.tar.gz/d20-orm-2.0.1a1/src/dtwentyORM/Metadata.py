# File: ArangoDB Datafield based Metadata
# Author: alexsanchezvega
# Company: d20
# Version: 1.0

from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from .BasicElement import BasicElement
from .GraphClassFactory import ClassFactory
import json
import os

def md_dbname():
    return f'{os.environ.get("DBPREFIX", "")}metadata'

class Metadata():

    def __init__(self, conf={}):
        graphname = ''
        collections = ['DataFields', 'Parameters', 'Labels', 'Log', 'Countries', 'LocationHistoryCatalogue', 'Zipcodes']
        edgeDefinitions={}
        db_name = md_dbname()
        factory = ClassFactory(graphname, db_name, collections = collections, edgeDefinitions=edgeDefinitions, conf=conf)

        print(factory, " - OK")


    class DataField(BasicElement):                    
        # Rethink
        @classmethod
        def get_col_dict(cls):
            if os.environ.get('COL_DICT', None) != None:
                col_dict = json.loads(os.environ.get('COL_DICT'))
            else:
                print("No configuration given, cannot start.")
                raise Exception
            return col_dict

        @classmethod
        def coll_to_class(cls, coll):
            col_dict = cls.get_col_dict()
            return col_dict.get(coll, coll)

        @classmethod
        def class_to_coll(cls, cl):
            col_dict = cls.get_col_dict()
            res = cl
            for e in col_dict.items():
                if e[1] == cl:
                    res = str(e[0])
                    break
            return res
                
        def make(self):
            if self.obj_type == None: 
                self.obj_type = self.__class__.__name__.lower()
            self.active = True
            self.deleted = False
            self.attributes = ['obj_type', 'active', 'deleted']
            self.get_all()
            self.attributes = [f.get('name') for f in self.found]
            self.scopes = {}
            for f in self.found:
                if not f.get('scope') in self.get('scopes'):
                    self.scopes[f.get('scope')] = []
                self.scopes[f.get('scope')].append(f.get('name'))
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None, obj_type=None):
            self.collection = 'DataFields'
            self.obj_type = obj_type
            super().__init__(db_name = md_dbname(), data=data)
            
        @property
        def obj_type(self):
            return self._obj_type

        @obj_type.setter
        def obj_type(self, value):
            self._obj_type = value
            

    class Parameter(BasicElement):
        def make(self):
            self.attributes = ['_key', 'name', 'desc', 'code', 'value', 'created', 'updated', 'active', 'deleted']
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None):
            self.collection = 'Parameters'
            super().__init__(db_name = md_dbname(), data=data)

    class Label(BasicElement):
        def make(self):
            self.attributes = ['_key', 'name', 'lang', 'code', 'value', 'created', 'updated', 'active', 'deleted']
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None):
            self.collection = 'Labels'
            super().__init__(db_name = md_dbname(), data=data)


    class LogEntry(BasicElement):

        def make(self):
            self.attributes = ['_key', 'action', 'user', 'api_user', 'datetime', 'token', 'api_token', 'source', 'user_agent', 'user_location', 'user_ip', 'host_ip']
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None):
            self.collection = 'Log'
            super().__init__(db_name = md_dbname(), data=data)


    class LocationLog(BasicElement):

        def make(self):
            self.attributes = ['_key', 'type', 'location', 'date']
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None):
            self.collection = 'LocationHistoryCatalogue'
            super().__init__(db_name = md_dbname(), data=data)


    class Countries_col(BasicElement):
        def make(self):
            self.attributes = ['_key', 'name', 'translations', 'alpha3Code']
            for key in self.attributes:
                setattr(self, key, None)

        def __init__(self, data=None):
            self.collection = 'Countries'
            super().__init__(db_name = md_dbname(), data=data)


    class cp_col(BasicElement):

        def make(self):
            self.attributes = ['_key', 'IdEnt', 'Entidad', 'Ciudad', 'Municipio', 'Colonia', 'CP']
            for key in self.attributes:
                setattr(self, key, None)

        def get_by_cp(self, cp):
            self.CP = cp
            self.get_all()

        def __init__(self, data=None):
            self.collection = 'Zipcodes'
            super().__init__(db_name = md_dbname(), data=data)
