from typing import List, Type

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


# Define a Pydantic model for the post data
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)

    def __init__(self, id_: int, title: str, description: str, **kw):
        super().__init__(**kw)
        self.id = id_
        self.title = title
        self.description = description


# decorator for safe database operations
def safe_execute(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}"
    return wrapper


class DatabaseManager:
    def __init__(self):
        # Set up the engine and metadata
        self.engine = create_engine("sqlite:///notes.db", echo=True, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @safe_execute
    def inser_post(self, post_data: Post):
        # Insert data into the database using ORM session
        session = self.Session()
        try:
            session.add(post_data)
            session.commit()
        finally:
            session.close()

    @safe_execute
    def get_posts(self) -> list[Type[Post]]:
        # Retrieve a post by its ID using ORM session
        session = self.Session()
        try:
            posts = session.query(Post).all()
            return posts
        finally:
            session.close()

    @safe_execute
    def delete_post(self, post_id: int):
        # Delete a post by its ID using ORM session
        session = self.Session()
        try:
            post = session.query(Post).get(post_id)
            session.delete(post)
            session.commit()
        finally:
            session.close()
        return f"Deleted row with ID: {post_id}"

    @safe_execute
    def update_post(self, data: Base):
        # Update a post by its ID using ORM session
        session = self.Session()
        try:
            if table := session.get(Post, data.id):
                table.title = data.title if data.title else ''
                table.description = data.description if data.description else ''
                session.commit()
        finally:
            session.close()
