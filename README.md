
# Student Health Management System (SHMS)

A web-based application to streamline health services for students in educational institutions.

## 🚀 Features

- Student registration and login
- Book appointments with doctors
- Doctors can view appointments and student records
- Admin can manage users and services
- Students can rate healthcare services

## 🛠️ Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL

## 📁 File Structure

```
/SHMS
|-- app.py                # Main backend logic using Flask
|-- templates/
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|-- static/
|   |-- styles.css
|   |-- script.js
|-- db/
|   |-- setup.sql         # MySQL table definitions
```

## 🖥️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/SHMS.git
   ```

2. **Navigate to the project**
   ```bash
   cd SHMS
   ```

3. **Set up the database**
   - Import the `setup.sql` file into your MySQL server.

4. **Run the Flask app**
   ```bash
   python app.py
   ```

5. **Run on Local Host**
   ```bash
   localhost: [Port number]
   ```
