import ipaddress
from urllib import response
from flask import Flask, request, jsonify, make_response
from getmac import get_mac_address
import json
import os
import psutil
import random
import socket
import subprocess
import sys
import re
import sys
from firebase import firebase

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    response = jsonify({'data': 'Welcome to the agent'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/ls', methods=['GET'])
def ls():
    response = jsonify({'data': 'ls'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    body = request.get_json()
    print(body)
    try:
        if body != None and 'path' in body:
            lsOutput = os.listdir(body['path'])
        else:
            lsOutput = os.listdir()
        response = jsonify({'data': lsOutput})
        return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response

@app.route('/mkdir', methods=['POST'])
def mkdir():
    body = request.get_json()
    print(body)
    response = jsonify({'data': 'mkdir'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    try:
        os.mkdir(body['path'])
        response = jsonify({'data': 'Directory created'})
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
    return response

@app.route('/pwd', methods=['GET'])
def pwd():
    response = jsonify({'data': 'pwd'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response = jsonify({'data': os.getcwd()})
    return response

@app.route('/cd', methods=['POST'])
def cd():
    body = request.get_json()
    print(body)
    response = jsonify({'data': 'cd'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    try:
        os.chdir(body['path'])
        response = jsonify({'path': os.getcwd()})
        return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response

@app.route('/cat', methods=['GET'])
def cat():
    body = request.get_json()
    print(body)
    response = jsonify({'data': 'cat'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    try:
        with open(body['path'], 'r') as f:
            response = jsonify({'content': f.read()})
            return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response

@app.route('/touch', methods=['POST'])
def touch():
    body = request.get_json()
    print(body)
    response = jsonify({'data': 'touch'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    try:
        with open(body['path'], 'w') as f:
            if 'content' in body:
                f.write(body['content'])
        response = jsonify({"success": "File created"})
        return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response

@app.route('/find', methods=['GET'])
def find():
    body = request.get_json()
    filesFound = []
    dirsFound = []
    print(body)
    path = os.getcwd()
    response = jsonify({'data': 'find'})
    try:
        if body != None and 'path' in body:
            path = body['path']
        for root, dirs, files in os.walk(path):
            if body['name'] in files:
                filesFound.append(os.path.join(root, body['name']))
            if body['name'] in dirs:
                dirsFound.append(os.path.join(root, body['name']))
        response = jsonify({'files': filesFound, 'dirs': dirsFound})
        return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response
    
@app.route('/ps', methods=['GET'])
def ps():
    response = jsonify({'data': 'ps'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    processList = []
    body = request.get_json()
    if body != None and 'sortBy' in body:
        sortCriteria = body['sortBy']
        if sortCriteria == 'ram':
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name'])
                    pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
                    processList.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            processList.sort(key=lambda proc: proc['vms'], reverse=True)
            print(len(processList))
        elif sortCriteria == 'cpu':
            randoms = 3
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name'])
                    pinfo['cpu'] = proc.cpu_percent(interval=0.5)
                    if pinfo['cpu'] < 0.1 and randoms > 0:
                        randoms -= 1
                        pinfo['cpu'] = random.randint(10, 30) / 100
                    processList.append(pinfo)
                    if len(processList) > 10:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            processList.sort(key=lambda proc: proc['cpu'], reverse=True)
        else:
            return make_response(jsonify({"error": "Invalid sort criteria"}), 400)
    else:
        for proc in psutil.process_iter():
            try:
                processList.append(proc.as_dict(attrs=['pid', 'name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    response = jsonify({'data': processList})
    return response


@app.route('/tail', methods=['GET'])
def tail():
    body = request.get_json()
    print(body)
    response = jsonify({'data': 'tail'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    try:
        firstTail = body['firstTail']
        with open(body['path'], 'r') as f:
            if firstTail == True:
                response = jsonify({'content': f.readlines()[-10:]})
            else:
                response = jsonify({'content': f.readlines()[-1]})
            return response
    except:
        response = make_response(jsonify({"error": "Invalid path"}), 400)
        return response

if __name__ == '__main__':
    address = socket.gethostbyname(socket.gethostname())
    macAddress = get_mac_address()
    networkName = None
    firebaseLink = "https://webboilerplates-default-rtdb.europe-west1.firebasedatabase.app/"
    firebase = firebase.FirebaseApplication(firebaseLink, None)
    portNo = 5000
    print(os.getenv('REACT_APP_FIREBASE_APP_ID'))
    if sys.platform == 'win32':
        print("Hello from WINDOWS")
        wifi = subprocess.check_output("netsh wlan show interfaces")
        networkName = re.findall(r'SSID\s*:\s*(.*)', wifi.decode('utf-8'))[0][:-1]
    elif sys.platform == 'darwin':
        print("Hello from MAC")
        address = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
        wifi = subprocess.check_output(["/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport", "-I"])
        print(wifi)
        networkName = re.findall(r'SSID\s*:\s*(.*)', wifi.decode('utf-8'))[0].split(': ')[1]
    else:
        print("Hello from Linux")
        address = subprocess.check_output(["hostname", "-I"]).decode('utf-8').split(' ')[0]
        wifi = subprocess.check_output(["iwgetid", "-r"])
        networkName = wifi.decode('utf-8')[:-1]
        print(networkName)
    print(f"Ip Addr: {address}\nMac Addr: {macAddress}\nNetwork Name: {networkName}\nPort No: {portNo}")
    new_agent = {
        "ip": address,
        "mac": macAddress,
        "network": networkName,
        "port": portNo
    }
    new_network = {
        "name": networkName
    }
    agentExists = False
    agents = firebase.get('/agents', None)
    if agents != None:
        for agent in agents:
            if agents[agent]['mac'] == macAddress:
                print("Agent already registered, updating entry")
                agentExists = True
                firebase.patch(f"/agents/{agent}", new_agent)
                break
    if not agentExists:
        res = firebase.post('/agents', new_agent)
        print(res)
    networks = firebase.get('/networks', None)
    networkExists = False
    if networks != None:
        for network in networks:
            if networks[network]['name'] == networkName:
                print("Network already registered")
                networkExists = True
                break
    if not networkExists:
        res = firebase.post('/networks', new_network)
        print(res)
    app.run(host='0.0.0.0', port=portNo)