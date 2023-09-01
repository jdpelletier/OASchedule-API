#!/usr/local/anaconda-3/bin/python
import argparse
from flask import Flask
from flask_cors import CORS

def parse_args():
    parser = argparse.ArgumentParser(description="Start KVS API")
    parser.add_argument("--port", type=int, default=0, help='Server Port')
    return parser.parse_args()

def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    import views

    app.register_blueprint(views.main)

    return app

if __name__ == '__main__':
    args = parse_args()
    port = args.port
    app = create_app()
    host = '0.0.0.0'
    # port = 53879

    # run flask server
    print(f"Starting OA Schedule API: PORT = {port}")
    # app.run(host=host, port=port)
    app.run(host=host, port=port)
    print("Stopping OA Schedule API.")