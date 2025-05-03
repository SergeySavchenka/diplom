from flask import Flask, render_template, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, date
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


# Таблица связи многие-ко-многим
task_label = db.Table('task_label',
                      db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
                      db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True)
                      )

task_link = db.Table('task_link',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('linked_task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    status = db.relationship('Status', backref='tasks')
    task_order = db.Column(db.Integer, default=0)
    labels = db.relationship('Label', secondary=task_label, backref='tasks')

    # Новые поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    weight = db.Column(db.Integer)
    due_date = db.Column(db.Date)
    confidentiality = db.Column(db.String(50))

    activities = db.relationship('Activity', backref='task', lazy='dynamic')

    # Связанные задачи (many-to-many)
    linked_tasks = db.relationship(
        'Task',
        secondary=task_link,
        primaryjoin=(task_link.c.task_id == id),
        secondaryjoin=(task_link.c.linked_task_id == id),
        backref='tasks'
    )


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), default="#888888")  # Цвет метки


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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


@app.route('/task/add', methods=['GET', 'POST'])
def add_task():
    statuses = Status.query.all()
    labels = Label.query.all()
    if not statuses:
        return redirect(url_for('board'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status_id = request.form.get('status_id')

        new_task = Task(title=title, description=description, status_id=status_id)

        # Привязываем метки
        label_ids = request.form.getlist('label_ids')
        if label_ids:
            selected_labels = Label.query.filter(Label.id.in_(label_ids)).all()
            new_task.labels.extend(selected_labels)

        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('board'))

    return render_template('add_task.html', statuses=statuses, all_labels=Label.query.all())


@app.route('/task/<int:task_id>')
def task_details(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task_details.html', task=task)


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    statuses = Status.query.all()
    labels = Label.query.all()

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status_id = request.form.get('status_id')

        # Обновляем метки
        label_ids = request.form.getlist('label_ids')
        task.labels = Label.query.filter(Label.id.in_(label_ids)).all()

        db.session.commit()
        return redirect(url_for('task_details', task_id=task.id))

    return render_template('edit_task.html', task=task, statuses=statuses, all_labels=labels)


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


@app.route('/labels')
def list_labels():
    labels = Label.query.all()
    return render_template('labels.html', labels=labels)


@app.route('/label/add', methods=['POST'])
def add_label():
    name = request.form.get('name')
    description = request.form.get('description')
    color = request.form.get('color', '#888888')

    if name and not Label.query.filter_by(name=name).first():
        new_label = Label(name=name, description=description, color=color)
        db.session.add(new_label)
        db.session.commit()

    return redirect(url_for('list_labels'))


@app.route('/label/<int:label_id>/edit', methods=['GET', 'POST'])
def edit_label(label_id):
    label = Label.query.get_or_404(label_id)

    if request.method == 'POST':
        label.name = request.form.get('name')
        label.description = request.form.get('description')
        label.color = request.form.get('color', label.color)
        db.session.commit()
        return redirect(url_for('list_labels'))

    return render_template('edit_label.html', label=label)


@app.route('/label/<int:label_id>/delete', methods=['POST'])
def delete_label(label_id):
    label = Label.query.get_or_404(label_id)
    db.session.delete(label)
    db.session.commit()
    return redirect(url_for('list_labels'))


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
