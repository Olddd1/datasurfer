from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, JSON, Boolean
import datetime

class Users:
    def __init__(self):
        self.meta = MetaData()

        self.users = Table('users', self.meta,
                           Column('user_id', Integer, unique=True),
                           Column('subscribe', Boolean),
                           Column('until', String),
                           Column('last_art', Integer))

        self.stocks = Table('stocks', self.meta,
                            Column('art', Integer),
                            Column('data', JSON))

        self.engine = create_engine("sqlite:///db.db")
        self.meta.create_all(self.engine)

        self.conn = self.engine.connect()

    def create_user(self, user_id):
        self.conn.execute(self.users.insert().values(user_id=user_id, subscribe=0, until=str(datetime.date.today()), last_art=0))

    def get_user(self, user_id):
        return self.conn.execute(self.users.select().where(self.users.c.user_id == user_id))

    def get_users(self):
        return self.conn.execute(self.users.select().where(True))

    def subscribe_update(self, status, date, user_id):
        self.conn.execute(self.users.update().values(subscribe=status, until=date).where(self.users.c.user_id == user_id))

    def last_atr_update(self, user_id, art):
        self.conn.execute(self.users.update().values(last_art=art).where(self.users.c.user_id == user_id))

    def add_art_to_stocks(self, art, data):
        self.conn.execute(self.stocks.insert().values(art=art, data=data))

    def get_stocks(self, art):
        return self.conn.execute(self.stocks.select().where(self.stocks.c.art == art))

    def update_stocks(self, art, data):
        self.conn.execute(self.stocks.update().values(data=data).where(self.stocks.c.art == art))

    def clear_users(self):
        self.conn.execute(self.users.delete().where(True))

    def clear_stocks(self):
        self.conn.execute(self.stocks.delete().where(True))