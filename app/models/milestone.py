from datetime import datetime
from app import db
from app.models.base import BaseModel

class Milestone(BaseModel):
    __tablename__ = 'milestones'
    __table_args__ = {'extend_existing': True}

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date, nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 0 to 100

    # Foreign Keys
    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    dream = db.relationship('Dream', back_populates='milestones')
    creator = db.relationship('User', back_populates='created_milestones')
    goals = db.relationship('Goal', back_populates='milestone', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Milestone {self.title}>'

    @property
    def status(self):
        if self.progress >= 100:
            return 'Completed'
        elif self.progress > 0:
            return 'In Progress'
        return 'Not Started'

    def update_progress(self):
        """Update progress based on weighted goals progress"""
        if not self.goals:
            self.progress = 0
            db.session.commit()
            return
            
        total_tasks = 0
        weighted_progress = 0
        
        # Weight goals by their number of tasks
        for goal in self.goals:
            task_count = len(goal.tasks)
            total_tasks += task_count
            weighted_progress += goal.progress * task_count
        
        self.progress = weighted_progress / total_tasks if total_tasks > 0 else 0
        db.session.commit()
        
        # Update parent dream's progress
        if self.dream:
            self.dream.update_progress()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'progress': self.progress,
            'dream': self.dream.title if self.dream else None,
            'creator': self.creator.username,
            'goal_count': len(self.goals)
        })
        return base_dict 