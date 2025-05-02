from flask import Flask, render_template, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# --- Загрузка переменных окружения ---
load_dotenv()

ENV = os.getenv("FLASK_ENV", "auto")
if ENV == "auto":
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

load_dotenv(dotenv_path=env_file)
print(f"Загружен конфиг из: {env_file}")

# --- Настройка приложения ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_key')
app.debug = os.getenv('DEBUG', 'False').lower() in ['true', '1']

db = SQLAlchemy(app)

# --- Модели ---

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    status = db.relationship('Status', backref='tasks')
    task_order = db.Column(db.Integer, default=0)  # Новое поле


# --- Роуты ---

@app.route('/')
def home():
    return redirect(url_for('board'))


@app.route('/board')
def board():
    tasks = Task.query.order_by(Task.task_order.asc()).all()
    statuses = Status.query.all()

    task_counts = {}
    for status in statuses:
        task_counts[status.id] = Task.query.filter_by(status_id=status.id).count()

    return render_template('board.html', tasks=tasks, statuses=statuses, task_counts=task_counts)


@app.route('/tasks')
def list_tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)


@app.route('/wiki')
def wiki():
    return render_template('wiki.html')


@app.route('/labels')
def labels():
    return render_template('labels.html')


@app.route('/task/add', methods=['GET', 'POST'])
def add_task():
    statuses = Status.query.all()
    if not statuses:
        return redirect(url_for('board'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status_id = request.form.get('status_id')

        new_task = Task(title=title, description=description, status_id=status_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('board'))

    return render_template('add_task.html', statuses=statuses)


@app.route('/task/<int:task_id>')
def task_details(task_id):
    task = Task.query.get_or_404(task_id)
    statuses = Status.query.all()
    return render_template('task_details.html', task=task, statuses=statuses)


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    statuses = Status.query.all()

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status_id = request.form.get('status_id')

        db.session.commit()
        return redirect(url_for('task_details', task_id=task.id))

    return render_template('edit_task.html', task=task, statuses=statuses)


@app.route('/api/update/<int:task_id>/<int:status_id>')
def api_update_status(task_id, status_id):
    task = Task.query.get_or_404(task_id)
    target_status = Status.query.get_or_404(status_id)

    task.status_id = target_status.id
    db.session.commit()

    # Обновляем порядок у всех задач в старом статусе
    old_tasks = Task.query.filter(Task.status_id == target_status.id).order_by(Task.task_order.asc()).all()
    for i, t in enumerate(old_tasks):
        t.task_order = i
    db.session.commit()

    template = """
    <div class="card mb-2"
         id="{{ task.id }}"
         draggable="true"
         ondragstart="drag(event)"
         style="cursor: grab;">
        <div class="card-body p-2">
            <strong>{{ task.title }}</strong>
            {% if task.description %}
                <p class="text-muted small">{{ task.description }}</p>
            {% endif %}
        </div>
    </div>
    """

    html = render_template_string(template, task=task)
    return html


@app.route('/api/order', methods=['POST'])
def api_update_order():
    data = request.get_json()
    for item in data['tasks']:
        task = Task.query.get(item['id'])
        if task:
            task.task_order = item['order']
    db.session.commit()
    return '', 204


@app.route('/status/add', methods=['GET', 'POST'])
def add_status():
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not Status.query.filter_by(name=name).first():
            db.session.add(Status(name=name))
            db.session.commit()
        return redirect(url_for('board'))

    return render_template('add_status.html')


# --- Запуск приложения ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Добавляем дефолтные статусы, если их нет
        if Status.query.count() == 0:
            default_statuses = [
                Status(name="Open"),
                Status(name="Doing"),
                Status(name="To Test"),
                Status(name="Testing"),
                Status(name="Closed")
            ]
            db.session.add_all(default_statuses)
            db.session.commit()

    app.run(debug=True)
