from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'ismael_searcher_secret'  # Nécessaire pour la session

@app.route('/')
def home():
    # Récupération de l'adresse IP (avec gestion des proxys)
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = request.remote_addr
    # User-Agent (navigateur, OS...)
    user_agent = request.headers.get('User-Agent', 'inconnu')
    # Langue préférée
    lang = request.headers.get('Accept-Language', 'inconnue')
    # Heure de la visite
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    # URL visitée
    url = request.url
    # Affichage dans les logs Render
    log_line = f"[VISITE] {now} | IP: {user_ip} | UA: {user_agent} | Langue: {lang} | URL: {url}\n"
    print(log_line.strip())
    # Enregistrement dans la base SQLite
    try:
        conn = sqlite3.connect('ismael_searcher.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS visites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ip TEXT,
            user_agent TEXT,
            langue TEXT,
            url TEXT
        )''')
        c.execute('''INSERT INTO visites (date, ip, user_agent, langue, url) VALUES (?, ?, ?, ?, ?)''',
                  (now, user_ip, user_agent, lang, url))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur SQLite : {e}")
    return render_template('index.html')

@app.route('/logs', methods=['GET', 'POST'])
def show_logs():
    PASSWORD = '1.Ism@eL.A'
    # Si pas connecté, demander le mot de passe
    if 'logs_auth' not in session:
        if request.method == 'POST':
            if request.form.get('password') == PASSWORD:
                session['logs_auth'] = True
                return redirect(url_for('show_logs'))
            else:
                return render_template('logs_password.html', error=True)
        return render_template('logs_password.html', error=False)
    # Si connecté, afficher les logs
    logs = []
    try:
        conn = sqlite3.connect('ismael_searcher.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM visites ORDER BY id DESC LIMIT 100''')
        logs = c.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la lecture des logs : {e}")
    return render_template('logs.html', logs=logs)

@app.route('/logout_logs')
def logout_logs():
    session.pop('logs_auth', None)
    return redirect(url_for('show_logs'))

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
