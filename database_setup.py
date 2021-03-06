from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """
    Registered user information is stored in db.
    """
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)


class Industry(Base):
    """
    Industry information is stored in db
    """

    __tablename__ = 'Industry'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable="False")
    user_id = Column(String, ForeignKey('User.name'))
    user = relationship(User, cascade="all, delete-orphan", single_parent=True)

# Return object data in easily serializeable format"""
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class Stock(Base):
    """This Stock class holds all of the stock tickers
    and their closing price"""
    __tablename__ = 'Stock'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable='False')
    close_price = Column(String(10), nullable='False')
    industry_id = Column(Integer, ForeignKey('Industry.id'))
    user_id = Column(String, ForeignKey('User.name'))



# Return obejct data in an easily serializable format
    @property
    def serialize(self):
        return {
            'ticker': self.ticker,
            'id': self.id,
            'close_price': self.close_price,
            'industry_id': self.industry_id,
            'user_id': self.user_id
            }




engine = create_engine('sqlite:///stocksbyindustrywithusers.db')
Base.metadata.create_all(engine)