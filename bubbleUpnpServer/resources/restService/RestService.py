
import logging
import subprocess
import sys
import threading
import time

from flask import Flask
from flask import request

app = Flask(__name__)

def _runProcess(listeningPort):
  app.run(host='0.0.0.0', port=listeningPort)
  
@app.route('/shutdown', methods=['PUT'])
def shutdown():
  logging.info("Shutdown post")
  
  func = request.environ.get('werkzeug.server.shutdown')
  if func is None:
      raise RuntimeError('Not running with the Werkzeug Server')
  func()
  
  RestService.isServiceRunning = False
  return "Server shutting down"

@app.route('/service/start', methods=['PUT'])
def startService():
  logging.info("Service started")
  if RestService.runningProcess is None:
    if RestService.commandToRun is not None:
      logging.info("Start service");
      RestService.runningProcess = subprocess.Popen(RestService.commandToRun)
    else:
      logging.info("Command not valid");
  else:
    logging.info("Servie already running");

  return "Service running"

@app.route('/service/stop', methods=['PUT'])
def stopService():
  logging.info("Service stopped")
  if RestService.runningProcess is not None:
    logging.info("Kill running process");
    RestService.runningProcess.terminate()
    RestService.runningProcess.kill()
    RestService.runningProcess = None
  else:
    logging.info("No service running");
  
  return "Service stopped"
    
@app.route('/')
def hello_world():
    logging.info("Root url called")
    return 'Hello, World!'

class RestService(threading.Thread):
  isServiceRunning = True
  runningProcess = None
  commandToRun = None

  def __init__(self):
    threading.Thread.__init__(self)
    self._port = 58051

  def run(self):
    logging.info("Rest service started")
    _runProcess(self._port)

  def stop(self):
    logging.info("Stopping rest service")
    restClient = http.client.HTTPConnection("localhost", self._port)
    restClient.request("PUT", "/shutdown", None)
    logging.info("Rest service stopped")

if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
  logging.info("Main started")
  restService = RestService()
  
  if len(sys.argv) >= 2:
    try:
      restService._port = int(sys.argv[1])
    except ValueError:
      pass    # Nothing to do
      
  if len(sys.argv) >= 3:
    RestService.commandToRun = str(sys.argv[2])
    logging.info("Command to run: " + RestService.commandToRun)
  
  restService.start()
  
  logging.info("Wait loop")
  while RestService.isServiceRunning:
    time.sleep(10)
    
  logging.info("Exit main")
