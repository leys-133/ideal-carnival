"""
تطبيق ويب بسيط لإدارة الصف باستخدام Flask.

يوفر هذا التطبيق واجهة ويب تفاعلية تسمح بما يلي:
1. إنشاء صف جديد وتحديد اسم المعلم.
2. إضافة طلاب للصف.
3. تسجيل الحضور اليومي للطلاب مع إمكانية إضافة ملاحظات.
4. عرض تقرير للحضور مع تحليل مبسط من Gemini.

تم الحفاظ على بساطة التصميم والوظائف بحيث يكون التطبيق سهل الاستخدام ويمكن تطويره لاحقًا.
"""

from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import date
from gemini import analyze

# اسم ملف البيانات
DATA_FILE = "data.json"

def load() -> dict:
    """تحميل البيانات من ملف JSON أو إرجاع قاموس فارغ عند عدم وجوده."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save(data: dict) -> None:
    """حفظ البيانات إلى ملف JSON بتنسيق مقروء."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


app = Flask(__name__)


@app.route("/")
def index():
    """عرض الصفحة الرئيسية التي تُظهر جميع الصفوف وروابط للعمليات الأخرى."""
    data = load()
    return render_template("index.html", data=data)


@app.route("/add_class", methods=["GET", "POST"])
def add_class():
    """إنشاء صف جديد. عند إرسال النموذج يتم حفظ الصف والعودة للصفحة الرئيسية."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        teacher = request.form.get("teacher", "").strip()
        if name:
            data = load()
            if name not in data:
                data[name] = {"teacher": teacher, "students": {}}
                save(data)
            return redirect(url_for("index"))
    return render_template("add_class.html")


@app.route("/add_student/<cls>", methods=["GET", "POST"])
def add_student(cls: str):
    """إضافة طالب للصف المحدد. يستقبل معرف الصف كجزء من الرابط."""
    data = load()
    if cls not in data:
        return redirect(url_for("index"))
    if request.method == "POST":
        sid = request.form.get("sid", "").strip()
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        if sid and name:
            data[cls]["students"][sid] = {
                "name": name,
                "phone": phone,
                "days": {}
            }
            save(data)
            return redirect(url_for("index"))
    return render_template("add_student.html", cls=cls)


@app.route("/attendance/<cls>", methods=["GET", "POST"])
def attendance(cls: str):
    """تسجيل الحضور للصف المحدد. يظهر قائمة بالطلاب لتحديد حضورهم وإضافة ملاحظات."""
    data = load()
    if cls not in data:
        return redirect(url_for("index"))
    students = data[cls]["students"]
    if request.method == "POST":
        today = str(date.today())
        for sid in students:
            present = request.form.get(f"present_{sid}") == "on"
            note = request.form.get(f"note_{sid}", "").strip()
            if "days" not in students[sid]:
                students[sid]["days"] = {}
            students[sid]["days"][today] = {"present": present, "note": note}
        save(data)
        return redirect(url_for("index"))
    return render_template("attendance.html", cls=cls, students=students)


@app.route("/report/<cls>")
def report(cls: str):
    """عرض تقرير الحضور للصف المحدد مع تحليل مبسط من Gemini."""
    data = load()
    if cls not in data:
        return redirect(url_for("index"))
    students = data[cls]["students"]
    # بناء نص التقرير
    report_lines = []
    for sid, s in students.items():
        total = len(s.get("days", {}))
        present_count = sum(1 for rec in s.get("days", {}).values() if rec.get("present"))
        report_lines.append(f"{s['name']} حضر {present_count} من {total} أيام")
    report_text = "\n".join(report_lines)
    # استدعاء التحليل من Gemini
    analysis = analyze(report_text)
    return render_template("report.html", cls=cls, students=students, report_lines=report_lines, analysis=analysis)


if __name__ == "__main__":
    # تشغيل التطبيق على المضيف المحلي، يمكن تغيير المضيف والمنفذ حسب الحاجة.
    app.run(debug=True)