from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Items, Users, Base, Recent
from datetime import datetime

engine = create_engine('sqlite:///catalogdb.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

users = Users(name="Sina Serati", email="wintersina@gmail.com")
session.add(users)
session.commit()

users2 = Users(name="fake name", email="fakeemaila@gmail.com")
session.add(users)
session.commit()

cat1 = Categories(name="Soccer")

session.add(cat1)
session.commit()

item1 = Items(title="Shoes", description="Football boots, called cleats or soccer shoes in North America, are an item of footwear worn when playing football. Those designed for grass pitches have studs on the outsole to aid grip.",
              user=users, category=cat1)

session.add(item1)
session.commit()

recent1 = Recent(created_date=datetime.now(),item=item1)

session.add(recent1)
session.commit()

item2 = Items(title="Gloves", description="While only one player on the field is wearing them, goalkeeper gloves are an essential part of every soccer team's defense. Goalkeeper gloves provide a better grip on the ball, protect and cushion your fingers and palms, and help you block, catch and punch the ball.",
              user=users, category=cat1)

session.add(item2)
session.commit()


recent1 = Recent(created_date=datetime.now(),item=item2)

session.add(recent1)
session.commit()

item3 = Items(title="Yellow Card", description="Every good soccer play should earn one, at least once a game.",
              user=users2, category=cat1)

session.add(item3)
session.commit()


recent1 = Recent(created_date=datetime.now(),item=item3)

session.add(recent1)
session.commit()

#--------------------
cat2 = Categories(name="Basketball")

session.add(cat2)
session.commit()

item1 = Items(title="Shoes", description="The insert is a feature that appears on some basketball shoe models. It is a detachable insole designed to provide arch support.",
              user=users, category=cat2)

session.add(item1)
session.commit()

recent1 = Recent(created_date=datetime.now(),item=item1)

session.add(recent1)
session.commit()

item2 = Items(title="ball", description="hard, round and orange.",
              user=users, category=cat2)

session.add(item2)
session.commit()


recent1 = Recent(created_date=datetime.now(),item=item2)

session.add(recent1)
session.commit()

#------------------------
cat3 = Categories(name="Hockey")

session.add(cat3)
session.commit()

item1 = Items(title="puck", description="hard, round and flat at the same time. Small too.",
              user=users, category=cat3)

session.add(item1)
session.commit()

recent1 = Recent(created_date=datetime.now(),item=item1)

session.add(recent1)
session.commit()

#------------------------
cat4 = Categories(name="Skating")

session.add(cat4)
session.commit()

item1 = Items(title="trucks", description="used for turning, you want time modiretly tight, depending on your driving condition",
              user=users, category=cat4)

session.add(item1)
session.commit()

recent1 = Recent(created_date=datetime.now(),item=item1)

session.add(recent1)
session.commit()

item2 = Items(title="grip tape", description="Grip tape is the gritty, sand papery layer that's applied to the top of a skateboard deck so that your shoes can grip the board. Skaters often cut patterns into their grip tape before applying it.",
              user=users, category=cat4)

session.add(item2)
session.commit()

recent1 = Recent(created_date=datetime.now(),item=item2)

session.add(recent1)
session.commit()
