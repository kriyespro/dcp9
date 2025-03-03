import click
from flask.cli import with_appcontext
from app.models import db, User, Role

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with default roles and admin user."""
    # Create roles if they don't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user')
        db.session.add(user_role)
    
    # Create admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role=admin_role
        )
        admin_user.set_password('admin123')  # Default password, should be changed
        db.session.add(admin_user)
    
    db.session.commit()
    click.echo('Initialized the database with default roles and admin user.')
    click.echo('Admin credentials:')
    click.echo('  Username: admin')
    click.echo('  Password: admin123')
    click.echo('Please change the admin password after first login!') 