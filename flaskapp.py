from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash)
from flask import session as login_session
from oauth2client import client, crypt
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/linuxapp5.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

app.secret_key = '0\x1ak\x02\x8a\xc2\xf3\x03\xd1\xf0H\xd0vpBb\xc4\xde\xf5~\xf9\xd3\x9c\xc9'

CLIENT_ID = json.loads(open('/var/www/html/flaskapp/client_secrets.json', 'r').read()
                       )['web']['client_id']
APPLICATION_NAME = "&#191;Como lo dice?"

# Create our database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    g_id = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    given_name = db.Column(db.String(30), nullable=False)
    family_name = db.Column(db.String(30), nullable=False)
    picture = db.Column(db.String(500), nullable=False)

    def __init__(self, g_id, email, given_name, family_name, picture):
        self.g_id = g_id
        self.email = email
        self.given_name = given_name
        self.family_name = family_name
        self.picture = picture

    def __repr__(self):
        return '<User %r>' % self.given_name


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('words', lazy='dynamic'))
    word = db.Column(db.String(80), nullable=False)
    partOfSpeech = db.Column(db.String(9), nullable=False)
    definition = db.Column(db.String(300), nullable=False)
    inSentenceSpanish = db.Column(db.String(300), nullable=False)
    inSentenceEnglish = db.Column(db.String(300), nullable=False)

    def __init__(self, user, word, partOfSpeech, definition, inSentenceSpanish,
                 inSentenceEnglish):
        self.user = user
        self.word = word
        self.partOfSpeech = partOfSpeech
        self.definition = definition
        self.inSentenceSpanish = inSentenceSpanish
        self.inSentenceEnglish = inSentenceEnglish

    def __repr__(self):
        return '<Word %r>' % self.word

db.create_all()


# classmethod functions for User DB
# looks up user entity by id number
def by_user_id(u_id):
    return User.query.filter_by(id=u_id).first()


# looks up user entity by g_id number
def by_g_id(idinfo):
    g_id = idinfo['sub']
    return User.query.filter_by(g_id=g_id).first()


# creates user entity but DOES NOT store
def register(idinfo):
    return User(g_id=idinfo['sub'], email=idinfo['email'],
                given_name=idinfo['given_name'],
                family_name=idinfo['family_name'],
                picture=idinfo['picture'])


# Helper functions for Word DB
# looks up word entity by id number
def by_word_id(word_id):
    return Word.query.filter_by(id=word_id).first()


# returns word from database
def by_word(word):
    return Word.query.filter_by(word=word).first()


# creates word entity but DOES NOT store
def createWord(form, user):
    return Word(word=form['word'], partOfSpeech=form['partOfSpeech'],
                definition=form['definition'],
                inSentenceSpanish=form['inSentenceSpanish'],
                inSentenceEnglish=form['inSentenceEnglish'],
                user=user)


# edits word entity but DOES NOT store
def editWordFun(oldWord, form):
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
        db.session.add(new_user)
        db.session.commit()

    # stores google data in login_session
    login_session['idinfo'] = idinfo

    return idinfo['given_name']


@app.route('/signout')
def clearSession():
    login_session.clear()
    return redirect(url_for('showMain'))


@app.route('/')
def showMain():
    words = Word.query.all()
    title = 'Palabras m&#225;s recientes &#127791; Most recent words'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/nouns')
def showNouns():
    words = Word.query.filter_by(partOfSpeech='noun')
    title = 'Palabras m&#225;s recientes &#127791; Most recent words'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/adjectives')
def showAdjectives():
    words = Word.query.filter_by(partOfSpeech='adjective')
    title = 'Adjetivos &#127791; Adjectives'
    params = {'title': title}
    if 'idinfo' in login_session:
        params['user'] = by_g_id(login_session['idinfo'])
    if words:
        params['words'] = words
    return render_template('word-list.html', **params)


@app.route('/verbs')
def showVerbs():
    words = Word.query.filter_by(partOfSpeech='verb')
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
            db.session.add(word)
            db.session.commit()
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
                editedWord = editWordFun(oldWord, form)
                db.session.add(editedWord)
                db.session.commit()
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
            db.session.delete(word)
            db.session.commit()
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
    words = (Word).query.all()
    return jsonify(words=[w.serialize for w in words])


if __name__ == '__main__':
    app.secret_key = '0\x1ak\x02\x8a\xc2\xf3\x03\xd1\xf0H\xd0vpBb\xc4\xde\xf5~\xf9\xd3\x9c\xc9'