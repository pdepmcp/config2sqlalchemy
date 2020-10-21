#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
#from sqlalchemy import engine_from_config
#from sqlalchemy.orm import sessionmaker

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,
    ForeignKey,
)


import transaction
import zope.sqlalchemy

import json
import logging
l = logging.getLogger(__name__)

import sys
PY2 = sys.version_info[0] == 2
if not PY2:
    unicode = str


from importlib import import_module



from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData




# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = None # declarative_base(metadata=metadata)




def createClass(name,baseclass=object):
  class Foo(baseclass):
    pass

  Foo.__name__ = name
  Foo.__qualname__ = name
  Foo.__tablename__ = name
  return Foo

def createMultiInheritClass(name = "Foo",baseclasses = (),props = {} ):
  newclass= type(name,baseclasses,props)
  return newclass

def createMethod(mylambda):
  def method(self,*args):
    print (self.__class__.__name__,args)
    return mylambda(*args)

  return method


def CreateColumnDefinitions(element):
  attrs = {}
  for c in element["cols"]:
    args = []
    pk = False
    nullable = True
    coltype = None
    fieldlen = 512
    if len(c)>=3:
      pk = "pk" in c[2]
      nullable = not(pk or "notnull" in c[2])
      if 'fieldlen' in c[2]:
        fieldlen = int(c[2]['fieldlen'])
    if len(c)==4:
      if "fk" in c[3]:
        args.append(ForeignKey(".".join(c[3]["fk"] ) )  )
      pass

    if c[1]=="integer":
      coltype = Integer
    elif c[1] == "string":
      coltype = Unicode(fieldlen)
    else:
      raise Exception ("unknown col type: {} (col:{})".format(c[1],c))
    
    l.debug( element["name"],c[0],coltype,pk )
    attrs[c[0]] = Column(coltype, *args, primary_key = pk,nullable = nullable)
  return attrs

def createModelFromJson(fn,targetmodule):
  with (open(fn,'r')) as fd:
    jsonmodel = json.load(fd)
  targetmodule = import_module(targetmodule)
  for e in jsonmodel.get("entities",[]):
    attrs = {
    '__tablename__':e["name"]
    }
    args = []
    attrs.update(CreateColumnDefinitions(e))
    generatedClass = createMultiInheritClass(e["name"],(Base,),attrs)

    #globals()[generatedClass.__name__] = generatedClass
    #targetmodule[generatedClass.__name__] = generatedClass
    setattr(targetmodule,generatedClass.__name__, generatedClass)
    l.info("{} added to module {}".format(generatedClass.__name__,targetmodule) )
    del generatedClass
  for e in jsonmodel.get("extensions",[]):
    baseclasspath= e["name"].split(".")
    classmodule = import_module(".".join(baseclasspath[:-1] ))
    baseclass = getattr(classmodule,baseclasspath[-1])
    cols = CreateColumnDefinitions(e)
    for colname,col in cols.items():
      setattr(baseclass,colname,col)
    l.info("modified class {} in {}".format(baseclass.__name__,classmodule) )
  pass


def getBase(settings):
  global Base
  base = settings.get("config2sqlalchemy.basemodule",None)
  if base is not None:
    basemodule = import_module(base)
    Base = basemodule.Base
  else:
    Base = declarative_base(metadata=metadata)


configured = False
def includeme(config):

    global configured
    if configured:
        return
    configured = True
    settings = config.get_settings()
    getBase(settings)
    myfile = settings.get("config2sqlalchemy.json")
    targetmodule = settings.get("config2sqlalchemy.target","")
    if targetmodule:
      createModelFromJson(myfile,targetmodule)
