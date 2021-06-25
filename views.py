from flask import Blueprint, jsonify, request
from .Util import writeToJson, readFromJson
from flask_cors import cross_origin


main = Blueprint('main', __name__)

@main.route('/update_schedule', methods=['POST'])
@cross_origin()
def update_schedule():
    f = request.files['file']
    # f = 'C:\\Users\\johnp\\Desktop\\Keck\\Software\\OASchedule\\OASchedule-API\\sched.xlsx'
    status = writeToJson(f)
    return readFromJson('data.json')

@main.route('/')
@cross_origin()
def display_schedule():
    f = 'data.json'
    return readFromJson(f)
