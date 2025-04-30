from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# ---- Определяем среду ----------------------
# Можно задать через переменную окружения
ENV = os.getenv("FLASK_ENV", "auto")

if ENV == "auto":
    # Попробуем определить по наличию MySQL
    try:
        import pymysql
        mysql_available = True
    except ImportError:
        mysql_available = False

    if mysql_available:
        env_file = "example_configs/.env.local"
    else:
        env_file = "example_configs/.env.work"
else:
    env_file = f".env.{ENV}"

# Загружаем указанный .env файл
load_dotenv(dotenv_path=env_file)

print(f"Загружен конфиг: {env_file}")
# --------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.debug = os.getenv('DEBUG', 'False').lower() in ['true', '1']

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='new')  # new, in_progress, testing, done


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_task = Task(title=title, description=description)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))

    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/update/<int:task_id>/<status>')
def update_status(task_id, status):
    valid_statuses = ['new', 'in_progress', 'testing', 'done']
    if status not in valid_statuses:
        return "Invalid status", 400

    task = Task.query.get(task_id)
    task.status = status
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/config')
def show_config():
    return {
        "current_env_file": env_file,
        "database_url": app.config['SQLALCHEMY_DATABASE_URI'],
        "debug": app.debug
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
