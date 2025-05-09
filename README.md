
# Student Health Management System (SHMS)

A web-based application to streamline health services for students in educational institutions.

## 🚀 Features
**For Student**
- Student login and forget password
- Book appointments with doctors
- Students can rate healthcare services
  
**For Doctor**
- The admin team will manually create the account after verifying all the details provided through mail
- After payment is processed, the doctor detail will be displayed
- Approvment for an appointments
- Doctors can view appointments and student records

## 🛠️ Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL

## 🖥️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/SHMS.git
   ```

2. **Mail Id setup**
- In app.py Link your Mail Id and Password for 'Forget Password' Feature in 'forgot_password' Function at two if condition i.e 'username' and 'resend'

3. **Navigate to the project**
   ```bash
   cd SHMS
   ```

4. **Set up the database**
   - Import the `setup.sql` file into your MySQL server.

5. **Install Flask and PyMySQL**
   ```bash
   pip install flask
   pip install PyMySQL
   ```

6. **Run the Flask app**
   ```bash
   python app.py
   ```

7. **Run on Local Host**
   ```bash
   localhost: [Port number]
   ```
8. **Login in detail**
- For login functionality and email reception, please ensure your credentials are correctly stored in the MySQL database. Alternatively, you may log in using the provided credentials: Username: joyson@gmail.com Password: Test@12345 . However, please note that the 'Forgot Password' feature will not be operational, as email notifications will not be received
