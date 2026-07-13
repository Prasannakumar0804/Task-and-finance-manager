from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.transactions import transactions_bp
from routes.dashboard import dashboard_bp
from flask import render_template

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(dashboard_bp)

 

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)