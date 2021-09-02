from flask import Blueprint, jsonify, request, send_file
import Util
from flask_cors import cross_origin


main = Blueprint('main', __name__)

@main.route('/update_schedule', methods=['POST'])
@cross_origin()
def update_schedule():
    f = request.files['file']
    status = Util.writeToJson(f)
    return readFromJson('data.json')

@main.route('/')
@cross_origin()
def display_schedule():
    f = 'data.json'
    return Util.readFromJson(f)

@main.route('/get-employee-schedule', methods=['POST'])
@cross_origin()
def getEmployeeSchedule():
    emp = request.get_json()
    try:
        return send_file(Util.exportPersonalSchedule('data.json', emp["employee"]), attachment_filename=f'{emp["employee"]}.csv', as_attachment=True)
    except Exception as e:
        return str(e)
