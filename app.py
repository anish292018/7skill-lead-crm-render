from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Import WhatsApp sender (from whatsapp.py)
from whatsapp import send_whatsapp

app = Flask(__name__)

# -------------------------------
# Database initialization
# -------------------------------
def init_db():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# -------------------------------
# IST Time
# -------------------------------
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

# -------------------------------
# Google Sheets Setup
# -------------------------------
def setup_google_sheets():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute('SELECT * FROM leads ORDER BY id DESC')
    leads = c.fetchall()
    conn.close()
    return render_template('dashboard.html', leads=leads)

@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    try:
        data = request.json

        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        source = data.get('source', '').strip()

        # ---------------- Validation ----------------
        if not name or not phone or not source:
            return jsonify({'success': False, 'message': 'All fields are required'})

        if len(phone) != 10 or not phone.isdigit():
            return jsonify({'success': False, 'message': 'Phone must be 10 digits'})

        created_at = get_ist_time()

        # ---------------- Save to SQLite ----------------
        conn = sqlite3.connect('leads.db')
        c = conn.cursor()

        # Prevent duplicate phone
        c.execute('SELECT phone FROM leads WHERE phone = ?', (phone,))
        if c.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Phone already exists'})

        c.execute(
            'INSERT INTO leads (name, phone, source, created_at) VALUES (?, ?, ?, ?)',
            (name, phone, source, created_at)
        )
        conn.commit()
        conn.close()

        # ---------------- Save to Google Sheets (non-blocking) ----------------
        try:
            sheet = setup_google_sheets()
            sheet.append_row([name, phone, source, created_at])
            print("✅ Lead added to Google Sheets")
        except Exception as e:
            print(f"Google Sheets error: {e}")

        # ---------------- 🔥 Send WhatsApp (TEMPLATE MODE) ----------------
        send_whatsapp(name, phone)

        return jsonify({'success': True, 'message': 'Lead saved successfully'})

    except Exception as e:
        print(f"Submit lead error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_lead/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    try:
        conn = sqlite3.connect('leads.db')
        c = conn.cursor()
        c.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# -------------------------------
# App Start
# -------------------------------
if __name__ == '__main__':
    init_db()
    print("\n" + "=" * 60)
    print("🚀 7Skill Academy Lead CRM")
    print("📊 SQLite | 📄 Google Sheets | 📱 WhatsApp Cloud API")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
