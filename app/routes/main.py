from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Dream, Milestone, Goal, Task, db, User, Role
from app.forms.milestone import MilestoneForm
from app.forms.dream import DreamForm
from app.forms.goal import GoalForm
from app.forms.task import TaskForm
from datetime import datetime, timedelta
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    dreams = Dream.query.filter_by(creator_id=current_user.id).all()
    total_dreams = len(dreams)
    total_milestones = Milestone.query.filter_by(creator_id=current_user.id).count()
    total_goals = Goal.query.filter_by(creator_id=current_user.id).count()
    total_tasks = Task.query.filter_by(creator_id=current_user.id).count()
    
    # Add edit_url to each dream
    for dream in dreams:
        dream.edit_url = url_for('main.edit_dream', dream_id=dream.id)
        dream.progress = calculate_dream_progress(dream)
    
    stats = get_time_based_stats()
    
    return render_template('main/dashboard.html',
                         dreams=dreams,
                         total_dreams=total_dreams,
                         total_milestones=total_milestones,
                         total_goals=total_goals,
                         total_tasks=total_tasks,
                         **stats)

def calculate_dream_progress(dream):
    """Calculate the progress of a dream based on its milestones."""
    milestones = Milestone.query.filter_by(dream_id=dream.id).all()
    if not milestones:
        return 0
    
    total_progress = sum(milestone.progress or 0 for milestone in milestones)
    return round(total_progress / len(milestones))

def calculate_milestone_progress(milestone):
    """Calculate the progress of a milestone based on its goals."""
    goals = Goal.query.filter_by(milestone_id=milestone.id).all()
    if not goals:
        return 0
    
    total_progress = sum(goal.progress or 0 for goal in goals)
    return round(total_progress / len(goals))

def calculate_goal_progress(goal):
    """Calculate the progress of a goal based on its tasks."""
    tasks = Task.query.filter_by(goal_id=goal.id).all()
    if not tasks:
        return 0
    
    total_progress = sum(task.progress or 0 for task in tasks)
    return round(total_progress / len(tasks))

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@main.route('/dreams/create', methods=['GET', 'POST'])
@login_required
def create_dream():
    form = DreamForm()
    if form.validate_on_submit():
        dream = Dream(
            title=form.title.data,
            description=form.description.data,
            target_date=form.target_date.data,
            creator_id=current_user.id
        )
        db.session.add(dream)
        db.session.commit()
        
        flash(f'Dream created successfully! ID:{dream.id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/dream/create.html', form=form)

@main.route('/dreams/<int:dream_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dream(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id:
        flash('You do not have permission to edit this dream.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = DreamForm(obj=dream)
    if form.validate_on_submit():
        dream.title = form.title.data
        dream.description = form.description.data
        dream.target_date = form.target_date.data
        db.session.commit()
        
        flash('Dream updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/dream/edit.html', form=form, dream=dream)

@main.route('/dreams/<int:dream_id>/delete', methods=['POST'])
@login_required
def delete_dream(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id:
        flash('You do not have permission to delete this dream.', 'error')
        return redirect(url_for('main.dashboard'))
    
    dream.soft_delete()
    flash('Dream moved to trash.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/milestones/create/<int:dream_id>', methods=['GET', 'POST'])
@login_required
def create_milestone(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id:
        flash('You do not have permission to create milestones for this dream.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = MilestoneForm()
    if form.validate_on_submit():
        milestone = Milestone(
            title=form.title.data,
            description=form.description.data,
            target_date=form.target_date.data,
            dream_id=dream_id,
            creator_id=current_user.id
        )
        db.session.add(milestone)
        db.session.commit()
        
        flash(f'Milestone created successfully! ID:{milestone.id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/milestone/create.html', form=form, dream=dream)

@main.route('/milestones/<int:milestone_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.creator_id != current_user.id:
        flash('You do not have permission to edit this milestone.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = MilestoneForm(obj=milestone)
    if form.validate_on_submit():
        milestone.title = form.title.data
        milestone.description = form.description.data
        milestone.target_date = form.target_date.data
        milestone.progress = calculate_milestone_progress(milestone)
        db.session.commit()
        
        flash('Milestone updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/milestone/edit.html', form=form, milestone=milestone)

@main.route('/milestones/<int:milestone_id>/delete', methods=['POST'])
@login_required
def delete_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.creator_id != current_user.id:
        flash('You do not have permission to delete this milestone.', 'error')
        return redirect(url_for('main.dashboard'))
    
    milestone.soft_delete()
    flash('Milestone moved to trash.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/goals/create/<int:milestone_id>', methods=['GET', 'POST'])
@login_required
def create_goal(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.creator_id != current_user.id:
        flash('You do not have permission to create goals for this milestone.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            title=form.title.data,
            description=form.description.data,
            target_date=form.target_date.data,
            milestone_id=milestone_id,
            creator_id=current_user.id,
            progress=0
        )
        db.session.add(goal)
        db.session.commit()
        
        flash(f'Goal created successfully! ID:{goal.id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/goal/create.html', form=form, milestone=milestone)

@main.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.creator_id != current_user.id:
        flash('You do not have permission to edit this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_date = form.target_date.data
        goal.progress = calculate_goal_progress(goal)
        db.session.commit()
        
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/goal/edit.html', form=form, goal=goal)

@main.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.creator_id != current_user.id:
        flash('You do not have permission to delete this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    goal.soft_delete()
    flash('Goal moved to trash.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/tasks/create/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def create_task(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.creator_id != current_user.id:
        flash('You do not have permission to create tasks for this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            assignee_id=form.assignee_id.data if form.assignee_id.data else None,
            goal_id=goal_id,
            creator_id=current_user.id,
            status=form.status.data,
            progress=0
        )
        db.session.add(task)
        db.session.commit()
        
        flash(f'Task created successfully! ID:{task.id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/task/create.html', form=form, goal=goal)

@main.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id and task.assignee_id != current_user.id:
        flash('You do not have permission to edit this task.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        task.assignee_id = form.assignee_id.data if form.assignee_id.data else None
        
        # Update progress based on status and trigger hierarchy updates
        task.update_progress()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/task/edit.html', form=form, task=task)

@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id:
        flash('You do not have permission to delete this task.', 'error')
        return redirect(url_for('main.dashboard'))
    
    task.soft_delete()
    flash('Task moved to trash.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    users = User.query.all()
    return render_template('main/admin/users.html', users=users)

@main.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def admin_user_new():
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        role_id = request.form.get('role')

        if not all([username, email, first_name, last_name, password, password_confirm, role_id]):
            flash('All fields are required.', 'error')
            return redirect(url_for('main.admin_user_new'))

        if password != password_confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('main.admin_user_new'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('main.admin_user_new'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.admin_user_new'))

        role = Role.query.get(role_id)
        if not role:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('main.admin_user_new'))

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('User created successfully.', 'success')
        return redirect(url_for('main.admin_users'))

    roles = Role.query.all()
    return render_template('main/admin/user_edit.html', user=None, roles=roles)

@main.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_user_edit(user_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role_id = request.form.get('role')

        if not all([username, email, first_name, last_name, role_id]):
            flash('All fields are required.', 'error')
            return redirect(url_for('main.admin_user_edit', user_id=user_id))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists.', 'error')
            return redirect(url_for('main.admin_user_edit', user_id=user_id))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Email already registered.', 'error')
            return redirect(url_for('main.admin_user_edit', user_id=user_id))

        role = Role.query.get(role_id)
        if not role:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('main.admin_user_edit', user_id=user_id))

        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        db.session.commit()

        flash('User updated successfully.', 'success')
        return redirect(url_for('main.admin_users'))

    roles = Role.query.all()
    return render_template('main/admin/user_edit.html', user=user, roles=roles)

@main.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def admin_user_toggle(user_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    
    if user.is_admin():
        flash('Cannot deactivate admin users.', 'error')
        return redirect(url_for('main.admin_users'))

    user.is_active = not user.is_active
    db.session.commit()

    flash(f'User {"activated" if user.is_active else "deactivated"} successfully.', 'success')
    return redirect(url_for('main.admin_users'))

@main.route('/admin/users/<int:user_id>/change-password', methods=['POST'])
@login_required
def admin_user_change_password(user_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not new_password or not confirm_password:
        flash('Both password fields are required.', 'error')
        return redirect(url_for('main.admin_users'))

    if new_password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('main.admin_users'))

    user.set_password(new_password)
    db.session.commit()

    flash('Password updated successfully.', 'success')
    return redirect(url_for('main.admin_users'))

@main.route('/trash')
@login_required
def trash():
    """Show all soft-deleted items that can be restored."""
    deleted_dreams = Dream.query.filter(
        Dream.deleted_at.isnot(None),
        Dream.creator_id == current_user.id
    ).all()
    
    deleted_milestones = Milestone.query.filter(
        Milestone.deleted_at.isnot(None),
        Milestone.creator_id == current_user.id
    ).all()
    
    deleted_goals = Goal.query.filter(
        Goal.deleted_at.isnot(None),
        Goal.creator_id == current_user.id
    ).all()
    
    deleted_tasks = Task.query.filter(
        Task.deleted_at.isnot(None),
        db.or_(Task.creator_id == current_user.id, Task.assignee_id == current_user.id)
    ).all()
    
    return render_template('main/trash.html',
                         deleted_dreams=deleted_dreams,
                         deleted_milestones=deleted_milestones,
                         deleted_goals=deleted_goals,
                         deleted_tasks=deleted_tasks)

@main.route('/restore/<string:item_type>/<int:item_id>', methods=['POST'])
@login_required
def restore_item(item_type, item_id):
    """Restore a soft-deleted item."""
    model_map = {
        'dream': Dream,
        'milestone': Milestone,
        'goal': Goal,
        'task': Task
    }
    
    if item_type not in model_map:
        flash('Invalid item type.', 'error')
        return redirect(url_for('main.trash'))
    
    model = model_map[item_type]
    item = model.query.get_or_404(item_id)
    
    # Check permissions
    if item.creator_id != current_user.id and not (
        item_type == 'task' and item.assignee_id == current_user.id
    ):
        flash('You do not have permission to restore this item.', 'error')
        return redirect(url_for('main.trash'))
    
    # Restore the item
    item.restore()
    flash(f'{item_type.title()} restored successfully.', 'success')
    return redirect(url_for('main.trash'))

def get_time_based_stats():
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    # Daily stats
    daily_dreams = Dream.query.filter(Dream.created_at >= today_start).count()
    daily_milestones = Milestone.query.filter(Milestone.created_at >= today_start).count()
    daily_goals = Goal.query.filter(Goal.created_at >= today_start).count()
    daily_tasks = Task.query.filter(Task.created_at >= today_start).count()

    # Weekly stats
    weekly_dreams = Dream.query.filter(Dream.created_at >= week_start).count()
    weekly_milestones = Milestone.query.filter(Milestone.created_at >= week_start).count()
    weekly_goals = Goal.query.filter(Goal.created_at >= week_start).count()
    weekly_tasks = Task.query.filter(Task.created_at >= week_start).count()

    # Monthly stats
    monthly_dreams = Dream.query.filter(Dream.created_at >= month_start).count()
    monthly_milestones = Milestone.query.filter(Milestone.created_at >= month_start).count()
    monthly_goals = Goal.query.filter(Goal.created_at >= month_start).count()
    monthly_tasks = Task.query.filter(Task.created_at >= month_start).count()

    # Task assignments
    assigned_tasks = db.session.query(
        Task.assignee, func.count(Task.id)
    ).group_by(Task.assignee).all()
    assigned_tasks_dict = {user: count for user, count in assigned_tasks if user}

    # Overdue tasks
    overdue_tasks = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'Done'
    ).count()

    # Completed tasks
    completed_tasks = Task.query.filter(Task.status == 'Done').count()

    return {
        'daily_dreams': daily_dreams,
        'daily_milestones': daily_milestones,
        'daily_goals': daily_goals,
        'daily_tasks': daily_tasks,
        'weekly_dreams': weekly_dreams,
        'weekly_milestones': weekly_milestones,
        'weekly_goals': weekly_goals,
        'weekly_tasks': weekly_tasks,
        'monthly_dreams': monthly_dreams,
        'monthly_milestones': monthly_milestones,
        'monthly_goals': monthly_goals,
        'monthly_tasks': monthly_tasks,
        'assigned_tasks': assigned_tasks_dict,
        'overdue_tasks': overdue_tasks,
        'completed_tasks': completed_tasks
    } 