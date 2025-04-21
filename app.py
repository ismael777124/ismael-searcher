from flask import Flask, render_template, request
from datetime import datetime
import sqlite3

app = Flask(__name__)

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

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
