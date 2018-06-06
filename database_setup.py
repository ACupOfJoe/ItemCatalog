








Base = declarative_base() 


class User(Base): 
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Coumn(String(250), nullable=False) 
	email = Column(String(250), nullable=False) 
	picture = Column(String(250))

class StockCatalog(Base): 
	__tablename__ = 'restaurant'