import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    g_id = Column(String(250), nullable=False)
    email = Column(String(50), nullable=False)
    given_name = Column(String(30), nullable=False)
    family_name = Column(String(30), nullable=False)
    picture = Column(String(500), nullable=False)


class Word(Base):
    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    word = Column(String(80), nullable=False)
    partOfSpeech = Column(String(9), nullable=False)
    inSentenceSpanish = Column(String(300), nullable=False)
    inSentenceEnglish = Column(String(300), nullable=False)

    # classmethod functions for class Word
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word': self.word,
            'partOfSpeech': self.partOfSpeech,
            'inSentenceSpanish': self.inSentenceSpanish,
            'inSentenceEnglish': self.inSentenceEnglish,
        }


engine = create_engine('sqlite:///linuxapp1.db')


Base.metadata.create_all(engine)
