from flask import Flask
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    #
    # db.init_app(app)

    import views

    app.register_blueprint(views.main)

    return app

if __name__ == '__main__':

    app = create_app()
    host = '0.0.0.0'
    port = 53879

    # run flask server
    print(f"Starting OA Schedule API: PORT = {port}")
    # app.run(host=host, port=port)
    app.run(host=host, port=port, ssl_context='adhoc')
    print("Stopping OA Schedule API.")