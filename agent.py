from flask import Flask, request, jsonify
import json
import os

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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)