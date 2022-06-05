from flask import Flask
from flask_restful import Api, Resource
import paramiko

app = Flask(__name__)
api = Api(app)

#class HelloWorld(Resource):
#    def get(self, name, test):
#        return {'name': name, 'test': test}

#api.add_resource(HelloWorld, "/helloworld/<string:name>/<int:test>")

class CLI(Resource):
    def get(self,command):
        host="sandbox-iosxe-recomm-1.cisco.com"
        port=22
        username="developer"
        password="C1sco12345"
        command = command
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, look_for_keys=False)
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        print(lines)
        return {'stdout':lines}

api.add_resource(CLI, "/cli/<string:command>")


if __name__ == "__main__":
	app.run(debug=True)