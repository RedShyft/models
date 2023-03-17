import os
import datetime
import jwt

from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


JWT_SECRET = '0839942409BCFFF12C92AF8C66BF5BD06086F423C361D7C36BA8CB2CFBFCD8EF'


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    def update(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


Base = declarative_base(cls=Base)


class Account(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    active = Column(Boolean, default=True)
    plan = Column(String, default='basic')
    stripe_customer_id = Column(String)
    stripe_sub_id = Column(String)
    stripe_sub_status = Column(String)
    stripe_product_id = Column(String)

    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)

    def safe_data(self):
        return {
            'id': self.id,
            'email': self.email,
            'active': self.active,
            'plan': self.plan,
            'created_at': self.created_at,
            'reddit_accounts': self.reddit_users
        }

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @staticmethod
    def generate_jwt(id):
        return jwt.encode({"account_id": id}, JWT_SECRET, 'HS256')

    @staticmethod
    def decode_jwt(token):
        return jwt.decode(token, key=JWT_SECRET, algorithms=['HS256'], options={"verify_exp": False})


class RedditUser(Base):
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    active = Column(Boolean, default=True)
    eligible = Column(Boolean)
    suspended = Column(Boolean)
    email_verified = Column(Boolean)
    karma = Column(Integer)
    
    user_agent = Column(String)
    username = Column(String)
    refresh_token = Column(String)

    account = relationship("Account", backref="reddit_users", lazy=True)
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)


campaign_subreddit_association = Table(
    "campaign_subreddit_association",
    Base.metadata,
    Column("campaign_id", ForeignKey("campaign.id")),
    Column("subreddit_id", ForeignKey("subreddit.id"))
)


class Campaign(Base):
    id = Column(Integer, primary_key=True)
    reddit_user_id = Column(Integer, ForeignKey("reddituser.id"))
    subject = Column(String(225), nullable=False)
    message = Column(String(1000), nullable=False)
    active = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    query = Column(String, nullable=False)

    reddit_user = relationship(
        "RedditUser", backref="campaigns", lazy='joined')
    subreddits = relationship(
        "Subreddit", secondary=campaign_subreddit_association, lazy='joined')
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)


class Subreddit(Base):
    id = Column(String, primary_key=True)  # ID from reddit
    name = Column(String, nullable=False)
    display_name = Column(String)


class Message(Base):
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaign.id"))
    subreddit_id = Column(String, ForeignKey("subreddit.id"))
    redditor_id = Column(String, index=True)
    redditor_name = Column(String)
    resource_uri = Column(String(500))
    title = Column(String)

    campaign = relationship("Campaign", backref="messages")
    subreddit = relationship("Subreddit", backref="messages", lazy=True)

    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
