import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'faq_users'
    uid = sa.Column('uid', sa.BigInteger, primary_key=True)
    is_bot = sa.Column('is_bot', sa.Boolean)
    username = sa.Column('username', sa.Text)
    first_name = sa.Column('first_name', sa.Text)
    last_name = sa.Column('last_name', sa.Text)
    lang = sa.Column('lang', sa.Text)
    status = sa.Column('status', sa.Text)
    state = sa.Column('state', sa.Text)

    def __init__(self, message):
        self.uid = int(message.from_user.id)
        self.is_bot = message.from_user.is_bot
        self.username = message.from_user.username
        self.first_name = message.from_user.first_name
        self.last_name = message.from_user.last_name
        self.lang = 'English'
        self.status = 'User'
        self.state = 'START'

    def __repr__(self):
        return f"{self.uid} : {self.status} : {self.state} : {self.lang}"
