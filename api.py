import requests

GEMINI_API_KEY = "AIzaSyDMsrXIZ_wYC8B-a1gA-wV4QEOT9705REA"

def generate_schedule_with_ai(student, all_courses, completed_courses, answers):
    try:
        # Enhanced prompt for generating a highly accurate schedule
        prompt = (
            f"You are tasked with generating a precise and logical semester schedule for a university student. "
            f"Follow these detailed instructions and strictly adhere to the JSON format."
            f"\n\n### Context ###\n"
            f"Student Information:\n"
            f"- Name: {student['Name']}\n"
            f"- Major: {student['Major']}\n"
            f"- Hours Completed: {student['Hours_Completed']}\n"
            f"- Desired Hours for the Semester: {answers.get('hours')}\n"
            f"- Graduate Status: {answers.get('graduate')}\n\n"
            f"Study Plan (Courses Available):\n"
            f"{[{'course_name': course['course_name'], 'credits': course['credits'], 'section_name': course['section_name']} for course in all_courses]}\n\n"
            f"Completed Courses:\n"
            f"{[course for course in completed_courses]}\n\n"
            f"Student Preferences:\n"
            f"- Preferred Sections: {answers.get('sections')}\n"
            f"- Course Type Preference: {answers.get('course_type')}\n\n"
            f"### Instructions ###\n"
            f"1. The total credit hours **must exactly match** the student's desired hours ({answers.get('hours')} hours)."
            f" This is a strict requirement; no deviations are allowed.\n"
            f"2. If it is **not possible** to match the exact hours due to course credit constraints, "
            f"clearly indicate this in the JSON response with an explanation under a new field: 'note'.\n"
            f"3. Include only courses that the student has not completed yet from the provided study plan.\n"
            f"4. Ensure all prerequisites for selected courses are satisfied by the student's completed courses.\n"
            f"5. Prioritize courses from the student's preferred sections (e.g., 'General Education', 'Core Requirements'). "
            f"At least one course must be selected from each specified section in their preferences.\n"
            f"6. Only include courses that are 3 credit hours or less. Exclude any course exceeding this limit.\n"
            f"7. Replace the '<section>' placeholder in the JSON with the actual section name from the provided data (e.g., 'General Education').\n"
            f"8. If the exact number of hours cannot be achieved with courses from the preferred sections, "
            f"add courses from other sections in the study plan to meet the hour requirement.\n"
            f"9. Exclude any zero-credit courses unless the student is a graduate.\n"
            f"10. Optimize the schedule for logical academic progression and balance between general education, major-specific, and elective courses.\n"
            f"11. Provide the **exact total hours** in the 'hours' field after generating the schedule and include it in the JSON.\n"
            f"12. If you cannot meet the required hours, include a 'suggested_hours' field in the JSON with a suggested total that works for the provided constraints.\n\n"
            f"### JSON Format ###\n"
            f"{{\n"
            f'  "student": "{student["Name"]}",\n'
            f'  "major": "{student["Major"]}",\n'
            f'  "hours": {answers.get("hours")},\n'
            f'  "suggested_hours": <suggested_hours_if_needed>,\n'
            f'  "note": "<reason_if_exact_hours_are_not_met>",\n'
            f'  "courses": [\n'
            f'    {{\n'
            f'      "course_name": "<name>",\n'
            f'      "credits": <credits>,\n'
            f'      "section": "<section_name>"\n'
            f"    }},\n"
            f"    ...\n"
            f"  ]\n"
            f"}}\n\n"
            f"### Respond Now ###"
        )


        # Prepare the payload for the API request
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        # Send request to the AI API
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
        )

        # Check for API response status
        if response.status_code != 200:
            print(f"Gemini API Error: {response.status_code} - {response.text}")
            return {"error": f"Gemini API call failed: {response.text}"}

        return response.json()

    except Exception as e:
        print("Error in generate_schedule_with_ai:", str(e))
        return {"error": str(e)}

def generate_advice_with_ai(courses, language):
    try:
        # Language-specific instruction
        language_prompt = "Write the response in English." if language.lower() == "english" else "Write the response in Arabic."

        # Generate the AI prompt
        prompt = (
            f"I have the following courses:\n{courses}\n"
            f"{language_prompt} Provide advice for a student taking these courses, focusing on study strategies, potential challenges, and resources."
        )

        # Send request to Gemini API
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
        )

        # Log and handle API response
        if response.status_code != 200:
            return {"error": f"API Error: {response.status_code} - {response.text}"}

        advice = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return {"message": advice}

    except Exception as e:
        print("Error in generate_advice_with_ai:", str(e))
        return {"error": str(e)}