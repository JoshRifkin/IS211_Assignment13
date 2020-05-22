

DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS quizzes;
DROP TABLE IF EXISTS grades;

CREATE TABLE students (
    ID INTEGER PRIMARY KEY,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL
);

CREATE TABLE quizzes (
    ID INTEGER PRIMARY KEY ,
    subject TEXT NOT NULL,
    questions INTEGER NOT NULL,
    quizDate DATE NOT NULL
);

CREATE TABLE grades (
    studID INTEGER NOT NULL,
    quizID INTEGER NOT NULL,
    grade INTEGER NOT NULL
);

INSERT INTO students VALUES (1, 'John', 'Smith');
INSERT INTO quizzes VALUES (1, 'Python Basics', 5, '2015-02-05');
INSERT INTO grades VALUES (1, 1, 85);


