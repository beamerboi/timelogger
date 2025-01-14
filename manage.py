from flask_migrate import Migrate
from app import create_app
from extensions import db
from models.user import User
from models.time_log import TimeLog

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()