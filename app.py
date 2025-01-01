from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from database import get_student_by_id, get_completed_courses, get_all_sections, get_study_plan, get_courses_by_ids
from api import generate_schedule_with_ai,generate_advice_with_ai, GEMINI_API_KEY
import requests
import pandas as pd
from io import BytesIO


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        flash('Login functionality not implemented yet.')
        return redirect(url_for('index'))
    return render_template('login.html')  # Create a login.html template

@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/profile/<int:student_id>')
def profile(student_id):
    student = get_student_by_id(student_id)  # Fetch student data
    if not student:
        flash("Student not found!")
        return redirect(url_for('index'))

    # Fetch completed courses as names
    completed_course_ids = student.get('courses_completed', '').split(',')
    course_names = get_completed_courses(completed_course_ids) if completed_course_ids else []

    # Fetch all sections
    sections = get_all_sections()

    print("Student Data:", student)
    print("Completed Courses:", course_names)
    print("Sections:", sections)

    return render_template('profile.html', student=student, course_names=course_names, sections=sections)



@app.route('/fetch', methods=['POST'])
def fetch_profile():
    student_id = request.form.get('student-id')
    if not student_id:
        flash("Please enter a Student ID.")
        return redirect(url_for('index'))

    # Redirect to the profile page if the student exists
    return redirect(url_for('profile', student_id=student_id))

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        # Parse incoming data
        data = request.get_json()
        print("Incoming Data:", data)

        # Validate student ID
        student_id = data.get("student_id")
        if not student_id:
            return jsonify({"error": "Missing student ID"}), 400

        # Fetch student data
        student = get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        print("Fetched Student Data:", student)  # Debugging

        # Validate plan number and major ID
        plan_number = student.get("plan_number")
        major_id = student.get("major_id")
        if not plan_number or not major_id:
            return jsonify({"error": "Plan Number or Major ID is missing for this student!"}), 400

        # Fetch study plan
        study_plan = get_study_plan(plan_number, major_id)
        if not study_plan:
            return jsonify({
                "error": f"Study plan not found for Plan Number: {plan_number} and Major ID: {major_id}"
            }), 404

        print("Study Plan Sent to AI (Formatted):")
        for course in study_plan:
            print(f"- {course['course_name']} ({course['section_name']}, {course['credits']} credits)")

        # Fetch completed courses
        completed_course_ids = student.get("courses_completed", "").split(",")
        completed_courses = get_completed_courses(completed_course_ids)
        print("Completed Courses:", completed_courses)  # Debugging

        # Gather student answers
        answers = {
            "hours": data.get("hours"),
            "graduate": data.get("graduate"),
            "course_type": data.get("course_type"),
            "sections": data.get("sections"),
        }
        print("Student Answers:", answers)  # Debugging

        # Transform student dictionary for AI
        student_ai = {
            "Name": student.get("name"),
            "Major": student.get("major"),
            "Plan_Number": student.get("plan_number"),
            "Hours_Completed": student.get("hours_completed"),
            "Courses_Completed": student.get("courses_completed"),
            "Major_ID": student.get("major_id"),
        }

        # Call the AI function
        ai_response = generate_schedule_with_ai(student_ai, study_plan, completed_courses, answers)
        print("AI Response:", ai_response)  # Debugging

        # Handle errors from AI response
        if "error" in ai_response:
            return jsonify({"error": ai_response["error"]}), 500

        # Extract the schedule from the AI response
        schedule = ai_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No schedule generated.")
        return jsonify({"schedule": schedule}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred while generating the schedule",
            "details": str(e)
        }), 500


@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    try:
        # Get schedule data from the request
        data = request.get_json()
        schedule = data.get("schedule")
        if not schedule:
            return jsonify({"error": "No schedule data provided"}), 400

        # Convert the schedule data to a DataFrame
        df = pd.DataFrame(schedule)

        # Save the DataFrame to a BytesIO object
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Schedule")
        output.seek(0)

        # Send the Excel file to the user
        return send_file(
            output,
            as_attachment=True,
            download_name="schedule.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        print("Error saving schedule to Excel:", str(e))
        return jsonify({"error": "An error occurred while saving the schedule", "details": str(e)}), 500


@app.route('/get_advice', methods=['POST'])
def get_advice():
    try:
        data = request.get_json()
        courses = data.get("courses")
        language = data.get("language")

        if not courses or not language:
            return jsonify({"error": "Missing courses or language data"}), 400

        advice_response = generate_advice_with_ai(courses, language)

        if "error" in advice_response:
            return jsonify({"error": advice_response["error"]}), 500

        return jsonify({"message": advice_response["message"]})

    except Exception as e:
        return jsonify({"error": "An error occurred while getting advice", "details": str(e)}), 500


@app.route('/contact')
def contact():
    """
    Route to display the contact page.
    """
    # Render the contact.html template
    return render_template('contact.html')



if __name__ == "__main__":
    app.run(debug=True)
