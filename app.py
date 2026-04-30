import os
import psycopg2
from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import tempfile

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ Works for BOTH local + Render
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/student_db"
)

# DATABASE CONNECTION
def get_db():
    return psycopg2.connect(DATABASE_URL)

# CREATE TABLE
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT,
            names TEXT,
            anumber TEXT,
            mother TEXT,
            father TEXT,
            dob TEXT,
            gender TEXT,
            religion TEXT,
            qe TEXT,
            cons TEXT,
            cond TEXT,
            ysik TEXT,
            sira TEXT,
            sikm TEXT,
            ceys TEXT,
            snq TEXT,
            chk TEXT,
            csc TEXT,
            rc TEXT,
            caste TEXT,
            income TEXT,
            rnumber TEXT,
            ypassing TEXT,
            mmias TEXT,
            omias TEXT,
            mmis TEXT,
            mois TEXT,
            mmim TEXT,
            moim TEXT,
            mmism TEXT,
            omism TEXT,
            percentage TEXT,
            smobile TEXT,
            pmobile TEXT,
            address TEXT,
            email TEXT,
            course TEXT,
            dt TEXT,
            staff TEXT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

# LOGIN USER
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/add')
    return render_template('login.html')

# LOGIN ADMIN
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/dashboard')
    return render_template('login2.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return render_template('dashboard.html', data=data)

# ADD STUDENT
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO students (
                name,names,anumber,mother,father,dob,gender,religion,qe,cons,cond,ysik,
                sira,
                sikm,
                ceys,
                snq,
                chk,
                csc,
                rc,caste,income,
                rnumber,ypassing,
                mmias,
                omias,
                mmis,mois,
                mmim,moim,mmism,omism,percentage,smobile,pmobile,address,email,course,dt,staff
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(request.form.values()))

        conn.commit()
        cur.close()
        conn.close()

        return render_template('form.html', success=True)

    return render_template('form.html', success=False)

# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/dashboard')

# EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            UPDATE students SET
                name=%s,names=%s,anumber=%s,mother=%s,
                father=%s,dob=%s,gender=%s,religion=%s,
                qe=%s,cons=%s,cond=%s,
                ysik=%s,
                sira=%s,
                sikm=%s,
                ceys=%s,
                snq=%s,
                chk=%s,
                csc=%s,
                rc=%s,caste=%s,income=%s,
                rnumber=%s,ypassing=%s,
                mmias=%s,
                omias=%s,
                mmis=%s,mois=%s,
                mmim=%s,moim=%s,mmism=%s,omism=%s,percentage=%s,smobile=%s,pmobile=%s,address=%s,email=%s,course=%s,dt=%s,staff=%s
            WHERE id=%s
        """, (*request.form.values(), id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    row = cur.fetchone()

    columns = [desc[0] for desc in cur.description]
    student = dict(zip(columns, row))

    cur.close()
    conn.close()

    return render_template('edit.html', student=student)

# EXPORT
@app.route('/export')
def export():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)

    return send_file(temp.name, as_attachment=True)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
