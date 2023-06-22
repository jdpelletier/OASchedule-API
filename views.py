from flask import Blueprint, jsonify, request, send_file
import Util
from flask_cors import cross_origin


main = Blueprint('main', __name__)

@main.route('/update_schedule', methods=['POST'])
@cross_origin()
def update_schedule():
    f = request.files['file']
    status = Util.writeToJson(f)
    return Util.readFromJson('data.json')

###New, read from tel schedule
@main.route('/')
@cross_origin()
def display_schedule():
    return Util.getNSFromTelSched()

@main.route('/observers')
@cross_origin()
def getObservers():
    return Util.getObserversFromTelSchedule()

@main.route('/get-employee-schedule', methods=['POST'])
@cross_origin()
def getEmployeeSchedule():
    emp = request.get_json()
    try:
        return send_file(Util.exportPersonalSchedule('data.json', emp["employee"]), attachment_filename=f'{emp["employee"]}.csv', as_attachment=True)
    except Exception as e:
        return str(e)
