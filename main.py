from flask import Flask, request
from flask_restful import Api, Resource
import paramiko
from ncclient import manager
import xml.dom.minidom
import logging

app = Flask(__name__)
api = Api(app)


class CLI(Resource):

    host = "sandbox-iosxe-latest-1.cisco.com"
    port = 22
    username = "developer"
    password = "C1sco12345"

    def get(self, command):
        host = self.host
        port = self.port
        username = self.username
        password = self.password
        command = command
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, port, username, password, look_for_keys=False)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            return lines
        except Exception:
            logging.exception(Exception)
            return 'Connection failed'


api.add_resource(CLI, "/cli/<string:command>")


class Loopback(Resource):

    host = 'sandbox-iosxe-latest-1.cisco.com'
    username = 'developer'
    password = 'C1sco12345'

    def put(self, name):
        try:
            # JSON must be passed
            args = request.get_json(cache=False, force=True)
            # Description is required
            if 'description' not in args:
                return "Loopback description is required", 400
            # IP_address is required
            if 'ip_address' not in args:
                return "Loopback ip_address is required", 400
            # Mask is required
            if 'mask' not in args:
                return "mask for the loopback is required", 400
            # Dry_run is optional
            if 'dry_run' not in args:
                dry_run = False
            elif args["dry_run"] is True:
                dry_run = args['dry_run']
        except Exception as e:
            logging.info(str(e))
            return "bad request", 400

        # Create an XML configuration template for ietf-interfaces
        nci_template = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0"
          xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                <name>{name}</name>
                <description>{desc}</description>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
                    {type}
                </type>
                <enabled>{status}</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>{ip_address}</ip>
                        <netmask>{mask}</netmask>
                    </address>
                </ipv4>
                </interface>
            </interfaces>
        </config>"""

        # Create the NETCONF data payload for this interface
        nc_data = nci_template.format(name='Loopback'+name,
                                      desc=args["description"],
                                      type="ianaift:softwareLoopback",
                                      status="true",
                                      ip_address=args["ip_address"],
                                      mask=args["mask"]
                                      )

        # Open a connection to the network device using ncclient
        with manager.connect(
                host=self.host,
                port=830,
                username=self.username,
                password=self.password,
                hostkey_verify=False
                ) as m:

            if dry_run is True:
                # Return the generated payload
                # (to be sent to the device) back to the user
                return(xml.dom.minidom.parseString(nc_data).toprettyxml())
            else:
                try:
                    # Make a NETCONF <get-config> query using the filter
                    netconf_reply = m.edit_config(nc_data, target='running')
                except Exception as e:
                    return str(e)

        # Return the returned XML
        return(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())

    def delete(self, name):
        try:
            # Can have dry_run option requested in JSON
            args = request.get_json(cache=False, force=True)
            if 'dry_run' not in args:
                dry_run = False
            elif args["dry_run"] is True:
                dry_run = args['dry_run']
        except Exception as noJSON:
            logging.info(str(noJSON))
            dry_run = False

        # Create an XML configuration template for ietf-interfaces
        netconf_interface_template = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0"
          xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
         <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                        <interface operation="delete">
                                <name>{name}</name>
                        </interface>
                </interfaces>
        </config>"""
        netconf_data = netconf_interface_template.format(name=name)

        # Open a connection to the network device using ncclient
        with manager.connect(
                host=self.host,
                port=830,
                username=self.username,
                password=self.password,
                hostkey_verify=False
                ) as m:

            if dry_run is True:
                # Return the generated payload
                # (to be sent to the device) back to the user
                return(xml.dom.minidom.parseString(netconf_data).toprettyxml())
            else:
                try:
                    # Make a NETCONF <get-config> query using the filter
                    nc_reply = m.edit_config(netconf_data, target='running')
                    print(nc_reply)
                except Exception as e:
                    return str(e)
        # Return the returned XML
        return(xml.dom.minidom.parseString(nc_reply.xml).toprettyxml())


api.add_resource(Loopback, "/loopback/<string:name>")

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
