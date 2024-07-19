import json

from flask import Flask, render_template, request, jsonify, url_for, flash, session, redirect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import smtplib
from email.mime.text import MIMEText
import os
import cv2 as cv
from datetime import datetime
from torchvision.transforms import transforms
from tools.accuracy_caculator import acc_calculator
from tools.detector import detect
from tools.segmentor import *
from werkzeug.utils import secure_filename
import mysql.connector
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload_folder'
app.config['PROCESSED_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECURITY_PASSWORD_SALT'] = secrets.token_hex(16)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'masterdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# MySQL database configuration
db_config = {
    'user': 'root',
    'password': 'lnledwZHN42wLqCv6JFn',
    'host': 'remote.runflare.com:30168',
    'database': 'mysqlguo_db'
}

# Generate a secure secret key if not set in environment
if not os.getenv('FLASK_SECRET_KEY'):
    os.environ['FLASK_SECRET_KEY'] = secrets.token_hex(32)

app.secret_key = os.getenv('FLASK_SECRET_KEY')

s = URLSafeTimedSerializer(app.secret_key)


class User:
    def __init__(self, id, first_name, last_name, email, password, verfied):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.verified = verfied

    def __repr__(self):
        return json.dumps(self.__dict__)


# Database setup
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100),
            verified BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_image(filepath, filename):
    original_image = cv.imread(filepath)
    assert original_image is not None, "File could not be read, check with os.path.exists()"
    original_image = cv.cvtColor(original_image, cv.COLOR_BGR2RGB)
    shape = original_image.shape

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((390, 390))
    ])

    segmented_image = segment(original_image, transform, shape)
    binary_thresh, _, cropped_images = detect(segmented_image, original_image)
    labels, result, predict_label = acc_calculator(cropped_images, type='area')
    _, detected_image, _ = detect(segmented_image, original_image, labels=labels, label_annotate=True)

    # Save images
    cv.imwrite(os.path.join(app.config['PROCESSED_FOLDER'], f'{filename}_original.jpg'),
               cv.cvtColor(original_image, cv.COLOR_RGB2BGR))
    cv.imwrite(os.path.join(app.config['PROCESSED_FOLDER'], f'{filename}_segmented.jpg'), segmented_image)
    cv.imwrite(os.path.join(app.config['PROCESSED_FOLDER'], f'{filename}_binary_thresh.jpg'), binary_thresh)
    cv.imwrite(os.path.join(app.config['PROCESSED_FOLDER'], f'{filename}_detected.jpg'),
               cv.cvtColor(detected_image, cv.COLOR_RGB2BGR))

    return result, predict_label


@app.route('/')
def home():
    init_db()
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            if user['verified']:
                session['user_id'] = user['id']
                session.permanent = True
                # user_id = user['id']
                return redirect(url_for('index'))
            else:
                flash('Email not verified. Please check your email.', 'warning')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        token = s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
        link = url_for('confirm_email', token=token, _external=True)

        msg = MIMEText(f'Please click the link to verify your email: {link}')
        msg['Subject'] = 'Email Verification'
        msg['From'] = 'mahdiarmansouri@gmail.com'
        msg['To'] = email

        # Choose the appropriate method for your SMTP configuration
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login('mahdiarmansouri@gmail.com', 'ugrv ixjg sxsf xvml')
                server.sendmail('mahdiarmansouri@gmail.com', email, msg.as_string())
        except Exception as e:
            print(f"Failed to send email: {e}")
            flash('Failed to send verification email.', 'danger')
            return redirect(url_for('signup'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)',
                       (first_name, last_name, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('A verification link has been sent to your email address.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except SignatureExpired:
        flash('The confirmation link has expired.', 'danger')
        return redirect(url_for('signup'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET verified = TRUE WHERE email = %s', (email,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Your email has been verified!', 'success')
    return redirect(url_for('login'))


@app.route('/main')
def index():
    user_id = session.get('user_id')
    db_config = {
        'user': 'root',
        'password': 'root123',
        'host': 'localhost',
        'database': 'masterdb'
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    user = cursor.fetchone()
    user = User(*user)

    return render_template('main.html', user=user)


@app.route('/exam')
def exam():
    files = []
    for file in os.listdir('static/images/exam_images'):
        if file.endswith('.jpg'):
            files.append(file)
            print(file)
    print(files)
    return render_template('exam.html', files=files)


@app.route('/show-result')
def show_result():
    user_id = session.get('user_id')
    answers = session.get('answers')

    db_config = {
        'user': 'root',
        'password': 'root123',
        'host': 'localhost',
        'database': 'masterdb'
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    user = cursor.fetchone()
    user = User(*user)
    print(user)

    answers = json.loads(answers)
    print(answers)

    list_length = len(answers)

    return render_template('show_result.html', user=user, list_length=list_length, answers=answers)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/about-me')
def about_me():
    return render_template('about_me.html')


@app.route('/save-array', methods=['POST'])
def save_array():
    data = request.get_json()
    files = data['files']
    user_id = session.get('user_id')
    answers = json.dumps(files, indent=4)
    session['answers'] = answers
    print(type(answers))

    db_config = {
        'user': 'root',
        'password': 'root123',
        'host': 'localhost',
        'database': 'masterdb'
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    user = cursor.fetchone()
    user = User(*user)

    try:
        cursor.execute("INSERT INTO exam_results (id, first_name, last_name,  exam_results) VALUES (%s,%s, %s, %s)",
                       (user_id, user.first_name, user.last_name, answers))
        for file_name in files:
            cursor.execute("INSERT INTO test_table (image, result) VALUES (%s, %s)", (file_name[0], file_name[1]))

        conn.commit()

    except Exception as e:
        print(e)
    return jsonify({'message': 'Array saved successfully'}), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        result, predict_label = process_image(file_path, filename)
        if predict_label == 'non':
            return jsonify({
                'original': url_for('static', filename=f'images/{filename}_original.jpg'),
                'segmented': url_for('static', filename=f'images/{filename}_segmented.jpg'),
                'binary_thresh': url_for('static', filename=f'images/{filename}_binary_thresh.jpg'),
                'detected': url_for('static', filename=f'images/{filename}_detected.jpg'),
                'accuracy': f'There is no certainty in predictions ... ' if result != 0 else 'There is not enough valid detection...'
            })
        else:
            return jsonify({
                'original': url_for('static', filename=f'images/{filename}_original.jpg'),
                'segmented': url_for('static', filename=f'images/{filename}_segmented.jpg'),
                'binary_thresh': url_for('static', filename=f'images/{filename}_binary_thresh.jpg'),
                'detected': url_for('static', filename=f'images/{filename}_detected.jpg'),
                'accuracy': f'{predict_label} with {result}% of certainty!' if result != 0 else 'There is not enough valid detection...'
            })
    return jsonify({'error': 'Invalid file type'})


if __name__ == '__main__':
    app.run(debug=True)
