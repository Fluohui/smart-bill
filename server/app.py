from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os, datetime

DB = 'bill.db'
app = Flask(__name__)
CORS(app)

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bill
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item TEXT,
                        amount REAL,
                        category TEXT,
                        date TEXT)''')
init_db()

# 1. 添加账单
@app.post('/api/bill')
def add_bill():
    data = request.json
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bill(item,amount,category,date) VALUES(?,?,?,?)",
                    (data['item'], data['amount'], data['category'], datetime.date.today()))
        conn.commit()
        return jsonify({'id': cur.lastrowid})

# 2. 删除账单
@app.delete('/api/bill/<int:bid>')
def del_bill(bid):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM bill WHERE id=?", (bid,))
        return jsonify({'ok': True})

# 3. 列表 + 本月支出汇总
@app.get('/api/bill')
def list_bill():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM bill ORDER BY date DESC").fetchall()
        # 本月支出
        month_total = conn.execute("SELECT SUM(amount) FROM bill WHERE strftime('%Y-%m',date)=?",
                                   (datetime.date.today().strftime('%Y-%m'),)).fetchone()[0] or 0
        return jsonify({'list': [dict(r) for r in rows], 'monthTotal': month_total})

if __name__ == '__main__':
    app.run(debug=True, port=5000)