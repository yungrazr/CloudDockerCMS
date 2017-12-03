from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return """
Available API endpoints:

GET /containers                     List all containers
GET /containers?state=running      List running containers (only)
GET /containers/<id>                Inspect a specific container
GET /containers/<id>/logs           Dump specific container logs
GET /images                         List all images


POST /images                        Create a new image
POST /containers                    Create a new container

PATCH /containers/<id>              Change a container's state
PATCH /images/<id>                  Change a specific image's attributes
DELETE /containers/<id>             Delete a specific container
DELETE /containers                  Delete all containers (including running)
DELETE /images/<id>                 Delete a specific image
DELETE /images                      Delete all images
"""

def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.decode(encoding='UTF-8').startswith('Error'):
        print('Error: {0} -> {1}'.format(' '.join(cmd), stderr))
    return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['image'] = c[1]
        each['name'] = c[-1]
        each['ports'] = c[-2]
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2]
        each['tag'] = c[1]
        each['name'] = c[0]
        all.append(each)
    return all


@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool
    """
    if request.args.get('state') == 'running': 
        output = docker('ps')
        resp = json.dumps(docker_ps_to_array(output.decode(encoding='UTF-8')))
         
    else:
        output = docker('ps', '-a')
        resp = json.dumps(docker_ps_to_array(output.decode(encoding='UTF-8')))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
def container_specific_show(id):
	#Inspect a specific container
	
	resp = docker('inspect', str(id))
	return Response(response=resp, mimetype="application/json")	

@app.route('/containers/<id>/logs', methods=['GET'])
def container_specific_log(id):
	#Dump specific container logs
	output = docker('logs', str(id))
	resp = json.dumps(docker_logs_to_object(str(id), output.decode(encoding='UTF-8')))

	return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
def images_index():
	#List all images
	
    output = docker('images')
    resp = json.dumps(docker_images_to_array(output.decode(encoding='UTF-8')))
    
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['POST'])
def images_create():
	#Create Image
	dockerfile = request.files['file']
	dockerfile.save('Dockerfile')
	
	docker('build', '-t', 'custom', '.')
	images = docker('images')
	
	resp  = json.dumps(docker_images_to_array(images.decode(encoding='UTF-8')))
	return Response(response=resp, mimetype="application/json")
	
@app.route('/containers', methods=['POST'])
def containers_create():
	#Create container with existing image
	body = request.get_json(force=True)
	image = body['image']
	output = docker('run', '-d', image)[0:12]
	
	resp = '{"id": "' + output + '"}'
	return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
	#Update container attributes
	body = request.get_json(force=True)
	try:
		state = body['state']
		if state == 'running':
			docker('restart', id)
		else:
			docker('stop', id)
	except:
		pass
		
	resp = '{"id": "updated"}'
	return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
	#Update image attributes
	body = request.get_json(force=True)
	tag = body['tag']
    
	output = docker('tag', str(id), tag)
	resp = '{"id": "' + output + '"}'
	return Response(response=resp, mimetype="application/json")
	
@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
	#Delete specific container
	docker('rm', id)
    
	resp = '{"id": ' + str(id) + ', "status": "Removed"}'
	return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
	#Remove all containers
	output = docker('ps', '-a')
	contain = docker_ps_to_array(output)

	for c in contain:
		if c['image'] != 'cms':
			docker('stop', c['id'])
			docker('rm', c['id'])
			
	resp = '{"status": "containers removed"}'
	return Response(response=resp, mimetype="application/json")
    
@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
	#Delete specific image
	
    docker('rmi', str(id))
    resp = '{"id": ' + id + ', "status": "removed"}'
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['DELETE'])
def images_remove_all():
	#Remove all images
	output = docker('images')
	images = docker_images_to_array(output)
	
	for i in images:
		if i['name'] != 'cms':
			docker('rmi', i['name'])
			
	resp = '{"status": "images removed"}'
	return Response(response=resp, mimetype="application/json")	

if __name__ == '__main__':
    app.run()
