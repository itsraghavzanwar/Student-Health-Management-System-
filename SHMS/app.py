import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask import make_response
import pymysql
import random
from datetime import datetime,timezone,timedelta
import sqlite3

import smtplib
from email.message import EmailMessage

def nocache(view):
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    no_cache_wrapper.__name__ = view.__name__
    return no_cache_wrapper

app = Flask(__name__)
app.secret_key = 'strong.()io'
app.permanent_session_lifetime = timedelta(days=30)

db = pymysql.connect(
    host="localhost",
    user="root",
    password="smile1",
    database="SHMs"
)

cursor = db.cursor()

@app.route('/')
def home():
    if 'email' in session:
        email = session['email']
        query = "SELECT user_profession FROM all_users_detail WHERE user_email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
            profession = user[0]
            if profession == 'Student':
                return redirect(url_for('student_dashboard'))
            elif profession == 'Doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                session.pop('email', None)
    return render_template('login.html')

@app.route('/term')
def term_and_condition():
    with open('terms.txt','r') as file:
        content=file.read()
    return render_template('term_and_condition.html',content=content)

@app.route('/policy')
def private_policy():
    with open('policy.txt','r') as file:
        content=file.read()
    return render_template('private_policy.html',content=content)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['password']
        remember = request.form.get('remember')
        query = "SELECT user_profession FROM all_users_detail WHERE user_email = %s AND user_password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user:
            profession = user[0]
            session['email'] = username

            if remember:
                session.permanent = True
            else:
                session.permanent = False
            if profession == 'Student':
                session['email']=username
                return redirect(url_for('student_dashboard'))
            elif profession == 'Doctor':
                session['email']=username
                return redirect(url_for('doctor_dashboard'))
        else:
            return render_template('login.html', error="Invalid Username or Password !")
    else:
        return render_template('login.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    show_otp=False
    if request.method =='POST':
        if 'otp' in request.form:
            otp1 = request.form['otp']
            otp = session.get('otp')
            otp_time_str = session.get('otp_time')
            if otp_time_str:
                otp_time = datetime.fromisoformat(otp_time_str)
                now = datetime.now(timezone.utc)
                if now - otp_time > timedelta(minutes=3):
                    session.pop('otp', None)
                    session.pop('otp_time', None)
                    return render_template('forgotpassword.html', show_otp=show_otp, error="OTP expired!")
            if otp== otp1:
                session.pop('otp',None)
                session.pop('otp_time', None)
                session.pop('otp_resend_count', None)
                return render_template('password.html')
            else:
                session.pop('email',None)
                session.pop('otp',None)
                session.pop('otp_time', None)
                session.pop('otp_resend_count', None)
                show_otp=True
                return render_template('forgotpassword.html',show_otp=False,error="Invalid OTP !")
        elif 'username' in request.form:
            username = request.form['username']
            query = "SELECT * FROM all_users_detail WHERE user_email = %s"
            user =  cursor.execute(query,(username,))
            if user:
                session['email'] = username
                otp=""
                for i in range(6):
                    otp += str(random.randint(0,9))
                session['otp']=otp
                session['otp_time'] = datetime.now(timezone.utc).isoformat()
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                
                #set up your mail and password 
                from_mail=''
                server.login(from_mail,'')
                msg = EmailMessage()
                msg['Subject']='SHMs OTP Verification'
                msg['From']=from_mail
                msg['To']=username
                msg.set_content("OTP Verification : "+otp+ "\nVaild for 3 min \nDon't Share With anyone.")
                server.send_message(msg)
                server.quit()
                show_otp=True
                return render_template('forgotpassword.html',show_otp=show_otp,success="otp expire in 3 min!")
            elif 'resend' in request.form:
                username = session.get('email')
                if not username:
                    return render_template('forgotpassword.html', error="Session expired!")
                resend_count = session.get('otp_resend_count', 0)
                if resend_count >= 3:
                    return render_template('forgotpassword.html', show_otp=True, error="You have reached the maximum OTP resend limit.")
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                session['otp'] = otp
                session['otp_time'] = datetime.now(timezone.utc).isoformat()
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()

                #set up your mail and password 
                from_mail=''
                server.login(from_mail,'')
                msg = EmailMessage()
                msg['Subject'] = 'SHMs OTP Verification'
                msg['From'] = from_mail
                msg['To'] = username
                msg.set_content("Your new OTP is: " + otp + "\nValid for 3 minutes.")
                server.send_message(msg)
                server.quit()
                show_otp = True
                return render_template('forgotpassword.html', show_otp=show_otp, success="OTP resent successfully!")
            else:
                return render_template('forgotpassword.html', error = "Username doesn't Exist !")
        else:
            return render_template('forgotpassword.html')
    else:
        return render_template('forgotpassword.html')

@app.route('/forgotpass',methods=['POST'])
def forgotpass():
    email=session.get('email')
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    if not email:
        return render_template('forgotpassword.html', error="Session expired please try again !")

    strong_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$')
    if password != confirm_password:
        return render_template('password.html', error="Passwords don't match!")

    if not strong_regex.match(password):
        return render_template('password.html', error="Password not strong enough! (Use uppercase, lowercase, digit, special char, min 8 characters)")


    query = "update all_users_detail set user_password = %s where user_email = %s"
    cursor.execute(query,(password,email,))
    cursor.connection.commit()
    email = session.pop('email',None)
    return redirect(url_for('login_success'))

@app.route('/login-success')
def login_success():
    return render_template('login.html', success="Password updated successfully!")


@app.route('/student_dashboard',methods=['GET'])
@nocache
def student_dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))
    if request.method == 'GET':
        action = request.args.get('action')
        email=session.get('email')
        if action == 'logout':
            session.pop('email',None)
            session.clear()
            return redirect(url_for('login',success='Log out Successfull !'))
        query = "SELECT student_college_id,student_id , student_name FROM student WHERE student_email = %s"
        cursor.execute(query,(email,))
        data1=cursor.fetchone()
        if data1:
            query = "SELECT * FROM student WHERE student_email = %s"
            cursor.execute(query,(email,))
            data=cursor.fetchone()
            college_id = data1[0]
            qu= data1[1]
            username = data1[2]
            query1="SELECT * FROM college WHERE college_id = %s"
            cursor.execute(query1,(college_id,))
            college_data=cursor.fetchone()
            query2 = "select * from parent_detail where student_id = %s"
            cursor.execute(query2,(qu,))
            pd=cursor.fetchone()
            query3 = "select * from college_detail where student_id = %s"
            cursor.execute(query3,(qu,))
            cd=cursor.fetchone()
            return render_template('student_dashboard.html',data=data,college_data=college_data,pd=pd,cd=cd,username=username,action=action)
    return render_template('student_dashboard.html',data=None,college_data=None,pd=None,cd=None,username="default_user",action=action)

@app.route('/doctor-dashboard',methods=['GET'])
@nocache
def doctor_dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))
    if request.method == 'GET':
        action = request.args.get('action')
        email=session.get('email')
        if action == 'logout':
            session.pop('email',None)
            session.clear()
            return redirect(url_for('login',success='Log out Successfull !'))
        query = "SELECT * FROM doctor WHERE doctor_email = %s"
        cursor.execute(query,(email,))
        data=cursor.fetchone()
        query1 = "SELECT doctor_name FROM doctor WHERE doctor_email = %s"
        cursor.execute(query1,(email,))
        data1=cursor.fetchone()
        if data1:
            username=data1[0]
            return render_template('doctor_dashboard.html',data=data,action=action,username=username)
        return render_template('doctor_dashboard.html',data=data,action=action,username="default_user")
    return render_template('doctor_dashboard.html')

@app.route('/doctor-info', methods=['GET', 'POST'])
def doctor_info():
    if request.method == 'GET':
        email = session.get('email')

        cursor.execute("SELECT student_college_id FROM student WHERE student_email = %s", (email,))
        college_id = cursor.fetchone()

        if college_id:
            cursor.execute("SELECT college_city FROM college WHERE college_id = %s", (college_id[0],))
            city_data = cursor.fetchone()
            city = city_data[0] if city_data else None
        else:
            city = None

        cursor.execute("""
            SELECT 
                d.doctor_id, d.doctor_name, d.doctor_speciality, d.doctor_phone, 
                d.doctor_email, d.doctor_address, d.doctor_city, d.doctor_gender,
                d.doctor_dateofbirth, d.licence_no, d.consultation_fee, 
                gr.doctor_google_rating, gr.total_google_rating,
                IFNULL(ur.avg_rating, 0), IFNULL(ur.total_raters, 0)
            FROM doctor d
            LEFT JOIN google_rating gr ON d.doctor_id = gr.doctor_id
            LEFT JOIN (
                SELECT doctor_id, ROUND(AVG(doctor_rating), 1) AS avg_rating, COUNT(*) AS total_raters
                FROM user_rating GROUP BY doctor_id
            ) ur ON d.doctor_id = ur.doctor_id
            WHERE d.doctor_city = %s
        """, (city,))
        doctor_list = cursor.fetchall()

        return render_template('doctor_info.html', doctor_list=doctor_list)

    elif request.method == 'POST':
        city = request.form.get('city')
        specialization = request.form.get('specialization')

        if city == 'default' or specialization == 'default':
            return render_template('doctor_info.html', doctor_list=[])

        query = """
            SELECT 
                d.doctor_id, d.doctor_name, d.doctor_speciality, d.doctor_phone, 
                d.doctor_email, d.doctor_address, d.doctor_city, d.doctor_gender,
                d.doctor_dateofbirth, d.licence_no, d.consultation_fee, 
                gr.doctor_google_rating, gr.total_google_rating,
                IFNULL(ur.avg_rating, 0), IFNULL(ur.total_raters, 0)
            FROM doctor d
            LEFT JOIN google_rating gr ON d.doctor_id = gr.doctor_id
            LEFT JOIN (
                SELECT doctor_id, ROUND(AVG(doctor_rating), 1) AS avg_rating, COUNT(*) AS total_raters
                FROM user_rating
                GROUP BY doctor_id
            ) ur ON d.doctor_id = ur.doctor_id
            WHERE d.doctor_city = %s AND d.doctor_speciality = %s
        """
        cursor.execute(query, (city, specialization))
        doctor_list = cursor.fetchall()
        return render_template('doctor_info.html', doctor_list=doctor_list,selected_city=city, selected_specialization=specialization)



@app.route('/Medical-Record',methods=['GET'])
def Medical_record():
    return render_template('medical_record.html')

@app.route('/Medication',methods=['GET'])
def medication():
    return render_template('medication_record.html')

@app.route('/appointment',methods=['GET'])
def appointment():
    return render_template('appointment.html')

@app.route('/reviewing',methods=['GET'])
def reviewing():
    doctor_id = 1  # fetch based on context
    user_id = 2    # fetch from session or context
    return render_template('review.html', doctor_id=doctor_id, user_id=user_id)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    doctor_id = request.form['doctor_id']
    user_id = request.form['user_id']
    rating = request.form['rating']
    comment = request.form['comment']

    # Insert into DB
    conn = sqlite3.connect('your_db_file.db')  # replace with actual DB path
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_rating (doctor_id, doctor_rating, comment, user_id)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, rating, comment, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('reviewing'))

@app.route('/doctor-request', methods=['GET', 'POST'])
def doctor_request():
    doctor = None
    user_rating = None
    google_rating = None

    if request.method == 'GET':
        doctor_id = request.args.get('doctor_id')
        if doctor_id:
            

            session['doctor_id'] = doctor_id

            cursor.execute("SELECT * FROM doctor WHERE doctor_id = %s", (doctor_id,))
            doctor = cursor.fetchone()

            cursor.execute("""
                SELECT ROUND(AVG(doctor_rating), 1), COUNT(*) 
                FROM user_rating 
                WHERE doctor_id = %s
            """, (doctor_id,))
            user_rating = cursor.fetchone() 

            cursor.execute("""
                SELECT doctor_google_rating, total_google_rating 
                FROM google_rating 
                WHERE doctor_id = %s
            """, (doctor_id,))
            google_rating = cursor.fetchone()  

            cursor.execute("""SELECT s.student_name, ur.doctor_rating, ur.comment 
            FROM user_rating ur
            JOIN student s ON ur.user_id = s.student_id
            WHERE ur.doctor_id = %s
            """, (doctor_id,))
            rating_data = cursor.fetchall()


            return render_template(
                'doctor_request.html',
                doctor=doctor,
                user_rating=user_rating,
                google_rating=google_rating,
                rating_data=rating_data
            )
    
    elif request.method == 'POST':
        student_email = session.get('email')
        doctor_id = session.get('doctor_id')
        cursor.execute("""SELECT s.student_name, ur.doctor_rating, ur.comment 
            FROM user_rating ur
            JOIN student s ON ur.user_id = s.student_id
            WHERE ur.doctor_id = %s
            """, (doctor_id,))
        rating_data = cursor.fetchall()

        if doctor_id:
            cursor.execute("SELECT * FROM doctor WHERE doctor_id = %s", (doctor_id,))
            doctor = cursor.fetchone()

        cursor.execute("SELECT student_id FROM student WHERE student_email = %s", (student_email,))
        student_id = cursor.fetchone()

        if student_id:
            student_id = student_id[0]
            Date = request.form['Date']
            Time = request.form['Time']
            Issue = request.form['Issue']

            if not Date or not Time or not Issue:
                return render_template('doctor_request.html', error="Please fill in all fields.", doctor=doctor, rating_data=rating_data)

            cursor.execute("""
                INSERT INTO appointment (appointment_date, appointment_reason, appointment_time, student_id, doctor_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (Date, Issue, Time, student_id, doctor_id))
            cursor.connection.commit()

            return render_template('doctor_request.html', success="Request sent successfully!", doctor=doctor,rating_data=rating_data)
            
        return render_template('doctor_request.html', error="Student not found!", doctor=doctor,rating_data=rating_data)

    return render_template('doctor_request.html',rating_data=rating_data)


if __name__ == '__main__':
    app.run(debug=True)