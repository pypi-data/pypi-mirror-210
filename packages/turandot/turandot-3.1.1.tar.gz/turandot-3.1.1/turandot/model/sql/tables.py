from sqlalchemy import Column, Integer, String, Boolean, Text

from turandot.model.sql import Base


class DbCsl(Base):
    """Save path of CSL files to database"""
    __tablename__ = "csl"
    dbid = Column(Integer, primary_key=True)
    path = Column(String(320))


class DbFileSelectPersistence(Base):
    """Save recently used path of file select dialogs to database"""
    __tablename__ = "file_select_persistence"
    input_id = Column(String(70), primary_key=True)
    last_path = Column(String(320))


class DbTemplate(Base):
    """Save path & allowed templating engines of templates to the database"""
    __tablename__ = "templates"
    dbid = Column(Integer, primary_key=True)
    path = Column(Text)
    allow_jinja = Column(Boolean, default=False)
    allow_mako = Column(Boolean, default=False)
