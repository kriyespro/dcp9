from datetime import datetime
from app import db
from app.models.base import BaseModel

class Dream(BaseModel):
    __tablename__ = 'dreams'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date, nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 0 to 100

    # Foreign Keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', back_populates='created_dreams')
    milestones = db.relationship('Milestone', back_populates='dream', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Dream {self.title}>'

    @property
    def status(self):
        if self.progress >= 100:
            return 'Completed'
        elif self.progress > 0:
            return 'In Progress'
        return 'Not Started'

    def update_progress(self):
        """Update progress based on weighted milestones progress"""
        if not self.milestones:
            self.progress = 0
            db.session.commit()
            return
            
        total_tasks = 0
        weighted_progress = 0
        
        # Weight milestones by their total number of tasks
        for milestone in self.milestones:
            task_count = sum(len(goal.tasks) for goal in milestone.goals)
            total_tasks += task_count
            weighted_progress += milestone.progress * task_count
        
        self.progress = weighted_progress / total_tasks if total_tasks > 0 else 0
        db.session.commit()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'progress': self.progress,
            'creator': self.creator.username,
            'milestone_count': len(self.milestones)
        })
        return base_dict 