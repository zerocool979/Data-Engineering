from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    from app.main import routes
    app.register_blueprint(routes.main)
    
    return app
