CREATE DATABASE SHMs;

USE SHMs;

CREATE TABLE college (
    college_id INT PRIMARY KEY,
    college_name VARCHAR(255) NOT NULL,
    college_location VARCHAR(255),
    college_city VARCHAR(20)
);

INSERT INTO college(college_id,college_name,college_location,college_city)VAlUES(1,'MIT World Peace Univeristy','Anand Nagar , Kothrud','Pune');

create table all_users_detail(
	user_email VARCHAR(30) PRIMARY KEY,
    user_password VARCHAR(20),
    user_profession ENUM('Student','Doctor'),
    CHECK (
    user_password REGEXP '[A-Z]' AND
    user_password REGEXP '[a-z]' AND 
    user_password REGEXP '[0-9]' AND
    user_password REGEXP '[^a-zA-Z0-9]')
);

INSERT INTO all_users_detail VALUES('joyson@gmail.com','Test@12345','Student')
,('ajayshetty@gmail.com','Test@12345','Doctor')
,('malisingh25@gmail.com','Test@12345','Doctor');

CREATE TABLE student (
    student_id INT primary key,
    student_name VARCHAR(255) NOT NULL,
    student_dateofbirth VARCHAR(10),
    student_age INT,
    student_email VARCHAR(255) UNIQUE,
    student_phone VARCHAR(20) UNIQUE,
    student_address TEXT,
    student_gender ENUM('Male', 'Female', 'Other'),
    student_college_id INT,
    FOREIGN KEY (student_college_id) REFERENCES college(college_id) ON DELETE SET NULL,
	foreign key (student_email) references all_users_detail(user_email)  on delete cascade
);

INSERT INTO student VALUES(1,'Joy Son','10-2-2005',20,'joyson@gmail.com',9876543210,'xyz,Delhi','Male',1);

CREATE TABLE parent_detail (
    student_id INT PRIMARY KEY,
    Dad_name VARCHAR(50),
    Dad_phone VARCHAR(20),
	Dad_email VARCHAR(50),
    Mom_name VARCHAR(50),
    Mom_phone VARCHAR(20),
    Mom_email VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

INSERT INTO parent_detail values(1,'Loy Son',1478523690,'loyson@gmail.com','Jily Son ',1452036987,'jilyson@gmail.com');

CREATE TABLE college_detail (
    student_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    panel VARCHAR(10),
    semester INT,
    FOREIGN KEY (student_id) REFERENCES student(Student_id) ON DELETE CASCADE
);

INSERT INTO college_detail VALUES(1,'B-Tech CSE Core 2023-2027','I',3);

CREATE TABLE doctor (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(255) NOT NULL,
    doctor_speciality VARCHAR(255),
    doctor_phone VARCHAR(20),
    doctor_email VARCHAR(255) UNIQUE,
    doctor_address TEXT,
    doctor_city varchar(20),
    doctor_gender ENUM('Male','Female','Other'),
    doctor_dateofbirth VARCHAR(10),
    licence_no VARCHAR(10),
    consultation_fee int,
    foreign key (doctor_email) references all_users_detail(user_email) on delete cascade
)AUTO_INCREMENT = 1000;

INSERT INTO doctor(doctor_name,doctor_speciality,doctor_phone,doctor_email,doctor_address,doctor_city,doctor_gender,doctor_dateofbirth,licence_no,consultation_fee) VALUES('Dr. Ajay Shetty','Psychiatrist',5820146397,'ajayshetty@gmail.com',
'The Business Hub , kothrud','Pune','Male','14-02-1994','ABC123456',400),
('Dr. Malika Singh','Ophthalmologist',1042633497,'malikasingh25@gmail.com',
'The Optic Angel , Ideal Colony','Pune','Female','16-01-1999','XYZ',250);

CREATE TABLE appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_date DATE NOT NULL,
    appointment_reason TEXT,
    appointment_time TEXT,
    student_id INT,
    doctor_id INT,
    appointment_status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id) ON DELETE CASCADE
)AUTO_INCREMENT = 1000;

create table user_rating(
	doctor_id int,
	doctor_rating float,
    comment text,
    user_id int,
    foreign key(doctor_id) references doctor(doctor_id),
    foreign key(user_id) references student(student_id)
);

insert into user_rating values(1000,4,'he had resolved all the issue of mine.',1);

create table google_rating(
	doctor_id int,
    doctor_google_rating float,
    total_google_rating int
);

insert into google_rating values (1000,3.5,27),(1001,4,22);

CREATE TABLE medical_record (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    medical_date DATE NOT NULL,
    diagnosis TEXT,
    prescription TEXT,
    blood_grp VARCHAR(5),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    parent_medical_info TEXT,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
)auto_increment = 1000;

CREATE TABLE medication (
    med_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT,
    name VARCHAR(255) NOT NULL,
    dose VARCHAR(50),
    duration VARCHAR(50),
    side_effect TEXT,
    FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE CASCADE
)auto_increment = 1000;
