from flask import Flask, request, jsonify
app = Flask(__name__)

students, courses, grades = [], [], []

@app.get("/")
def home():
    return "API is running. Use /students, /courses, /grades"

# Add student
@app.post("/students")
def add_student():
    data = request.json
    students.append(data)
    return jsonify(data), 201

# Add course
@app.post("/courses")
def add_course():
    data = request.json
    courses.append(data)
    return jsonify(data), 201

# Add grade
@app.post("/grades")
def add_grade():
    data = request.json
    score = data.get("score", -1)
    if 0 <= score <= 100:
        grades.append(data)
        return jsonify(data), 201
    return jsonify({"error": "score must be 0-100"}), 400

# Get students
@app.get("/students")
def list_students():
    return jsonify(students)

# DELETE
@app.delete("/courses/<int:course_id>")
def delete_course(course_id):
    for c in courses:
        if c["id"] == course_id:
            courses.remove(c)
            return jsonify({"message": "deleted"})
    return jsonify({"error": "not found"}), 404

# PUT grade
@app.put("/grades")
def update_grade():
    data = request.json
    for g in grades:
        if g["student_id"] == data["student_id"] and g["course_id"] == data["course_id"]:
            g["score"] = data["score"]
            return jsonify(g)
    return jsonify({"error": "not found"}), 404

# Get GPA
@app.get("/students/gpa")
def students_gpa():
    result = []
    for s in students:
        scores = [g["score"] for g in grades if g["student_id"] == s["id"]]
        gpa = round(sum(scores) / len(scores) / 25, 2) if scores else 0
        result.append({"id": s["id"], "name": s["name"], "gpa": gpa})
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False)
