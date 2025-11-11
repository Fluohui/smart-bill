from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3, os, datetime
import pandas as pd
from io import StringIO, BytesIO

DB = 'bill.db'
app = Flask(__name__)
CORS(app)

# ---------- 初始化表 ----------
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bill(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            amount REAL,
            category TEXT,
            date TEXT)''')
init_db()

# ---------- 原有 CRUD ----------
@app.post('/api/bill')
def add_bill():
    data = request.json
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bill(item,amount,category,date) VALUES(?,?,?,?)",
                    (data['item'], data['amount'], data['category'], datetime.date.today()))
        conn.commit()
        return jsonify({'id': cur.lastrowid})

@app.delete('/api/bill/<int:bid>')
def del_bill(bid):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM bill WHERE id=?", (bid,))
        return jsonify({'ok': True})

@app.get('/api/bill')
def list_bill():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM bill ORDER BY date DESC").fetchall()
        month_total = conn.execute("SELECT SUM(amount) FROM bill WHERE strftime('%Y-%m',date)=?",
                                   (datetime.date.today().strftime('%Y-%m'),)).fetchone()[0] or 0
        return jsonify({'list': [dict(r) for r in rows], 'monthTotal': month_total})

# ---------- CSV 导入 ----------
@app.post('/api/upload')
def upload_csv():
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV'}), 400

    content = file.read().decode('utf-8')

    # 1. 先找到真正的表头行
    for skip in range(10, 25):                       # 从第 10 行开始试到 25 行
        try:
            df = pd.read_csv(StringIO(content), skiprows=skip, nrows=0)   # skiprows=16
            if '交易时间' in df.columns:
                break                                # 找到就停
        except Exception:
            continue                                 # 读不到就继续往下跳
    else:                                            # 整段循环结束还没找到
        return jsonify({'error': '未找到表头'}), 400

    # 2. 用正确行数正式读全表
    df = pd.read_csv(StringIO(content), skiprows=skip)

    # 3. 微信格式
    if '交易时间' in df.columns:
        df = df.rename(columns={
            '交易时间': 'date',
            '收/支': 'type',
            '交易对方': 'item',
            '金额(元)': 'amount'
        })
        df['amount'] = df['amount'].replace('¥', '', regex=True).astype(float)
        df = df[df['type'] == '支出']
        records = df[['date', 'item', 'amount']].to_dict(orient='records')

    # 4. 支付宝格式
    elif '交易创建时间' in df.columns:
        df = pd.read_csv(StringIO(content))   # 支付宝表头在第一行，不需要 skip
        df = df.rename(columns={
            '交易创建时间': 'date',
            '商品名称': 'item',
            '金额（元）': 'amount',
            '资金状态': 'status'
        })
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df[df['status'] == '支出']
        records = df[['date', 'item', 'amount']].to_dict(orient='records')

    else:
        return jsonify({'error': '不识别的文件格式'}), 400

    # 5. 批量入库
    with sqlite3.connect(DB) as conn:
        for r in records:
            conn.execute("INSERT INTO bill(item,amount,category,date) VALUES (?,?,?,?)",
                         (r['item'], abs(r['amount']), 'CSV导入', r['date'][:10]))
        conn.commit()
    return jsonify({'ok': True, 'count': len(records)})

# ---------- Excel 导出 ----------
@app.get('/api/export')
def export_excel():
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql_query("""
            SELECT date, item, amount, category
            FROM bill
            WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
            ORDER BY date DESC
        """, conn)

    if df.empty:
        return jsonify({'error': '本月无数据'}), 400

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='月度账单')
    output.seek(0)
    return send_file(output, download_name='月度账单.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)