import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name
        }

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    description = Column(String(80), nullable=False)
    title = Column(String(80), nullable=False)
    category = relationship(Categories)
    category_id = Column(Integer, ForeignKey('categories.id'))

    @property
    def serialize(self):
        return {
            'id' :self.id,
            'title': self.title,
            'description': self.description,
            'category_id':self.category_id
        }

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)


engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.create_all(engine)

