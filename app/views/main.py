from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models import Dream, Milestone, Goal, Task, User
from app.forms.dream import DreamForm
from app.forms.milestone import MilestoneForm
from app.forms.goal import GoalForm
from app.forms.task import TaskForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get dreams for current user only
    dreams = Dream.query.filter_by(creator_id=current_user.id).all()
    total_dreams = len(dreams)
    
    # Add edit_url to each dream
    for dream in dreams:
        dream.edit_url = url_for('main.edit_dream', dream_id=dream.id)
    
    # Get counts for current user
    total_milestones = Milestone.query.join(Dream).filter(Dream.creator_id == current_user.id).count()
    total_goals = Goal.query.join(Milestone, Goal.milestone_id == Milestone.id)\
                          .join(Dream, Milestone.dream_id == Dream.id)\
                          .filter(Dream.creator_id == current_user.id).count()
    total_tasks = Task.query.join(Goal, Task.goal_id == Goal.id)\
                          .join(Milestone, Goal.milestone_id == Milestone.id)\
                          .join(Dream, Milestone.dream_id == Dream.id)\
                          .filter(Dream.creator_id == current_user.id).count()
    
    # Calculate overall progress
    overall_progress = 0
    if total_dreams > 0:
        total_progress = sum(dream.progress or 0 for dream in dreams)
        overall_progress = total_progress / total_dreams
    
    return render_template('main/dashboard.html',
                         dreams=dreams,
                         total_dreams=total_dreams,
                         total_milestones=total_milestones,
                         total_goals=total_goals,
                         total_tasks=total_tasks,
                         overall_progress=overall_progress)

@main_bp.route('/profile')
@login_required
def profile():
    assigned_tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    return render_template('main/profile.html', tasks=assigned_tasks)

# Dream CRUD routes
@main_bp.route('/dreams/create', methods=['GET', 'POST'])
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

@main_bp.route('/dreams/<int:dream_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dream(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id and not current_user.is_admin():
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

@main_bp.route('/dreams/<int:dream_id>/delete', methods=['POST'])
@login_required
def delete_dream(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this dream.', 'error')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(dream)
    db.session.commit()
    flash('Dream deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/milestones/create/<int:dream_id>', methods=['GET', 'POST'])
@login_required
def create_milestone(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to add milestones to this dream.', 'error')
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

@main_bp.route('/milestones/<int:milestone_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this milestone.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = MilestoneForm(obj=milestone)
    if form.validate_on_submit():
        milestone.title = form.title.data
        milestone.description = form.description.data
        milestone.target_date = form.target_date.data
        db.session.commit()
        flash('Milestone updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/milestone/edit.html', form=form, milestone=milestone)

@main_bp.route('/milestones/<int:milestone_id>/delete', methods=['POST'])
@login_required
def delete_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    # Check if user owns the parent dream
    if milestone.dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this milestone.', 'error')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(milestone)
    db.session.commit()
    flash('Milestone deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

# API endpoints for dynamic loading
@main_bp.route('/api/dreams/<int:dream_id>/milestones')
@login_required
def get_milestones(dream_id):
    milestones = Milestone.query.filter_by(dream_id=dream_id).all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'progress': m.progress,
        'target_date': m.target_date.strftime('%Y-%m-%d'),
        'edit_url': url_for('main.edit_milestone', milestone_id=m.id)
    } for m in milestones])

@main_bp.route('/api/milestones/<int:milestone_id>/goals')
@login_required
def get_goals(milestone_id):
    goals = Goal.query.filter_by(milestone_id=milestone_id).all()
    return jsonify([{
        'id': g.id,
        'title': g.title,
        'description': g.description,
        'progress': g.progress,
        'target_date': g.target_date.strftime('%Y-%m-%d'),
        'edit_url': url_for('main.edit_goal', goal_id=g.id)
    } for g in goals])

@main_bp.route('/api/goals/<int:goal_id>/tasks')
@login_required
def get_tasks(goal_id):
    tasks = Task.query.filter_by(goal_id=goal_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'due_date': t.due_date.strftime('%Y-%m-%d'),
        'priority': t.priority,
        'status': t.status,
        'progress': t.progress,
        'assignee': t.assignee.username if t.assignee else None,
        'edit_url': url_for('main.edit_task', task_id=t.id)
    } for t in tasks])

@main_bp.route('/goals/create/<int:milestone_id>', methods=['GET', 'POST'])
@login_required
def create_goal(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    # Ensure user owns the parent dream
    if milestone.dream.creator_id != current_user.id:
        abort(403)
    
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

@main_bp.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.milestone.dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_date = form.target_date.data
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/goal/edit.html', form=form, goal=goal)

@main_bp.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    # Check if user owns the parent dream
    if goal.milestone.dream.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/tasks/create/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def create_task(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    # Ensure the user has permission to create tasks for this goal
    if goal.creator_id != current_user.id:
        flash('You do not have permission to create tasks for this goal.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = TaskForm()
    
    # Populate assignee choices
    form.assignee_id.choices = [(0, 'Unassigned')] + [
        (user.id, user.username) 
        for user in User.query.order_by(User.username).all()
    ]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data,
            creator_id=current_user.id,
            goal_id=goal.id,
            assignee_id=form.assignee_id.data if form.assignee_id.data else None
        )
        
        db.session.add(task)
        db.session.commit()
        flash(f'Task created successfully! ID:{task.id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/task/create.html', form=form, goal=goal)

@main_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.goal.milestone.dream.creator_id != current_user.id and task.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this task.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = TaskForm(obj=task)
    # Populate assignee choices
    form.assignee_id.choices = [(0, 'Unassigned')] + [
        (user.id, user.username) 
        for user in User.query.order_by(User.username).all()
    ]
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.status = form.status.data
        
        # Set assignee if one was selected
        if form.assignee_id.data != 0:
            task.assignee_id = form.assignee_id.data
        else:
            task.assignee_id = None
            
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Set the current assignee in the form
    if task.assignee_id:
        form.assignee_id.data = task.assignee_id
    else:
        form.assignee_id.data = 0
        
    return render_template('main/task/edit.html', form=form, task=task)

@main_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Check if user owns the parent dream or is the task creator
    if task.goal.milestone.dream.creator_id != current_user.id and task.creator_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this task.', 'error')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))