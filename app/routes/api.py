from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, Task, Dream, Milestone, Goal
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task_api(task_id):
    """Update task details via API."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user is assigned to this task or is creator
    if task.assignee_id != current_user.id and task.creator_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
        task.update_progress()  # This will update progress based on status
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data['due_date'] else None
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'progress': task.progress,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/dreams/<int:dream_id>/update', methods=['POST'])
@login_required
def update_dream(dream_id):
    """Update dream details."""
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        dream.title = data['title']
    if 'description' in data:
        dream.description = data['description']
    if 'target_date' in data:
        dream.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'dream': {
                'id': dream.id,
                'title': dream.title,
                'description': dream.description,
                'progress': dream.progress,
                'target_date': dream.target_date.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/milestones/<int:milestone_id>/update', methods=['POST'])
@login_required
def update_milestone(milestone_id):
    """Update milestone details."""
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.creator_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        milestone.title = data['title']
    if 'description' in data:
        milestone.description = data['description']
    if 'target_date' in data:
        milestone.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'milestone': {
                'id': milestone.id,
                'title': milestone.title,
                'description': milestone.description,
                'progress': milestone.progress,
                'target_date': milestone.target_date.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/goals/<int:goal_id>/update', methods=['POST'])
@login_required
def update_goal(goal_id):
    """Update goal details."""
    goal = Goal.query.get_or_404(goal_id)
    if goal.creator_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        goal.title = data['title']
    if 'description' in data:
        goal.description = data['description']
    if 'target_date' in data:
        goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'goal': {
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'progress': goal.progress,
                'target_date': goal.target_date.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/dreams/<int:dream_id>/milestones')
@login_required
def get_dream_milestones(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    milestones = Milestone.query.filter_by(dream_id=dream_id).all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'progress': m.progress or 0,
        'edit_url': f'/milestones/{m.id}/edit'
    } for m in milestones])

@api.route('/milestones/<int:milestone_id>/goals')
@login_required
def get_milestone_goals(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    goals = Goal.query.filter_by(milestone_id=milestone_id).all()
    return jsonify([{
        'id': g.id,
        'title': g.title,
        'description': g.description,
        'progress': g.progress or 0,
        'edit_url': f'/goals/{g.id}/edit'
    } for g in goals])

@api.route('/goals/<int:goal_id>/tasks')
@login_required
def get_goal_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    tasks = Task.query.filter_by(goal_id=goal_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'priority': t.priority,
        'status': t.status,
        'progress': t.progress or 0,
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
        'assignee': t.assignee.username if t.assignee else None,
        'edit_url': f'/tasks/{t.id}/edit'
    } for t in tasks]) 