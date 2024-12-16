from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session, flash, Response
from io import StringIO
import mysql.connector
import time
from mysql.connector import Error
import os
from flask_cors import CORS
import csv

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.secret_key = 'your_secret_key'  # 需要設置一個秘密金鑰以便使用 session

CORS(app, resources={r"/api/*": {"origins": "*"}})

for i in range(5):  # 最多重試5次
    try:
        db = mysql.connector.connect(
            host="mysql",
            user="root",
            password="rootpassword",
            database="education_platform",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        print("Database connection successful")
        break
    except Error as err:
        print(f"Error: {err}")
        print("Retrying in 10 seconds...")
        time.sleep(10)
else:
    print("Failed to connect to the database after several attempts.")


@app.route('/api/register', methods=['POST'])
def register():
    # 從表單中接收數據
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    role = request.form['role', 'student']
    

    # 檢查是否已存在相同的用戶名或信箱
    cursor = db.cursor()
    check_user_sql = "SELECT * FROM Users WHERE name = %s OR email = %s"
    cursor.execute(check_user_sql, (username, email))
    existing_user = cursor.fetchone()  # 獲取第一行結果，如果存在，則表示已經有此用戶

    if existing_user:
        cursor.close()
        return redirect('/') # 返回400錯誤，表示用戶名或信箱已存在

    # 插入新用戶資料
    insert_user_sql = "INSERT INTO Users (name, password, email, role) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_user_sql, (username, password, email, role))
    db.commit()  # 提交變更
    cursor.close()
    #return jsonify({"status": "success", "message": "註冊成功！"}), 200
    return  redirect('/')  # 註冊成功，返回200狀態碼

@app.route('/api/log', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # 接收表單提交的資料
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor = db.cursor()

        # 查詢資料庫中是否有該用戶名和密碼匹配的記錄
        sql = "SELECT * FROM users WHERE name = %s AND password = %s"
        val = (username, password)
        cursor.execute(sql, val)
        user = cursor.fetchone()

        cursor.close()
        return jsonify({"userId": user[0]}),200

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 接收表單提交的資料
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor = db.cursor()

        # 查詢資料庫中是否有該用戶名和密碼匹配的記錄
        sql = "SELECT * FROM users WHERE name = %s AND password = %s"
        val = (username, password)
        cursor.execute(sql, val)
        user = cursor.fetchone()

        cursor.close()

        # if user:
        #     # 如果登入成功，將用戶狀態儲存在 session 中
        #     session['logged_in'] = True
        #     session['username'] = username
        #     session['user_id'] = user[0]
        #     return redirect('/')  # 登入成功後重定向到首頁
        # else:
    return jsonify({"error": "登入失敗，請檢查帳號和密碼"}),401
    #return redirect('/')  # 回傳登入表單頁面

@app.route('/api/logout')
def logout():
    # 登出，清除 session 中的登入狀態
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/')  # 登出後重定向到首頁

@app.route('/api/user_status', methods=['GET'])
def user_status():
    if 'logged_in' in session and session['logged_in']:
        return jsonify({'logged_in': True, 'username': session['username']})
    else:
        return jsonify({'logged_in': False})

# 新增課程
@app.route('/api/add_courses', methods=['POST'])
def create_course():
    # if session.get('role') != 'teacher':
    #     return jsonify({"status": "error", "message": "Only teachers can create courses."}), 403

    title = request.form['title']
    description = request.form['description']
    video_url = request.form.get('video_url', None)

    cursor = db.cursor()
    sql = "INSERT INTO courses (title, description, video_url, teacher_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (title, description, video_url, session['user_id']))
    db.commit()
    cursor.close()

    return jsonify({"status": "success", "message": "Course created successfully."}), 200

# 抓取資料庫中所有的課程
@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    try:
        # 建立資料庫游標
        cursor = db.cursor(dictionary=True)  # dictionary=True 讓結果以字典形式返回
        
        # 查詢所有課程資料
        sql = "SELECT id, title, description, video_url, created_at FROM courses"
        cursor.execute(sql)
        
        # 獲取結果
        courses = cursor.fetchall()
        cursor.close()
        
        # 返回 JSON 格式的課程資料
        return jsonify({
            "status": "success",
            "courses": courses
        }), 200
    except Exception as e:
        # 異常處理
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# 紀錄學生觀看進度
@app.route('/api/record_progress', methods=['POST'])
def record_progress():
    data = request.get_json() 
    user_id = data['user_id']
    course_id = data['course_id']
    last_progress = data['last_progress']

    cursor = db.cursor()
    sql = """
        INSERT INTO video_watch_progress (user_id, course_id, last_progress)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE last_progress = VALUES(last_progress), last_watched_time = NOW()
    """
    cursor.execute(sql, (user_id, course_id, last_progress))
    db.commit()
    cursor.close()

    return jsonify({"status": "success", "message": "Progress recorded."}), 200

# 獲取學生觀看進度
@app.route('/api/get_progress', methods=['GET'])
def get_progress():
    user_id = request.args.get('id')
    course_id = request.args.get('course_id')

    cursor = db.cursor()
    sql = "SELECT last_progress FROM video_watch_progress WHERE user_id = %s AND course_id = %s"
    cursor.execute(sql, (user_id, course_id))
    progress = cursor.fetchone()
    cursor.close()

    if progress:
        return jsonify({"last_progress": progress[0]})
    else:
        return jsonify({"last_progress": 0})  # 默認從頭開始

# 上傳檔案
# @app.route('/api/assignments', methods=['POST'])
# def submit_assignment():
#     student_id = session['user_id']
#     course_id = request.form['course_id']
#     file_path = request.form['file_path']

#     cursor = db.cursor()
#     sql = "INSERT INTO assignments (student_id, course_id, file_path) VALUES (%s, %s, %s)"
#     cursor.execute(sql, (student_id, course_id, file_path))
#     db.commit()
#     cursor.close()

#     return jsonify({"status": "success", "message": "Assignment submitted successfully."}), 200

# 評分作業
# @app.route('/api/assignments/grade', methods=['POST'])
# def grade_assignment():
#     if session.get('role') != 'teacher':
#         return jsonify({"status": "error", "message": "Only teachers can grade assignments."}), 403

#     assignment_id = request.form['assignment_id']
#     grade = request.form['grade']

#     cursor = db.cursor()
#     sql = "UPDATE assignments SET grade = %s WHERE id = %s"
#     cursor.execute(sql, (grade, assignment_id))
#     db.commit()
#     cursor.close()

#     return jsonify({"status": "success", "message": "Assignment graded successfully."}), 200


# @app.route('/api/courses', methods=['GET'])
# def list_courses():
#     cursor = db.cursor()
#     sql = "SELECT id, title, description, video_url FROM courses"
#     cursor.execute(sql)
#     courses = cursor.fetchall()
#     cursor.close()

#     return jsonify({"courses": [{"id": c[0], "title": c[1], "description": c[2], "video_url": c[3]} for c in courses]})



# 啟動 Flask 應用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)