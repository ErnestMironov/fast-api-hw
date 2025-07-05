import csv
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    faculty = Column(String(20), nullable=False)
    course = Column(String(50), nullable=False)
    grade = Column(Integer, nullable=False)

class StudentDatabase:
    def __init__(self, db_url: str = "sqlite:///students.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def insert_student(self, last_name: str, first_name: str, faculty: str, course: str, grade: int) -> None:
        student = Student(
            last_name=last_name,
            first_name=first_name,
            faculty=faculty,
            course=course,
            grade=grade
        )
        self.session.add(student)
        self.session.commit()
    
    def get_all_students(self) -> List[Student]:
        return self.session.query(Student).all()
    
    def load_from_csv(self, csv_file_path: str) -> None:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                self.insert_student(
                    last_name=row['Фамилия'],
                    first_name=row['Имя'],
                    faculty=row['Факультет'],
                    course=row['Курс'],
                    grade=int(row['Оценка'])
                )
    
    def get_students_by_faculty(self, faculty: str) -> List[Student]:
        return self.session.query(Student).filter(Student.faculty == faculty).all()
    
    def get_unique_courses(self) -> List[str]:
        courses = self.session.query(Student.course).distinct().all()
        return [course[0] for course in courses]
    
    def get_average_grade_by_faculty(self, faculty: str) -> Optional[float]:
        result = self.session.query(Student).filter(Student.faculty == faculty).all()
        if not result:
            return None
        
        total_grade = sum(student.grade for student in result)
        return total_grade / len(result)
    
    def get_students_by_course_with_low_grade(self, course: str, max_grade: int = 30) -> List[Student]:
        return self.session.query(Student).filter(
            Student.course == course,
            Student.grade < max_grade
        ).all()
    
    def close(self):
        self.session.close()

def main():
    db = StudentDatabase()
    
    print("Loading data from CSV file...")
    db.load_from_csv('Students.csv')
    print("Data loaded successfully!")
    
    print("\n=== Students by faculty ===")
    faculty_students = db.get_students_by_faculty('АВТФ')
    for student in faculty_students[:5]:
        print(f"{student.last_name} {student.first_name} - {student.course}: {student.grade}")
    
    print("\n=== Unique courses ===")
    unique_courses = db.get_unique_courses()
    for course in unique_courses:
        print(course)
    
    print("\n=== Average grades by faculty ===")
    faculties = ['АВТФ', 'ФПМИ', 'ФЛА', 'РЭФ', 'ФТФ']
    for faculty in faculties:
        avg_grade = db.get_average_grade_by_faculty(faculty)
        if avg_grade:
            print(f"{faculty}: {avg_grade:.2f}")
    
    print("\n=== Students with low grades in Math Analysis ===")
    low_grade_students = db.get_students_by_course_with_low_grade('Мат. Анализ', 30)
    for student in low_grade_students[:5]:
        print(f"{student.last_name} {student.first_name} - {student.grade}")
    
    db.close()

if __name__ == "__main__":
    main() 