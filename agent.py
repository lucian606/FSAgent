from flask import Flask, request, jsonify
import json
import os
import psutil
import random

app = Flask(__name__)

@app.route('/ls', methods=['GET'])
def ls():
    body = request.get_json()
    print(body)
    try:
        if 'path' in body:
            lsOutput = os.listdir(body['path'])
        else:
            lsOutput = os.listdir('.')
        print(lsOutput)
        return json.dumps(lsOutput)
    except:
        return json.dumps({"error": "Invalid path"})

@app.route('/mkdir', methods=['POST'])
def mkdir():
    body = request.get_json()
    print(body)
    try:
        os.mkdir(body['path'])
        return json.dumps({"success": "Directory created"})
    except:
        return json.dumps({"error": "Invalid path"})

@app.route('/pwd', methods=['GET'])
def pwd():
    return json.dumps({"path": os.getcwd()})

@app.route('/cd', methods=['POST'])
def cd():
    body = request.get_json()
    print(body)
    try:
        os.chdir(body['path'])
        return json.dumps({"path": os.getcwd()})
    except:
        return json.dumps({"error": "Invalid path"})

@app.route('/cat', methods=['GET'])
def cat():
    body = request.get_json()
    print(body)
    try:
        with open(body['path'], 'r') as f:
            return json.dumps({"content": f.read()})
    except:
        return json.dumps({"error": "Invalid path"})

@app.route('/touch', methods=['POST'])
def touch():
    body = request.get_json()
    print(body)
    try:
        with open(body['path'], 'w') as f:
            if 'content' in body:
                f.write(body['content'])
        return json.dumps({"success": "File created"})
    except:
        return json.dumps({"error": "Invalid path"})

@app.route('/find', methods=['GET'])
def find():
    body = request.get_json()
    filesFound = []
    dirsFound = []
    print(body)
    path = os.getcwd()
    try:
        if 'path' in body:
            path = body['path']
        for root, dirs, files in os.walk(path):
            if body['name'] in files:
                filesFound.append(os.path.join(root, body['name']))
            if body['name'] in dirs:
                dirsFound.append(os.path.join(root, body['name']))
        return json.dumps({"files": filesFound, "dirs": dirsFound})
    except:
        return json.dumps({"error": "Invalid search path"})
    
@app.route('/ps', methods=['GET'])
def ps():
    processList = []
    body = request.get_json()
    if 'sortBy' in body:
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
            return json.dumps({"error": "Invalid sort criteria"})
    else:
        for proc in psutil.process_iter():
            try:
                processList.append(proc.as_dict(attrs=['pid', 'name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return json.dumps(processList)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)