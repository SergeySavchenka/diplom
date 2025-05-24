from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from dotenv import load_dotenv
import os
from markupsafe import Markup
import markdown
from werkzeug.utils import secure_filename
import io

from models import db, Task, Label, Status, Comment, Attachment, task_link, log_task_activity

load_dotenv(dotenv_path="example_configs/.env.local")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_key')
app.debug = os.getenv('DEBUG', 'False').lower() in ['true', '1']


db.init_app(app)


@app.template_filter()
def markdown_filter(text):
    if not text:
        return ''
    return Markup(markdown.markdown(text, extensions=['fenced_code', 'codehilite']))


@app.route('/')
def home():
    return redirect(url_for('board'))


@app.route('/board')
def board():
    task_list = Task.query.order_by(Task.task_order.asc()).all()
    statuses = Status.query.all()
    task_counts = {}
    for status in statuses:
        task_counts[status.id] = Task.query.filter_by(status_id=status.id).count()
    return render_template('board.html', tasks=task_list, statuses=statuses, task_counts=task_counts, active_page='board')


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
        status_id = 1

        new_task = Task(
            title=title,
            description=description,
            status_id=status_id,
            weight=None,
            due_date=None,
            confidentiality=request.form.get('confidentiality')
        )

        weight = request.form.get('weight')
        if weight:
            new_task.weight = request.form.get('weight')

        due_date_str = request.form.get('due_date')
        if due_date_str:
            from datetime import datetime
            try:
                new_task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Неверный формат даты", "danger")
                return render_template('add_task.html', statuses=statuses, all_labels=labels)

        label_ids = request.form.getlist('labels')
        if not label_ids:
            label_ids = ['13']
        if label_ids:
            selected_labels = Label.query.filter(Label.id.in_(map(int, label_ids))).all()
            new_task.labels.extend(selected_labels)

        assignee_id = request.form.get('assignee')
        new_task.assignee_id = int(assignee_id) if assignee_id else None

        db.session.add(new_task)
        db.session.commit()

        log_task_activity(new_task.id, 'Создание', f'Задача "{new_task.title}" создана')

        return redirect(url_for('board'))

    return render_template('add_task.html', statuses=statuses, all_labels=Label.query.all())


@app.route('/task/<int:task_id>/comment', methods=['POST'])
def add_comment(task_id):
    content = request.form.get('content')
    if not content:
        flash("Комментарий не может быть пустым", "danger")
        return redirect(url_for('task_details', task_id=task_id))

    new_comment = Comment(
        content=content,
        task_id=task_id,
    )
    db.session.add(new_comment)
    db.session.commit()

    flash("Комментарий добавлен", "success")
    return redirect(url_for('task_details', task_id=task_id))


@app.route('/task/<int:task_id>')
def task_details(task_id):
    task = Task.query.get_or_404(task_id)
    all_tasks = Task.query.all()

    direct_links = db.session.query(task_link.c.linked_task_id).filter(task_link.c.task_id == task_id).all()
    reverse_links = db.session.query(task_link.c.task_id).filter(task_link.c.linked_task_id == task_id).all()

    related_ids = set(r[0] for r in direct_links + reverse_links)
    related_tasks = Task.query.filter(Task.id.in_(related_ids)).all()

    statuses = Status.query.all()
    return render_template('task_details.html', task=task, related_tasks=related_tasks, all_tasks=all_tasks,
                           statuses=statuses)


@app.route('/task/<int:task_id>/link/add', methods=['POST'])
def add_task_link(task_id):
    linked_task_id = request.form.get('linked_task_id')
    return_to = request.form.get('return_to', 'edit_task')  # <-- Читаем откуда пришли

    if not linked_task_id:
        flash("Не выбрана задача для связи", "danger")
        return redirect(url_for(return_to, task_id=task_id))

    linked_task_id = int(linked_task_id)

    if task_id == linked_task_id:
        flash("Задача не может быть связана с самой собой", "danger")
        return redirect(url_for(return_to, task_id=task_id))

    existing = db.session.query(task_link).filter(
        db.or_(
            db.and_(task_link.c.task_id == task_id, task_link.c.linked_task_id == linked_task_id),
            db.and_(task_link.c.task_id == linked_task_id, task_link.c.linked_task_id == task_id)
        )
    ).first()

    if existing:
        flash("Такая связь уже существует", "warning")
        return redirect(url_for(return_to, task_id=task_id))

    db.session.execute(task_link.insert().values(task_id=task_id, linked_task_id=linked_task_id))
    db.session.execute(task_link.insert().values(task_id=linked_task_id, linked_task_id=task_id))
    db.session.commit()

    flash("Связь успешно создана", "success")
    return redirect(url_for(return_to, task_id=task_id))


@app.route('/task/<int:task_id>/link/<int:linked_task_id>/delete', methods=['POST'])
def delete_task_link(task_id, linked_task_id):
    return_to = request.form.get('return_to', 'task_details')

    db.session.execute(
        task_link.delete().where(
            db.or_(
                db.and_(task_link.c.task_id == task_id, task_link.c.linked_task_id == linked_task_id),
                db.and_(task_link.c.task_id == linked_task_id, task_link.c.linked_task_id == task_id)
            )
        )
    )
    db.session.commit()

    flash("Связь удалена", "success")
    return redirect(url_for(return_to, task_id=task_id))


@app.route('/task/<int:task_id>/create_bug', methods=['POST'])
def create_linked_bug_task(task_id):
    title = request.form.get('title')
    description = request.form.get('description')
    label_ids = ['2', '13']
    print(label_ids, 'aaa')
    status_id = [1]
    print(status_id)

    if not title:
        flash("Задача должна иметь название", "danger")
        return redirect(url_for('task_details', task_id=task_id))

    new_task = Task(
        title=title,
        description=description,
        status_id=status_id
    )

    labels = Label.query.filter(Label.id.in_(label_ids)).all()
    new_task.labels.extend(labels)

    db.session.add(new_task)
    db.session.flush()

    db.session.execute(task_link.insert().values(task_id=new_task.id, linked_task_id=task_id))
    db.session.execute(task_link.insert().values(task_id=task_id, linked_task_id=new_task.id))

    db.session.commit()

    log_task_activity(new_task.id, 'Создание', f'Баг-задача "{new_task.title}" создана')
    log_task_activity(new_task.id, 'Добавление метки', 'Метка "Bug" добавлена')

    flash("Баг-задача успешно создана и привязана к текущей задаче", "success")

    return redirect(url_for('task_details', task_id=new_task.id))


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    statuses = Status.query.all()
    labels = Label.query.all()
    all_tasks = Task.query.all()

    direct_links = db.session.query(task_link.c.linked_task_id).filter(task_link.c.task_id == task_id).all()
    reverse_links = db.session.query(task_link.c.task_id).filter(task_link.c.linked_task_id == task_id).all()
    related_ids = set(r[0] for r in direct_links + reverse_links)
    related_tasks = Task.query.filter(Task.id.in_(related_ids)).all()

    old_title = task.title
    old_description = task.description
    old_weight = task.weight
    old_due_date = task.due_date

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_description = request.form.get('description')

        task.title = new_title
        task.description = new_description

        label_ids = list(map(int, request.form.getlist('labels')))
        old_labels = [lb.name for lb in task.labels]
        new_labels = Label.query.filter(Label.id.in_(label_ids)).all()
        task.labels = new_labels

        added_labels = set(lb.name for lb in new_labels) - set(old_labels)
        removed_labels = set(old_labels) - set(lb.name for lb in new_labels)

        weight_str = request.form.get('weight')
        task.weight = int(weight_str) if weight_str and weight_str.isdigit() else None

        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                from datetime import datetime
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Неверный формат даты", "danger")
        else:
            task.due_date = None

        db.session.commit()

        if old_title != new_title:
            log_task_activity(task.id, 'Изменение заголовка', f'Название изменено с "{old_title}" на "{new_title}"')
        if old_description != new_description:
            log_task_activity(task.id, 'Изменение описание', 'Описание изменено')
        if old_weight != task.weight:
            log_task_activity(task.id, 'Изменение веса', f'Вес изменён на "{task.weight}"')
        if old_due_date != task.due_date:
            due_date_log = task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не указана'
            log_task_activity(task.id, 'Изменение даты', f'Дата выполнения изменена на {due_date_log}')

        for label in added_labels:
            log_task_activity(task.id, 'Добавление метки', f'Метка "{label}" добавлена')
        for label in removed_labels:
            log_task_activity(task.id, 'Удаление метки', f'Метка "{label}" удалена')

        return redirect(url_for('task_details', task_id=task.id))

    return render_template(
        'edit_task.html',
        task=task,
        statuses=statuses,
        all_labels=labels,
        all_tasks=all_tasks,
        related_tasks=related_tasks
    )


@app.route('/attachment/<int:attachment_id>/delete', methods=['POST'])
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    task_id = attachment.task_id
    db.session.delete(attachment)
    db.session.commit()
    log_task_activity(task_id, 'Удаление вложения', f'Файл "{attachment.filename}" удален')
    flash("Файл удален", "success")
    return redirect(url_for('task_details', task_id=task_id))


@app.route('/attachment/<int:attachment_id>')
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    return send_file(
        io.BytesIO(attachment.data),
        as_attachment=True,
        download_name=attachment.filename
    )


@app.route('/task/<int:task_id>/upload', methods=['POST'])
def upload_attachment(task_id):
    task = Task.query.get_or_404(task_id)

    if 'file' not in request.files:
        flash("Файл не выбран", "danger")
        return redirect(url_for('task_details', task_id=task_id))

    file = request.files['file']
    if file.filename == '':
        flash("Файл не выбран", "danger")
        return redirect(url_for('task_details', task_id=task_id))

    if file:
        filename = secure_filename(file.filename)
        data = file.read()

        attachment = Attachment(
            filename=filename,
            data=data,
            content_type=file.content_type,
            task_id=task.id
        )
        db.session.add(attachment)
        db.session.commit()

        log_task_activity(task.id, 'Добавление вложения', f'Файл "{filename}" загружен')
        flash("Файл успешно загружен", "success")

    return redirect(url_for('task_details', task_id=task_id))


@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def api_update_status(task_id):
    data = request.get_json()
    status_id = data.get('status_id')
    task = Task.query.get_or_404(task_id)
    target_status = Status.query.get_or_404(status_id)
    old_status_name = task.status.name
    new_status_name = target_status.name
    old_status_labels = [label.id for label in Label.query.join(Status).filter(Label.id == Status.label_id)]
    task.labels = [label for label in task.labels if label.id not in old_status_labels]
    new_label = Label.query.get(target_status.label_id)
    if new_label and new_label not in task.labels:
        task.labels.append(new_label)
    task.status_id = target_status.id
    db.session.commit()
    log_task_activity(
        task_id,
        'Изменение статуса',
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


if __name__ == '__main__':
    app.run(debug=True)
