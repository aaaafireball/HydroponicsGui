from flask import Flask, jsonify, request
import json
import multiprocessing
from ctypes import c_bool,c_char_p
import driver

# class for holding serverside instances and threading instances
class BackendGUI():
    def __init__(self, app):
        self.app = app

        self.manager = multiprocessing.Manager()
        self.data = self.manager.Value(c_char_p, '{}')
        self.kill_program = self.manager.Value((c_bool), False)

        self.multithread = multiprocessing.Process(target=driver.main, args=(self.kill_program,))


app = Flask(__name__)  # create the flask app
backend = BackendGUI(app)  # create the backend class object

'''
starts the water system with the given parameters

accepts:
    Json object with the following parameters:
    timeWaterCycle - water cycle intervals in hours
    timeStart - Starting time of the water cycle in hours
    timeStop - Ending time of the water cycle in hours
    bin1Nutrient1 - if nutrient 1 is sent to bin 1
    bin1Nutrient2 - if nutrient 2 is sent to bin 1
    bin1Nutrient3 - if nutrient 3 is sent to bin 1
    bin1Nutrient4 - if nutrient 4 is sent to bin 1
    bin1Nutrient5 - if nutrient 5 is sent to bin 1
    bin1Nutrient6 - if nutrient 6 is sent to bin 1
    bin1Nutrient7 - if nutrient 7 is sent to bin 1
    bin1Nutrient8 - if nutrient 8 is sent to bin 1
    bin1lights - if lights are turned on in bin 1
    bin2Nutrient1 - if nutrient 1 is sent to bin 2
    bin2Nutrient2 - if nutrient 2 is sent to bin 2
    bin2Nutrient3 - if nutrient 3 is sent to bin 2 
    bin2Nutrient4 - if nutrient 4 is sent to bin 2
    bin2Nutrient5 - if nutrient 5 is sent to bin 2
    bin2Nutrient6 - if nutrient 6 is sent to bin 2
    bin2Nutrient7 - if nutrient 7 is sent to bin 2
    bin2Nutrient8 - if nutrient 8 is sent to bin 2
    bin2lights - if lights are turned on in bin 2

returns:
    Json object with the following parameters:
    success - if the water system was started successfully
    error - if the water system was not started successfully
'''
@backend.app.route("/startSystem", methods=["POST"])
def startSystem():
    try:
        data = request.get_json()  # get the data from the request
        with open("./backEnd/system.json", "w") as f:
            json.dump(data, f)  # write the data to the system.json file
        backend.multithread.start()  # start the system

        return jsonify({"success": True})  # return success for frontend validation
    except (Exception) as e:
        return jsonify({"success": False, "error": str(e)})  # return error for frontend validation

@backend.app.route("/primePumps", methods=["POST"])
def primePumps():
    priming_pumps = multiprocessing.Process(target=driver.prime_pumps)
    priming_pumps.start()
    priming_pumps.join()
    with open("test.txt", "a") as  f:
        f.write("test")
    return jsonify({"success": True})

'''
Stops the water system

accepts:
    None
    
returns:
    Json object with the following parameters:
    success - if the water system was stopped successfully
    error - if the water system was not stopped successfully
'''
@backend.app.route("/stopSystem", methods=["POST"])
def stopSystem():
    try:
        kill_process = multiprocessing.Process(target=driver.stop, args=(backend.kill_program,)) # set the kill_program to true
        kill_process.start() # start the process
        kill_process.join() # wait for the process to finish

        backend.multithread.terminate()  # terminate the process
        backend.multithread.join()  # wait for the process to finish

        backend.multithread = multiprocessing.Process(target=driver.main, args=(backend.kill_program,))  # reset the process

        return jsonify({"success": True})  # return success for frontend validation
    except (Exception) as e:
        return jsonify({"success": False, "error": str(e)})  # return error for frontend validation

@backend.app.route("/stop", methods=["POST"])
def stop():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@backend.app.route("/readLog", methods=["GET"])
def readLog():
    text = None
    with open("log.txt", "r") as f:
        text = f.read()
    return jsonify({"success": True, "log": text})
