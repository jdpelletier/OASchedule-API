from flask import Blueprint, jsonify, request, send_file
import Util
from flask_cors import cross_origin


main = Blueprint('main', __name__)

@main.route('/update_schedule', methods=['POST'])
@cross_origin()
def update_schedule():
    user = request.form['user']
    admin = Util.isAdmin(user.get_json())
    if admin == True:
        f = request.files['file']
        status = Util.writeToJson(f)
    return Util.readFromJson('data.json')

@main.route('/')
@cross_origin()
def display_schedule():
    return Util.readFromJson('data.json')

@main.route('/compare')
@cross_origin()
def compare_schedule():
    return Util.compareJsons()

@main.route('/nightstaff', methods=['POST'])
@cross_origin()
def getNightStaff():
    return Util.getNSFromTelSched(request.get_json())

@main.route('/observers', methods=['POST'])
@cross_origin()
def getObservers():
    return Util.getObserversFromTelSchedule(request.get_json())

@main.route('/get-employee-schedule', methods=['POST'])
@cross_origin()
def getEmployeeSchedule():
    emp = request.get_json()
    try:
        return send_file(Util.exportPersonalSchedule('data.json', emp["employee"]), attachment_filename=f'{emp["employee"]}.csv', as_attachment=True)
    except Exception as e:
        return str(e)

@main.route('/file_check')
@cross_origin()
def check_for_file():
    return Util.fileCheck()

@main.route('/is_admin', methods=['POST'])
@cross_origin()
def isAdmin():
    return Util.isAdmin(request.get_json())