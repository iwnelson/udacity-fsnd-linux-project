from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash)
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Word
from oauth2client import client, crypt
import json

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///linuxapp1.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

app.secret_key = '0\x1ak\x02\x8a\xc2\xf3\x03\xd1\xf0H\xd0vpBb\xc4\xde\xf5~\xf9\xd3\x9c\xc9'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read()
                       )['web']['client_id']
APPLICATION_NAME = "&#191;Como lo dice?"


# classmethod functions for User DB
# looks up user entity by id number
def by_user_id(u_id):
    return session.query(User).filter_by(id=u_id)


# looks up user entity by g_id number
def by_g_id(idinfo):
    g_id = idinfo['sub']
    return session.query(User).filter_by(id=g_id)


# creates user entity but DOES NOT store
def register(idinfo):
    return User(g_id=idinfo['sub'], email=idinfo['email'],
                given_name=idinfo['given_name'],
                family_name=idinfo['family_name'],
                picture=idinfo['picture'])


# Helper functions for Word DB
# looks up word entity by id number
def by_word_id(word_id):
    return session.query(Word).filter_by(id=word_id)


# returns word from database
def by_word(word):
    return session.query(Word).filter_by(word=word)


# creates word entity but DOES NOT store
def createWord(form, user):
    return Word(word=form['word'], partOfSpeech=form['partOfSpeech'],
                definition=form['definition'],
                inSentenceSpanish=form['inSentenceSpanish'],
                inSentenceEnglish=form['inSentenceEnglish'],
                user=user)


# edits word entity but DOES NOT store
def editWord(oldWord, form):
    oldWord.word = form['word']
    oldWord.partOfSpeech = form['partOfSpeech']
    oldWord.definition = form['definition']
    oldWord.inSentenceSpanish = form['inSentenceSpanish']
    oldWord.inSentenceEnglish = form['inSentenceEnglish']
    return oldWord


def validInput(user_input):
    if len(user_input) < 4:
        return False
    else:
        return True


def wordChecker(form):
    errors = []
    partsOfSpeech = ['noun', 'adjective', 'verb']
    if 'word' not in form:
        errors.append('You must include a word')
    if not validInput(form['word']):
        errors.append('You must include a valid word')
    if form['partOfSpeech'] not in partsOfSpeech:
        errors.append('You must specify a part of speech')
    if 'definition' not in form:
        errors.append('You must include a definition')
    if not validInput(form['definition']):
        errors.append('You must include a valid definition')
    if 'inSentenceSpanish' not in form:
        errors.append('''You must include an example of the word in a Spanish
                         Sentence''')
    if not validInput(form['inSentenceSpanish']):
        errors.append('You must include a valid Spanish sentence')
    if 'inSentenceEnglish' not in form:
        errors.append('You must translate the example sentence to English')
    if not validInput(form['inSentenceEnglish']):
        errors.append('You must include a valid English sentence')
    return errors


# Login handlers
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/tokensignin', methods=['POST'])
def tokenAuth():
    # receives token from POST request
    token = request.form['idtoken']

    # authenticates token
    try:
        idinfo = client.verify_id_token(token, CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

    except crypt.AppIdentityError:
        return 'NOT VALID'

    # if new user, registers account
    if not by_g_id(idinfo):
        new_user = register(idinfo)
        session.add(new_user)
        session.commit()

    # stores google data in login_session
    login_session['idinfo'] = idinfo

    return idinfo['given_name']


@app.route('/signout')
def clearSession():
    login_session.clear()
    return redirect(url_for('showMain'))


@app.route('/')
def showMain():
    words = session.query(Word).order_by(asc(Word.word))
    title = 'Palabras m&#225;s recientes &#127791; Most recent words'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/nouns')
def showNouns():
    words = session.query(Word).filter_by(partOfSpeech='noun').order_by(asc(Word.word))
    title = 'Palabras m&#225;s recientes &#127791; Most recent words'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/adjectives')
def showAdjectives():
    words = session.query(Word).filter_by(partOfSpeech='adjective').order_by(asc(Word.word))
    title = 'Adjetivos &#127791; Adjectives'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/verbs')
def showVerbs():
    words = session.query(Word).filter_by(partOfSpeech='verb').order_by(asc(Word.word))
    title = 'Verbos &#127791; Verbs'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/new', methods=['GET', 'POST'])
def newWord():
    if request.method == 'POST':
        form = request.form
        errors = wordChecker(form)
        if 'idinfo' not in login_session:
            flash('You must log in to add words')
            return redirect(url_for('login'))
        elif by_word(form['word']):
            flash('%s has already been added' % form['word'])
            return redirect(url_for('newWord'))
        elif errors:
            for error in errors:
                flash(error)
            return redirect(url_for('newWord'))
        else:
            user = by_g_id(login_session['idinfo'])
            word = createWord(form, user)
            session.add(word)
            session.commit()
            flash('Thanks for adding %s, %s!' % (word.word, user.given_name))
            return redirect(url_for('showMain'))
    else:
        if 'idinfo' not in login_session:
            flash('You must log in to add words')
            return redirect(url_for('login'))
        user = by_g_id(login_session['idinfo'])
        return render_template('new-word.html', user=user)


@app.route('/edit/<int:word_id>', methods=['GET', 'POST'])
def editWord(word_id):
    if request.method == 'POST':
        if 'idinfo' not in login_session:
            flash('You must log in to edit words')
            return redirect(url_for('login'))

        user = by_g_id(login_session['idinfo'])
        oldWord = by_word_id(word_id)

        if not oldWord:
            flash('That is not a valid word.')
            return redirect(url_for('showMain'))
        elif oldWord.user.id != user.id:
            flash('You may only edit words that you have added.')
            return redirect(url_for('showMain'))
        else:
            form = request.form
            errors = wordChecker(form)

            if by_word(form['word']):
                matchedWord = by_word(form['word'])
                if oldWord.id != matchedWord.id:
                    flash('%s has already been added' % form['word'])
                    return redirect(url_for('editWord', word_id=word_id))

            if errors:
                for error in errors:
                    flash(error)
                return redirect(url_for('editWord', word_id=word_id))
            else:
                editedWord = editWord(oldWord, form)
                session.add(editedWord)
                session.commit()
                flash('Thanks for updating %s, %s!' % (editedWord.word,
                                                       user.given_name))
                return redirect(url_for('showMain'))

    else:
        if 'idinfo' not in login_session:
            flash('You must log in to edit words')
            return redirect(url_for('login'))

        user = by_g_id(login_session['idinfo'])
        oldWord = by_word_id(word_id)

        if not oldWord:
            flash('That is not a valid word.')
            return redirect(url_for('showMain'))
        elif oldWord.user.id != user.id:
            flash('You may only edit words that you have added.')
            return redirect(url_for('showMain'))
        else:
            return render_template('edit-word.html', user=user, oldWord=oldWord)


@app.route('/delete/<int:word_id>', methods=['GET', 'POST'])
def deleteWord(word_id):
    if request.method == 'POST':
        if 'idinfo' not in login_session:
            flash('You must log in to edit words')
            return redirect(url_for('login'))

        user = by_g_id(login_session['idinfo'])
        word = by_word_id(word_id)

        if not word:
            flash('That is not a valid word.')
            return redirect(url_for('showMain'))
        elif word.user.id != user.id:
            flash('You may only delete words that you have added.')
            return redirect(url_for('showMain'))
        else:
            word_text = word.word
            session.delete(word)
            session.commit()
            flash('You have successfully deleted %s, %s!' % (word_text,
                                                             user.given_name))
            return redirect(url_for('showMain'))

    else:
        if 'idinfo' not in login_session:
            flash('You must log in to delete words')
            return redirect(url_for('login'))

        user = by_g_id(login_session['idinfo'])
        word = by_word_id(word_id)

        if not word:
            flash('That is not a valid word.')
            return redirect(url_for('showMain'))
        elif word.user.id != user.id:
            flash('You may only delete words that you have added.')
            return redirect(url_for('showMain'))
        else:
            return render_template('delete-word.html', user=user, word=word)


@app.route('/jsondict')
def jsonDict():
    words = session.query(Word).all()
    return jsonify(words=[w.serialize for w in words])


if __name__ == '__main__':
    app.secret_key = '0\x1ak\x02\x8a\xc2\xf3\x03\xd1\xf0H\xd0vpBb\xc4\xde\xf5~\xf9\xd3\x9c\xc9'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
