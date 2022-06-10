from flask import Flask
from flask_restful import Api, Resource, reqparse
import paramiko
from ncclient import manager
import xml.dom.minidom
import logging

app = Flask(__name__)
api = Api(app)

loopback_put_args = reqparse.RequestParser()
loopback_put_args.add_argument("dry_run", type=bool)
loopback_put_args.add_argument(
                            "description", type=str,
                            help="Loopback description is required",
                            required=True
                            )
loopback_put_args.add_argument(
                            "ip_address", type=str,
                            help="Loopback ip_address is required",
                            required=True
                            )
loopback_put_args.add_argument(
                            "mask", type=str,
                            help="mask for the loopback is required",
                            required=True
                            )

loopback_delete_args = reqparse.RequestParser()
loopback_delete_args.add_argument("dry_run", type=bool)


class CLI(Resource):
    def get(self, command):
        host = "sandbox-iosxe-latest-1.cisco.com"
        port = 22
        username = "developer"
        password = "C1sco12345"
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

    dry_run = False
    host = 'sandbox-iosxe-latest-1.cisco.com'
    username = 'developer'
    password = 'C1sco12345'

    def put(self, name):
        args = loopback_put_args.parse_args()
        self.dry_run = args['dry_run']


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

            if self.dry_run is True:
                # Return the generated payload
                # (to be sent to the device) back to the user
                return(xml.dom.minidom.parseString(nc_data).toprettyxml())
            else:
                try:
                    # Make a NETCONF <get-config> query using the filter
                    netconf_reply = m.edit_config(nc_data, target='running')
                except Exception:
                    logging.exception(Exception)
                    # If the loopback to be created is invalid
                    return 'Inconsistent value'

        # Return the returned XML
        return(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())

    def delete(self, name):

        args = loopback_delete_args.parse_args()
        self.dry_run = args['dry_run']

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

            if self.dry_run is True:
                # Return the generated payload
                # (to be sent to the device) back to the user
                return(xml.dom.minidom.parseString(netconf_data).toprettyxml())
            else:
                try:
                    # Make a NETCONF <get-config> query using the filter
                    nc_reply = m.edit_config(netconf_data, target='running')
                except Exception:
                    # If the loopback to be deleted is invalid
                    logging.exception(Exception)
                    return 'Invalid loopback'
        # Return the returned XML
        return(xml.dom.minidom.parseString(nc_reply.xml).toprettyxml())


api.add_resource(Loopback, "/loopback/<string:name>")

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, debug=True)
