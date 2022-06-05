from flask import Flask
from flask_restful import Api, Resource
import paramiko

app = Flask(__name__)
api = Api(app)

class CLI(Resource):
    def get(self,command):
        host="sandbox-iosxe-recomm-1.cisco.com"
        port=22
        username="developer"
        password="C1sco12345"
        command = command
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, port, username, password, look_for_keys=False)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            formatted_lines = ' '.join(map(str, lines))
            return formatted_lines
        except:
            return 'Connection failed'

api.add_resource(CLI, "/cli/<string:command>")


if __name__ == "__main__":
	app.run(debug=True)