import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Role, Dream, Milestone, Goal, Task
from datetime import datetime, timedelta

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()
    
    # Create roles
    admin_role = Role(name='admin')
    user_role = Role(name='user')
    db.session.add_all([admin_role, user_role])
    db.session.commit()
    
    # Create test users with simpler setup
    admin = User(
        username='admin',
        email='admin@example.com',
        role=admin_role
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    test_user = User(
        username='test',
        email='test@example.com',
        role=user_role
    )
    test_user.set_password('test123')
    db.session.add(test_user)
    
    db.session.commit()
    
    # Create one test dream for admin
    dream = Dream(
        title='Test Dream',
        description='A test dream for development',
        target_date=datetime.now() + timedelta(days=30),
        creator_id=1,  # Admin user
        progress=0
    )
    db.session.add(dream)
    db.session.commit()
    
    # Create one test milestone
    milestone = Milestone(
        title='Test Milestone',
        description='A test milestone',
        target_date=datetime.now() + timedelta(days=15),
        dream_id=1,
        creator_id=1,
        progress=0
    )
    db.session.add(milestone)
    db.session.commit()
    
    # Create one test goal
    goal = Goal(
        title='Test Goal',
        description='A test goal',
        target_date=datetime.now() + timedelta(days=7),
        milestone_id=1,
        creator_id=1,
        progress=0
    )
    db.session.add(goal)
    db.session.commit()
    
    # Create one test task
    task = Task(
        title='Test Task',
        description='A test task',
        due_date=datetime.now() + timedelta(days=3),
        priority='Medium',
        status='Not Started',
        creator_id=1,
        goal_id=1,
        assignee_id=2  # Assigned to test user
    )
    db.session.add(task)
    db.session.commit()
    
    # Save test user credentials to a file
    with open('test_users.txt', 'w') as f:
        f.write('Test User Credentials:\n\n')
        f.write('Admin User:\n')
        f.write('Email: admin@example.com\n')
        f.write('Password: admin123\n\n')
        f.write('Test User:\n')
        f.write('Email: test@example.com\n')
        f.write('Password: test123\n')
    
    click.echo('Initialized the database with test users.')
    click.echo('Test user credentials have been saved to test_users.txt')

def init_app(app):
    app.cli.add_command(init_db_command) 