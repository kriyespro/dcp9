from datetime import datetime
from app import db
from app.models.base import BaseModel

class Goal(BaseModel):
    __tablename__ = 'goals'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date, nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 0 to 100

    # Foreign Keys
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.id', ondelete='CASCADE'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    milestone = db.relationship('Milestone', back_populates='goals')
    creator = db.relationship('User', back_populates='created_goals')
    tasks = db.relationship('Task', back_populates='goal', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Goal {self.title}>'

    @property
    def status(self):
        if self.progress >= 100:
            return 'Completed'
        elif self.progress > 0:
            return 'In Progress'
        return 'Not Started'

    def update_progress(self):
        """Update progress based on weighted task progress"""
        if not self.tasks:
            self.progress = 0
            db.session.commit()
            return
            
        # Weight multipliers based on priority
        priority_weights = {
            'Urgent': 1.5,
            'High': 1.2,
            'Medium': 1.0,
            'Low': 0.8
        }
        
        total_weight = 0
        weighted_progress = 0
        
        for task in self.tasks:
            weight = priority_weights.get(task.priority, 1.0)
            total_weight += weight
            weighted_progress += task.progress * weight
        
        self.progress = weighted_progress / total_weight if total_weight > 0 else 0
        db.session.commit()
        
        # Update parent milestone's progress
        if self.milestone:
            self.milestone.update_progress()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'progress': self.progress,
            'milestone': self.milestone.title if self.milestone else None,
            'creator': self.creator.username,
            'task_count': len(self.tasks)
        })
        return base_dict 