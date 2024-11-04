from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'  # Needed for session management

ARTICLES_DIR = 'articles/'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

# Ensure articles directory exists
if not os.path.exists(ARTICLES_DIR):
    os.makedirs(ARTICLES_DIR)

# Load articles from filesystem
def load_articles():
    articles = []
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(ARTICLES_DIR, filename), 'r') as f:
                articles.append(json.load(f))
    return articles

# Save an article to filesystem
def save_article(article):
    filename = os.path.join(ARTICLES_DIR, f"{article['title'].replace(' ', '_')}.json")
    with open(filename, 'w') as f:
        json.dump(article, f)

# Delete an article from filesystem
def delete_article(title):
    filename = os.path.join(ARTICLES_DIR, f"{title.replace(' ', '_')}.json")
    if os.path.exists(filename):
        os.remove(filename)

# Routes
@app.route('/')
def home():
    articles = load_articles()
    return render_template('home.html', articles=sorted(articles, key=lambda x: x['date'], reverse=True))

@app.route('/article/<title>')
def article(title):
    filename = os.path.join(ARTICLES_DIR, f"{title.replace(' ', '_')}.json")
    with open(filename, 'r') as f:
        article = json.load(f)
    return render_template('article.html', article=article)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    articles = load_articles()
    return render_template('dashboard.html', articles=articles)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_article():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = datetime.now().strftime('%Y-%m-%d')
        article = {'title': title, 'content': content, 'date': date}
        save_article(article)
        return redirect(url_for('dashboard'))
    return render_template('add_article.html')

@app.route('/admin/edit/<title>', methods=['GET', 'POST'])
def edit_article(title):
    if not session.get('admin'):
        return redirect(url_for('login'))
    filename = os.path.join(ARTICLES_DIR, f"{title.replace(' ', '_')}.json")
    with open(filename, 'r') as f:
        article = json.load(f)
    if request.method == 'POST':
        article['title'] = request.form['title']
        article['content'] = request.form['content']
        save_article(article)
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', article=article)

@app.route('/admin/delete/<title>')
def delete(title):
    if not session.get('admin'):
        return redirect(url_for('login'))
    delete_article(title)
    return redirect(url_for('dashboard'))

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
