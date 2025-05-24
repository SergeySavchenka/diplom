from flask import Flask, render_template, request, redirect, url_for, render_template_string, jsonify
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
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'), nullable=False)


# Таблицы связи многие-ко-многим
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    weight = db.Column(db.Integer)
    due_date = db.Column(db.Date)
    confidentiality = db.Column(db.String(50))

    # Связанные метки
    labels = db.relationship('Label', secondary=task_label, backref='tasks')

    # Связь с активностью
    activities = db.relationship('Activity', backref='task', lazy='dynamic')


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), default="#888888")  # Цвет метки


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=True)  # тип действия: created, status_changed и т.д.
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def log_task_activity(task_id, action_type, description):
    activity = Activity(
        task_id=task_id,
        action_type=action_type,
        description=description
    )
    db.session.add(activity)
    db.session.commit()


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

    return render_template('board.html', tasks=tasks, statuses=statuses, task_counts=task_counts, active_page='board')


@app.route('/tasks')
def tasks():
    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks, active_page='tasks')


@app.route('/wiki')
def wiki():
    return render_template('wiki.html', active_page='wiki')


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

        label_ids = request.form.getlist('label_ids')
        if label_ids:
            selected_labels = Label.query.filter(Label.id.in_(label_ids)).all()
            new_task.labels.extend(selected_labels)

        db.session.add(new_task)
        db.session.commit()

        log_task_activity(
            new_task.id,
            'created',
            f'Задача "{new_task.title}" создана'
        )

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

    old_title = task.title
    old_description = task.description
    old_status_name = task.status.name if task.status else '—'

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_description = request.form.get('description')
        new_status_id = int(request.form.get('status_id') or task.status_id)

        # Обновляем поля
        task.title = new_title
        task.description = new_description
        task.status_id = new_status_id

        # Обновляем метки
        label_ids = list(map(int, request.form.getlist('label_ids')))
        old_labels = [lb.name for lb in task.labels]
        new_labels = Label.query.filter(Label.id.in_(label_ids)).all()
        task.labels = new_labels

        added_labels = set(lb.name for lb in new_labels) - set(old_labels)
        removed_labels = set(old_labels) - set(lb.name for lb in new_labels)

        db.session.commit()

        # Логируем изменения
        if old_title != new_title:
            log_task_activity(task.id, 'title_updated', f'Название изменено с "{old_title}" на "{new_title}"')

        if old_description != new_description:
            log_task_activity(task.id, 'description_updated', 'Описание изменено')

        if task.status.name != old_status_name:
            log_task_activity(task.id, 'status_updated', f'Статус изменён на "{task.status.name}"')

        for label in added_labels:
            log_task_activity(task.id, 'label_added', f'Метка "{label}" добавлена')

        for label in removed_labels:
            log_task_activity(task.id, 'label_removed', f'Метка "{label}" удалена')

        return redirect(url_for('task_details', task_id=task.id))

    return render_template('edit_task.html', task=task, statuses=statuses, all_labels=labels)


@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def api_update_status(task_id):
    data = request.get_json()
    status_id = data.get('status_id')

    task = Task.query.get_or_404(task_id)
    target_status = Status.query.get_or_404(status_id)

    old_status_name = task.status.name
    new_status_name = target_status.name

    # Удаляем старую метку статуса
    old_status_labels = [label.id for label in Label.query.join(Status).filter(Label.id == Status.label_id)]
    task.labels = [label for label in task.labels if label.id not in old_status_labels]

    # Добавляем новую метку статуса
    new_label = Label.query.get(target_status.label_id)
    if new_label and new_label not in task.labels:
        task.labels.append(new_label)

    # Обновляем статус
    task.status_id = target_status.id
    db.session.commit()

    # Логируем изменение статуса
    log_task_activity(
        task_id,
        'status_changed',
        f'Статус изменён с "{old_status_name}" на "{new_status_name}"'
    )

    return jsonify({
        'id': task.id,
        'title': task.title,
        'url': url_for('task_details', task_id=task.id, _external=True),
        'labels': [{'name': lb.name, 'color': lb.color} for lb in task.labels]
    })


@app.route('/api/order', methods=['POST'])
def api_update_order():
    data = request.get_json()
    for item in data['tasks']:
        task = Task.query.get(item['id'])
        if task:
            task.task_order = item['order']
    db.session.commit()
    return '', 204


@app.route('/labels')
def list_labels():
    labels = Label.query.all()
    return render_template('labels.html', labels=labels, active_page='labels')


@app.route('/label/add', methods=['GET', 'POST'])
def add_label():
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#888888')
        description = request.form.get('description')

        if name and not Label.query.filter_by(name=name).first():
            new_label = Label(name=name, description=description, color=color)
            db.session.add(new_label)
            db.session.commit()
            return redirect(url_for('list_labels'))

    return render_template('add_label.html')


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
                Status(name="Open", label_id=1),
                Status(name="Doing", label_id=2),
                Status(name="To Test", label_id=3),
                Status(name="Testing", label_id=4),
                Status(name="Closed", label_id=5)
            ]
            db.session.add_all(default_statuses)
            db.session.commit()

    app.run(debug=True)
