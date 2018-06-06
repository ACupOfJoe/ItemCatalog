








Base = declarative_base() 


class User(Base): 
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Coumn(String(250), nullable=False) 
	email = Column(String(250), nullable=False) 
	picture = Column(String(250))

"""This Industries class holds the information for all of the different industries each stock is included in """ 

class Industries(Base):
	__tablename__ = 'stockindustrycatalog'

	id = Column(Integer, primary_key=True)
	name = Column(String(40), nullable="False")
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	"""Return object data in easily serializeable format"""
	def serialize(self)
	
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
	catalog_id = Column(Integer, ForeignKey('stockindustrycatalog.id'))

	@property
	"""Return obejct data in an easily serializable format"""
	def serialize(self)
	return { 
		'ticker': self.ticker
		'id': self.id
		'close_price': self.close_price

	}




