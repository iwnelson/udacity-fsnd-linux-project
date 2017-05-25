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

    # # classmethod functions for class User

    # # looks up user entity by id number
    # @classmethod
    # def by_id(cls, u_id):
    #     return session.query(User).filter_by(id=u_id).one()

    # # looks up user entity by g_id number
    # @classmethod
    # def by_g_id(cls, idinfo):
    #     g_id = idinfo['sub']
    #     return session.query(User).filter_by(id=g_id).one()

    # # creates user entity but DOES NOT store
    # @classmethod
    # def register(cls, idinfo):
    #     return User(g_id=idinfo['sub'], email=idinfo['email'],
    #                 given_name=idinfo['given_name'],
    #                 family_name=idinfo['family_name'],
    #                 picture=idinfo['picture'])


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

    # # looks up word entity by id number
    # @classmethod
    # def by_id(cls, word_id):
    #     return session.query(Word).filter_by(id=word_id).one()

    # # returns word from database
    # @classmethod
    # def by_word(cls, word):
    #     return session.query(Word).filter_by(word=word).one()

    # # creates word entity but DOES NOT store
    # @classmethod
    # def createWord(cls, form, user):
    #     return Word(word=form['word'], partOfSpeech=form['partOfSpeech'],
    #                 definition=form['definition'],
    #                 inSentenceSpanish=form['inSentenceSpanish'],
    #                 inSentenceEnglish=form['inSentenceEnglish'],
    #                 user=user)

    # # edits word entity but DOES NOT store
    # @classmethod
    # def editWord(cls, oldWord, form):
    #     oldWord.word = form['word']
    #     oldWord.partOfSpeech = form['partOfSpeech']
    #     oldWord.definition = form['definition']
    #     oldWord.inSentenceSpanish = form['inSentenceSpanish']
    #     oldWord.inSentenceEnglish = form['inSentenceEnglish']
    #     return oldWord


engine = create_engine('sqlite:///linuxapp1.db')


Base.metadata.create_all(engine)
