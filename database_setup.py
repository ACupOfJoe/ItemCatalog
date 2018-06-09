from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine









Base = declarative_base() 


class User(Base): 
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False) 
	email = Column(String(250), nullable=False) 
	picture = Column(String(250), nullable=True)

"""This Industries class holds the information for all of the different industries each stock is included in """ 

class Industry(Base):
	__tablename__ = 'industry'

	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable="False")
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

# Return object data in easily serializeable format"""
	@property
	def serialize(self):
		return { 
			'name': self.name,
			'id': self.id
		}

"""This Stock class holds all of the stock tickers and their closing price"""

class Stock(Base): 
	__tablename__ = 'stock'

	id = Column(Integer, primary_key=True)
	ticker = Column(String(10), nullable='False')
	close_price = Column(String(10), nullable='False')
	industry_id = Column(Integer, ForeignKey('industry.id'))

 # Return obejct data in an easily serializable format
	@property
	def serialize(self):
		return { 
			'ticker': self.ticker,
			'id': self.id,
			'close_price': self.close_price
			}


engine = create_engine('sqlite:///stocksbyindustrywithusers.db')


Base.metadata.create_all(engine)