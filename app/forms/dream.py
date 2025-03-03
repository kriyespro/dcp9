from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date

class DreamForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=500, message='Description must be between 10 and 500 characters')
    ])
    target_date = DateField('Target Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Submit')

class MilestoneForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=255, message='Title must be less than 255 characters')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    target_date = DateField('Target Date', validators=[Optional()])
    submit = SubmitField('Save Milestone')

class GoalForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=255, message='Title must be less than 255 characters')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    target_date = DateField('Target Date', validators=[Optional()])
    submit = SubmitField('Save Goal')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=255, message='Title must be less than 255 characters')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateField('Due Date', validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ])
    status = SelectField('Status', choices=[
        ('Todo', 'Todo'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Done', 'Done')
    ])
    progress = FloatField('Progress (%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Progress must be between 0 and 100')
    ])
    assignee_id = SelectField('Assign To', coerce=int)
    submit = SubmitField('Save Task')

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        from app.models.user import User
        # Populate assignee choices
        users = User.query.all()
        self.assignee_id.choices = [(user.id, user.get_full_name()) for user in users] 