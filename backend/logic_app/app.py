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

#CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080", "supports_credentials": True}})
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
    data = request.json
    email = data['email']
    username = data['username']
    password = data['password']
    role = data.get('role', 'student')
    

    # 檢查是否已存在相同的用戶名或信箱
    try:
        cursor = db.cursor()
        # 使用参數化查詢防止 SQL 注入
        check_user_sql = "SELECT * FROM users WHERE name = %s OR email = %s"
        cursor.execute(check_user_sql, (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"status": "error", "message": "用戶名或信箱已存在"}), 400

        insert_user_sql = "INSERT INTO users (name, password, email, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_user_sql, (username, password, email, role))
        db.commit()
        
        return jsonify({"status": "success", "message": "註冊成功！"}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()

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
        if user:
            #request.sessionp['logged_in']=True
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user[0]
            return jsonify({"userId": user[0],"username":session['username']}),200
    else: 
        return jsonify({'error': '用戶未登入'}), 401

# @app.route('/api/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         # 接收表單提交的資料
#         data = request.get_json()
#         username = data['username']
#         password = data['password']
#         cursor = db.cursor()

#         # 查詢資料庫中是否有該用戶名和密碼匹配的記錄
#         sql = "SELECT * FROM users WHERE name = %s AND password = %s"
#         val = (username, password)
#         cursor.execute(sql, val)
#         user = cursor.fetchone()

#         cursor.close()

#         # if user:
#         #     # 如果登入成功，將用戶狀態儲存在 session 中
#         #     session['logged_in'] = True
#         #     session['username'] = username
#         #     session['user_id'] = user[0]
#         #     return redirect('/')  # 登入成功後重定向到首頁
#         # else:
#     return jsonify({"error": "登入失敗，請檢查帳號和密碼"}),401
#     #return redirect('/')  # 回傳登入表單頁面

@app.route('/api/logout')
def logout():
    # 登出，清除 session 中的登入狀態
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/')  # 登出後重定向到首頁

@app.route('/api/user_status', methods=['GET'])
def user_status():
    #return jsonify({'logged_in':session['user_id']}),200
    if 'logged_in' in session and session['logged_in']:
        return jsonify({'logged_in': True,"userId": session['user_id'],'username': session['username']})
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
    cursor = None
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        course_id = data.get('course_id')
        last_progress = data.get('last_progress')
        view_count = data.get('view_count')

        cursor = db.cursor()
        # 先檢查是否存在記錄
        check_sql = """
            SELECT id FROM video_watch_progress 
            WHERE user_id = %s AND course_id = %s 
            ORDER BY last_watched_time DESC LIMIT 1
        """
        cursor.execute(check_sql, (user_id, course_id))
        existing_record = cursor.fetchone()

        if existing_record:
            # 更新現有記錄
            update_sql = """
                UPDATE video_watch_progress 
                SET last_progress = %s, view_count = %s, last_watched_time = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor.execute(update_sql, (last_progress, view_count, existing_record[0]))
        else:
            # 創建新記錄
            insert_sql = """
                INSERT INTO video_watch_progress 
                (user_id, course_id, last_progress, view_count) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (user_id, course_id, last_progress, view_count))
        
        db.commit()
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error in record_progress: {str(e)}")
        if cursor:
            try:
                db.rollback()
            except Exception as rollback_error:
                print(f"Rollback error: {str(rollback_error)}")
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as close_error:
                print(f"Cursor close error: {str(close_error)}")
@app.route('/api/memory_retention', methods=['GET'])
def get_memory_retention():
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        sql = """
            SELECT course_id, last_watched_time, last_progress, view_count
            FROM video_watch_progress
            ORDER BY course_id, last_watched_time
        """
        cursor.execute(sql)
        records = cursor.fetchall()
        
        return jsonify({
            "status": "success",
            "data": records
        })
        
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()   
@app.route('/api/user_watched_courses', methods=['GET'])
def get_user_watched_courses():
    cursor = None
    try:
        cursor = db.cursor()
        user_id = request.args.get('user_id')
        
        print(f"Fetching watched courses for user_id: {user_id}")  # 記錄用戶ID
        
        sql = """
            SELECT DISTINCT course_id 
            FROM video_watch_progress 
            WHERE user_id = %s
        """
        cursor.execute(sql, (user_id,))
        watched_courses = [row[0] for row in cursor.fetchall()]
        
        print(f"Found watched courses: {watched_courses}")  # 記錄查詢結果
        
        # 驗證數據庫中是否有記錄
        cursor.execute("SELECT COUNT(*) FROM video_watch_progress")
        total_records = cursor.fetchone()[0]
        print(f"Total records in video_watch_progress: {total_records}")
        
        # 檢查特定用戶的記錄
        cursor.execute("SELECT COUNT(*) FROM video_watch_progress WHERE user_id = %s", (user_id,))
        user_records = cursor.fetchone()[0]
        print(f"Records for user {user_id}: {user_records}")
        
        return jsonify({
            "watched_courses": watched_courses,
            "debug_info": {
                "user_id": user_id,
                "total_records": total_records,
                "user_records": user_records
            }
        })
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()
# 獲取學生觀看進度
@app.route('/api/get_progress', methods=['GET'])
def get_progress():
    cursor = None
    user_id = request.args.get('id')
    course_id = request.args.get('course_id')
    try:
        cursor = db.cursor()
        sql = """
            SELECT last_progress, view_count
            FROM video_watch_progress 
            WHERE user_id = %s AND course_id = %s 
            ORDER BY last_watched_time DESC
            LIMIT 1
        """
        cursor.execute(sql, (user_id, course_id))

        record = cursor.fetchone()
    except Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
    
    if record:
        return jsonify({
            "last_progress": record[0],
            "view_count": record[1]
        })
    else:
        return jsonify({
            "last_progress": 0,
            "view_count": 0
        })
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