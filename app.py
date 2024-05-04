from flask import Flask, render_template, request, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
import shutil
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['OUTPUT_FOLDER'] = 'static/output/'
app.config['SECRET_KEY'] = 'your_secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def get_id(self):
        return self.username

users = {}

@login_manager.user_loader
def load_user(username):
    return users.get(username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = load_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'Username already exists'
        new_user = User(username, password)
        users[username] = new_user
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    elif users:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('signup'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/image-restoration', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        try:
            file = request.files['image']
            filename = secure_filename(file.filename)
            temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_file_path)

            include_scratches = request.form.get('with_scratch', False)
            is_high_resolution = request.form.get('HR', False)

            original_image_path, restored_image_path = run_restoration_script(temp_file_path, include_scratches, is_high_resolution)

            return jsonify({
                'originalImagePath': original_image_path,
                'restoredImagePath': restored_image_path
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return render_template('index.html')

def run_restoration_script(input_file_path, include_scratches, is_high_resolution):
    # Create a temporary input folder
    input_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_input')
    os.makedirs(input_folder, exist_ok=True)

    # Copy the uploaded file to the temporary input folder
    new_file_path = os.path.join(input_folder, os.path.basename(input_file_path))
    shutil.copy(input_file_path, new_file_path)

    # Call the run.py script with the appropriate arguments
    gpu = '0'  # Replace with the desired GPU ID
    arguments = ['python', 'image_restoration/run_flask.py', '--input_folder', input_folder, '--output_folder', app.config['OUTPUT_FOLDER'], '--GPU', gpu]

    if include_scratches:
        arguments.append('--with_scratch')

    if is_high_resolution:
        arguments.append('--HR')

    subprocess.run(arguments)

    # Get the original and restored image paths
    original_image_path = new_file_path
    restored_image_path = os.path.join(
    app.config['OUTPUT_FOLDER'], 
    "super_resolution_output",  # Add the folder here
    f"{os.path.splitext(os.path.basename(input_file_path))[0]}.png"
)


    return original_image_path, restored_image_path

if __name__ == '__main__':
    app.run(debug=True) 