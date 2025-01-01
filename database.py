import sqlite3

DB_PATH = "data/Study_Plans.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# Student-related functions
def get_student_by_id(student_id):
    """Fetch a student's data by ID, including their major ID."""
    conn = get_db_connection()
    query = """
        SELECT s.Student_ID as id, s.Name as name, s.Major as major, s.Plan_Number as plan_number,
               s.Hours_Completed as hours_completed, s.Courses_Completed as courses_completed,
               m.major_id
        FROM Students s
        JOIN Majors m ON s.Major = m.major_name
        WHERE s.Student_ID = ?
    """
    student = conn.execute(query, (student_id,)).fetchone()
    conn.close()
    return dict(student) if student else None



def get_completed_courses(course_ids):
    """Fetch names of completed courses from a list of course IDs."""
    if not course_ids:  # Handle empty lists
        return []
    conn = get_db_connection()
    placeholders = ', '.join('?' for _ in course_ids)
    query = f"SELECT course_name FROM Courses WHERE course_id IN ({placeholders})"
    courses = conn.execute(query, course_ids).fetchall()
    conn.close()
    return [course['course_name'] for course in courses]

# Major-related functions
def get_major_by_name(major_name):
    """Fetch a major's ID by its name."""
    conn = get_db_connection()
    query = "SELECT * FROM Majors WHERE major_name = ?"
    major = conn.execute(query, (major_name,)).fetchone()
    conn.close()
    return dict(major) if major else None

# Plan-related functions
def get_plan_by_major_and_number(major_id, plan_number):
    """Fetch a plan's data by major ID and plan number."""
    conn = get_db_connection()
    query = "SELECT * FROM Plans WHERE major_id = ? AND plan_number = ?"
    plan = conn.execute(query, (major_id, plan_number)).fetchone()
    conn.close()
    return dict(plan) if plan else None

# Course-related functions
def get_courses_by_ids(course_ids):
    """Fetch detailed course information by their IDs."""
    if not course_ids:  # Handle empty lists
        return []
    conn = get_db_connection()
    placeholders = ', '.join('?' for _ in course_ids)
    query = f"SELECT * FROM Courses WHERE course_id IN ({placeholders})"
    courses = conn.execute(query, course_ids).fetchall()
    conn.close()
    return [dict(course) for course in courses]

def get_course_name_by_id(course_id):
    """Fetch a course name by its ID."""
    conn = get_db_connection()
    query = "SELECT course_name FROM Courses WHERE course_id = ?"
    course = conn.execute(query, (course_id,)).fetchone()
    conn.close()
    return course['course_name'] if course else None

# Study plan-related functions
def get_study_plan(plan_number, major_id):
    """Fetch a study plan by its plan number and major ID."""
    conn = get_db_connection()
    query = """
        SELECT spc.*, c.course_name, c.credits, s.section_name
        FROM StudyPlanCourses spc
        JOIN Courses c ON spc.course_id = c.course_id
        JOIN Plans p ON spc.plan_id = p.plan_id
        JOIN Sections s ON spc.section_id = s.section_id
        WHERE p.plan_number = ? AND p.major_id = ?
    """
    plan = conn.execute(query, (plan_number, major_id)).fetchall()
    conn.close()
    return [dict(row) for row in plan]

# Section-related functions
def get_all_sections():
    """Fetch all sections from the database."""
    conn = get_db_connection()
    query = "SELECT section_id as id, section_name as name FROM Sections"
    sections = conn.execute(query).fetchall()
    conn.close()
    return [dict(section) for section in sections]


# Plan-related metadata functions
def get_plan_maximums(plan_id):
    """Fetch maximum hours and other plan-related limits."""
    conn = get_db_connection()
    query = "SELECT * FROM Plans WHERE plan_id = ?"
    plan = conn.execute(query, (plan_id,)).fetchone()
    conn.close()
    return dict(plan) if plan else None
