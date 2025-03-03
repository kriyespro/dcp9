from datetime import datetime
from app import db
from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = 'tasks'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent
    status = db.Column(db.String(20), default='Todo')  # Todo, In Progress, Review, Done
    progress = db.Column(db.Float, default=0.0)  # 0 to 100

    # Foreign Keys
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id', ondelete='CASCADE'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    goal = db.relationship('Goal', back_populates='tasks')
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_tasks')
    assignee = db.relationship('User', foreign_keys=[assignee_id], back_populates='assigned_tasks')

    def __repr__(self):
        return f'<Task {self.title}>'

    def update_progress(self, new_progress=None):
        """Update task progress based on status or direct progress value"""
        if new_progress is not None:
            self.progress = new_progress
        else:
            # Calculate progress based on status
            status_progress = {
                'Done': 100.0,
                'Review': 75.0,
                'In Progress': 50.0,
                'Todo': 0.0,
                'Not Started': 0.0,
                'Completed': 100.0
            }
            self.progress = status_progress.get(self.status, 0.0)
        
        db.session.commit()
        
        # Update parent goal's progress
        if self.goal:
            self.goal.update_progress()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'progress': self.progress,
            'goal': self.goal.title if self.goal else None,
            'creator': self.creator.username,
            'assignee': self.assignee.username if self.assignee else None
        })
        return base_dict 