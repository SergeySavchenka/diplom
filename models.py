from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Таблица связи многие-ко-многим для меток задачи
task_label = db.Table('task_label',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True)
)

# Таблица связи многие-ко-многим для связей между задачами
task_link = db.Table('task_link',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('linked_task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

# Таблица связи "назначенный"
task_assigned = db.Table('task_assigned',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
)

# Таблица связи "участники задачи"
task_participant = db.Table('task_participant',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
)


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'), nullable=False)


class Label(db.Model):
    __tablename__ = 'label'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), default="#888888")


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), nullable=False)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    task_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    weight = db.Column(db.Integer)
    due_date = db.Column(db.Date)
    confidentiality = db.Column(db.String(50))

    # Отношения
    status = db.relationship('Status', backref='tasks')
    labels = db.relationship('Label', secondary=task_label, backref='tasks')
    activities = db.relationship('Activity', backref='task', lazy='dynamic')

    # Назначенный пользователь
    assigned_users = db.relationship('User', secondary=task_assigned, backref=db.backref('assigned_tasks', lazy='dynamic'))

    # Участники задачи
    participants = db.relationship('User', secondary=task_participant, backref=db.backref('participated_tasks', lazy='dynamic'))

    # Связанные задачи
    linked_tasks = db.relationship(
        'Task',
        secondary=task_link,
        primaryjoin=id == task_link.c.task_id,
        secondaryjoin=id == task_link.c.linked_task_id,
        backref='linked_to'
    )


class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    action_type = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Task', backref=db.backref('comments', lazy='dynamic'))


class Attachment(db.Model):
    __tablename__ = 'attachment'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary(length=(1 << 24)), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Task', backref=db.backref('attachments', lazy='dynamic'))


def log_task_activity(task_id, action_type, description):
    activity = Activity(
        task_id=task_id,
        action_type=action_type,
        description=description
    )
    db.session.add(activity)
    db.session.commit()
