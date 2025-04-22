from app import db
from app.models.course_models import Course, CourseClass, CourseSchedule
from app.models.user import Major
from sqlalchemy import and_
import re

def is_duplicate_course(code, exclude_id=None):
    db.session.expire_all()  # 👈 clear session cache
    query = Course.query.filter_by(code=code)
    if exclude_id:
        query = query.filter(Course.id != exclude_id)
    result = db.session.query(query.exists()).scalar()
    print(f"[DEBUG] Duplicate course? code={code}, exclude_id={exclude_id}, result={result}")
    return result

def is_duplicate_class_code(class_code, exclude_id=None):
    query = CourseClass.query.filter_by(class_code=class_code)
    if exclude_id:
        query = query.filter(CourseClass.id != exclude_id)
    return db.session.query(query.exists()).scalar()

def is_conflicting_schedule(class_id, day_of_week, start_time, end_time, exclude_id=None):
    query = CourseSchedule.query.filter(
        CourseSchedule.course_class_id == class_id,
        CourseSchedule.day_of_week == day_of_week,
        CourseSchedule.start_time < end_time,
        CourseSchedule.end_time > start_time
    )
    if exclude_id:
        query = query.filter(CourseSchedule.id != exclude_id)
    return db.session.query(query.exists()).scalar()
def generate_course_code(major_id):
    major = Major.query.get(major_id)
    if not major or not major.prefix:
        return None

    # Đếm số môn học đã có trong chuyên ngành
    count = Course.query.filter_by(major_id=major_id).count()
    code = f"{major.prefix.upper()}{str(count + 1).zfill(3)}" 
    return code




def generate_prefix_from_name(name):

    if not name:
        return ""
    name = re.sub(r'[^\w\s]', '', name)
    words = name.strip().split()
    prefix = ''.join([word[0].upper() for word in words if word])

    return prefix
