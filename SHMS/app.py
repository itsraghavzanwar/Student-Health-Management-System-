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
                cursor.execute("SELECT student_id FROM student WHERE student_email = %s", (username,))
                result = cursor.fetchone()
                if result:
                    session['user_id'] = result[0] 
                    return redirect(url_for('student_dashboard'))
            elif profession == 'Doctor':
                session['email']=username
                cursor.execute("SELECT doctor_id FROM doctor WHERE doctor_email = %s", (username,))
                result = cursor.fetchone()
                if result:
                    session['doctor_id'] = result[0]
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
            session['user_id'] = data1[1] 
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
        session['doctor_id']=data[0]
        if data1:
            username=data1[0]
            return render_template('doctor_dashboard.html',data=data,action=action,username=username)
        return render_template('doctor_dashboard.html',data=data,action=action,username="default_user")
    return render_template('doctor_dashboard.html')

@app.route('/doctor-info', methods=['GET', 'POST'])
@nocache
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

        if city == 'default' and specialization == 'default':
            return render_template('doctor_info.html', doctor_list=doctor_list)
        elif city == 'default':
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
                WHERE d.doctor_speciality = %s
            """
            cursor.execute(query, (specialization))
            doctor_list = cursor.fetchall()
            return render_template('doctor_info.html', doctor_list=doctor_list, selected_specialization=specialization)
        elif specialization == 'default':
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
                WHERE d.doctor_city = %s
            """
            cursor.execute(query, (city,))
            doctor_list = cursor.fetchall()
            return render_template('doctor_info.html', doctor_list=doctor_list,selected_city=city)

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


@app.route('/doctor-request', methods=['GET', 'POST'])
@nocache
def doctor_request():
    doctor = None
    user_rating = None
    google_rating = None
    rating_data=[]
    doctor_id = request.args.get('doctor_id')
    user_id = request.args.get('user_id')
    if request.method == 'GET':
        if doctor_id:
            session['doctor_id'] = doctor_id
            user_id=session.get('user_id')

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
                rating_data=rating_data,
                userIid=user_id
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

            return redirect(url_for('doctor_request', doctor_id=doctor_id, user_id=user_id)) 
        
        return render_template('doctor_request.html', error="Student not found!", doctor=doctor,rating_data=rating_data)

    return render_template('doctor_request.html',doctor=doctor,user_rating=user_rating,google_rating=google_rating,rating_data=rating_data,userIid=user_id)

@app.route('/reviewing',methods=['GET','POST'])
@nocache
def reviewing():
    doctor_id = request.args.get('doctor_id')
    user_id = session.get('user_id')
    if doctor_id:
        session['doctor_id'] = doctor_id
    return render_template('review.html', doctor_id=doctor_id, user_id=user_id)

@app.route('/review',methods=['GET','POST'])
def review():
    if request.method == 'GET':
        doctor_id = session.get('doctor_id')
        user_id = session.get('user_id') 
        rating = request.args.get('rating')
        comment = request.args.get('comment')
        if rating and comment and doctor_id and user_id:
            cursor.execute("""INSERT INTO user_rating (doctor_id, doctor_rating, comment, user_id) VALUES (%s, %s, %s, %s)""", (doctor_id, rating, comment, user_id))
            cursor.connection.commit()

            return redirect(url_for('doctor_request', doctor_id=doctor_id, user_id=user_id))
        
    elif request.method == 'POST':
        doctor_id = session.get('doctor_id')
        user_id = session.get('user_id')
        rating = request.form['rating']
        comment = request.form['comment']

        cursor.execute("""INSERT INTO user_rating (doctor_id, doctor_rating, comment, user_id) VALUES (%s, %s, %s, %s) """, (doctor_id, rating, comment, user_id))
        cursor.connection.commit()

        return redirect(url_for('doctor_request', doctor_id=doctor_id, user_id=user_id))

@app.route('/appointment1', methods=['GET', 'POST'])
@nocache
def appointment1():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('login'))

    if request.method == 'GET':
        query = """
            SELECT a.*, s.student_name 
            FROM appointment a 
            JOIN student s ON a.student_id = s.student_id 
            WHERE a.doctor_id = %s
            ORDER BY 
                (a.appointment_date < CURDATE() OR 
                (a.appointment_date = CURDATE() AND STR_TO_DATE(a.appointment_time, '%%H:%%i') < CURTIME())) ASC,
                a.appointment_date ASC,
                STR_TO_DATE(a.appointment_time, '%%H:%%i') ASC  # Fixed here
        """
        cursor.execute(query, (doctor_id,))
        results = cursor.fetchall()
        return render_template('appointment1.html', results=results)

    
    elif request.method == 'POST':
        action_value = request.form.get('action')
        if action_value:
            action, appointment_id = action_value.split('-', 1)
            comment_field = f'appointment_comment-{appointment_id}'
            comment = request.form.get(comment_field, '').strip()
            
            if not comment:
                query = """SELECT a.*, s.student_name FROM appointment a JOIN student s ON a.student_id = s.student_id WHERE a.doctor_id = %s ORDER BY (a.appointment_date < CURDATE() OR (a.appointment_date = CURDATE() AND STR_TO_DATE(a.appointment_time, '%%H:%%i') < CURTIME())) ASC,a.appointment_date ASC,STR_TO_DATE(a.appointment_time, '%%H:%%i') ASC"""


                cursor.execute(query,(doctor_id,))
                results = cursor.fetchall()
                return render_template('appointment1.html', results=results, error="Please add a comment before approving or rejecting.")
            
            status = 'Approved' if action == 'approved' else 'Rejected'
            update_query = """
                UPDATE appointment
                SET appointment_status = %s, appointment_comment = %s
                WHERE appointment_id = %s
            """
            cursor.execute(update_query, (status, comment, appointment_id))
            cursor.connection.commit()
            
            refresh_query = """
                SELECT a.*, s.student_name 
                FROM appointment a 
                JOIN student s ON a.student_id = s.student_id 
                WHERE a.doctor_id = %s
                ORDER BY 
                    (a.appointment_date < CURDATE() OR 
                    (a.appointment_date = CURDATE() AND STR_TO_DATE(a.appointment_time, '%%H:%%i') < CURTIME())) ASC,
                    a.appointment_date ASC,
                    STR_TO_DATE(a.appointment_time, '%%H:%%i') ASC
            """
            cursor.execute(refresh_query, (doctor_id,))
            results = cursor.fetchall()
            return render_template('appointment1.html', results=results)

    query = """
    SELECT a.*, s.student_name 
    FROM appointment a 
    JOIN student s ON a.student_id = s.student_id 
    WHERE a.doctor_id = %s
    ORDER BY 
        (a.appointment_date < CURDATE() OR 
        (a.appointment_date = CURDATE() AND STR_TO_DATE(a.appointment_time, '%H:%i') < CURTIME())) ASC,
        a.appointment_date ASC,
        STR_TO_DATE(a.appointment_time, '%H:%i') ASC
"""

    cursor.execute(query,(doctor_id,))
    results = cursor.fetchall()
    return render_template('appointment1.html', results=results)

@app.route('/appointment', methods=['GET'])
@nocache
def appointment():
    if request.method == 'GET':
        student_id = session.get('user_id')
        query = """
            SELECT 
                a.*, 
                d.doctor_name  # Add doctor name here
            FROM appointment a 
            JOIN student s ON a.student_id = s.student_id 
            JOIN doctor d ON a.doctor_id = d.doctor_id  # Join doctor table
            WHERE a.student_id = %s
            ORDER BY 
                (a.appointment_date < CURDATE() OR 
                (a.appointment_date = CURDATE() AND STR_TO_DATE(a.appointment_time, '%%H:%%i') < CURTIME())) ASC,
                a.appointment_date ASC,
                STR_TO_DATE(a.appointment_time, '%%H:%%i') ASC
        """
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        return render_template('appointment.html', results=results)

@app.route('/Medical-Record',methods=['GET'])
@nocache
def Medical_record():
    if request.method == 'GET':
        student_id=session.get('user_id')
        cursor.execute("select * from medical_record where student_id = %s",(student_id,))
        data=cursor.fetchall()
        return render_template('medical_record.html',data=data)

@app.route('/medication',methods=['GET'])
@nocache
def medication():
    if request.method == 'GET':
        student_id=session.get('user_id')
        cursor.execute("select * from medication where student_id = %s",(student_id,))
        data=cursor.fetchall()
        return render_template('medication_record.html',data=data)

@app.route('/medication1',methods=['GET','POST'])
@nocache
def medication1():
        if request.method == 'GET':
            return render_template('medication1.html')
        
        elif request.method == 'POST':
            S_Id = request.form['S_Id']
            Appointment = request.form['Appointment']
            Medicine_name = request.form['Medicine_name']
            Dose = request.form['Dose']
            Duration = request.form['Duration']
            Side_effect = request.form['Side_effect']
            if not S_Id or not Appointment or not Medicine_name or not Dose or not Duration or not Side_effect:
                return render_template('medication1.html', error="Please fill in all fields.")

            cursor.execute("""
                INSERT INTO medication (student_id,appointment_id,name,dose,duration,side_effect)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (S_Id,Appointment,Medicine_name,Dose,Duration,Side_effect))
            cursor.connection.commit()

            return render_template('medication1.html', success="Submitted Successfully")
        

if __name__ == '__main__':
    app.run(debug=True)