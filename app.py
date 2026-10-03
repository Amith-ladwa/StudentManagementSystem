from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET", "POST"])
def index():

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        conn.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )

        conn.commit()

    search = request.args.get("search", "")

    if search:

        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR email LIKE ?",
            ("%" + search + "%", "%" + search + "%")
        ).fetchall()

    else:

        students = conn.execute(
            "SELECT * FROM students"
        ).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    course_stats = conn.execute(
        "SELECT course, COUNT(*) AS total FROM students GROUP BY course"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        search=search,
        total_students=total_students,
        course_stats=course_stats
    )


@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        conn.execute(
            "UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?",
            (name, email, course, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )


if __name__ == "__main__":

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    app.run(debug=True)