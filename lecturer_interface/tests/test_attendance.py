from services.student_service import get_students_for_class

students = get_students_for_class("b_tech_i")

for s in students:
    print(s["roll_number"], s["name"])
