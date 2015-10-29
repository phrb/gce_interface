import socket
import pickle
import sys
import time

from six.moves import input
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import *
from time import sleep

def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items']

def add_firewall_tcp_rule(compute, project, port):
    try:
        firewall = compute.firewalls().get(project=project,
                                           firewall='allow-tcp').execute()
    except HttpError, err:
        print("Adding TCP rule to project %s" % (project))
        config = {
            'kind': 'compute#firewall',
            'name': 'allow-tcp',
            'sourceRanges': [ '0.0.0.0/0' ],
            'allowed': [{
                          'IPProtocol': 'tcp',
                          'ports': [ port ]
                       }]
        }
        compute.firewalls().insert(project=project, body=config).execute()
        return
    print("Project %s already had a TCP rule" % (project))

def create_instance(compute, project, zone, name):
    source_disk_image = \
        "projects/just-clover-107416/global/images/debian8-opentuner-ready"
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open('startup-script.sh', 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,
        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                # Every project has a default Cloud Storage bucket that's
                # the same name as the project.
                'key': 'bucket',
                'value': project
            }]
        }
    }
    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()

def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()

def wait_for_operation(compute, project, zone, operations):
    sys.stdout.write('Waiting for operation to finish')
    while True:
        results = [compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute() for operation in operations ]

        if all(result['status'] == 'DONE' for result in results):
            print("done.")
            for result in results:
                if 'error' in result:
                    raise Exception(result['error'])
            return result
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)

def get_natIP(instance, interface = 0, config = 0):
    return instance['networkInterfaces'][interface]['accessConfigs'][config]['natIP']

def start_server(instance_ip):
    SERVER_IP      = instance_ip
    SERVER_PORT    = 8080
    BUFFER_SIZE    = 4096

    attempts       = 13
    delay          = 2

    REPO           = " https://github.com/phrb/autotuning-gce.git"
    DIST           = " tuner"

    INTERFACE_PATH = " tuner/rosenbrock/rosenbrock.py"
    INTERFACE_NAME = " Rosenbrock"

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (str(SERVER_IP), SERVER_PORT)
    print "Connecting to {0} : {1}".format(SERVER_IP, SERVER_PORT)

    for _ in range(attempts):
        try:
            sock.connect(server_address)
        except Exception as e:
            if e.errno == 106:
                print "Connected."
                break
            else:
                print "Couldn't connect ({0}), trying again.".format(e.errno)
                sleep(delay)
                pass


    msg = "start"
    sock.sendall(msg)

    # START
    sock.recv(BUFFER_SIZE).strip()

    msg = "clone" + REPO + DIST
    sock.sendall(msg)

    # CLONE
    sock.recv(BUFFER_SIZE).strip()
    sock.recv(BUFFER_SIZE).strip()

    msg = "load" + INTERFACE_PATH + INTERFACE_NAME
    sock.sendall(msg)

    # LOAD
    sock.recv(BUFFER_SIZE).strip()
    sock.recv(BUFFER_SIZE).strip()

    return sock


def run(project, zone, instance_names):
    BUFFER_SIZE    = 4096
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)

    print('Checking Firewall allow-tcp rule')
    add_firewall_tcp_rule(compute, project, '8080')

    print('Creating instances.')

    for name in instance_names:
        print "Creating {0}.".format(name)
        operation = create_instance(compute, project, zone, name)
        wait_for_operation(compute, project, zone, [operation['name']])

    instances = list_instances(compute, project, zone)

    sockets   = []

    print('Instances in project %s and zone %s:' % (project, zone))

    for instance in instances:
        print('Instance running at IP: ')
        print(' - ' + get_natIP(instance))

        sockets.append(start_server(get_natIP(instance)))

    print "Checking for instances' server status."
    for sock in sockets:
        msg = "status"
        sock.sendall(msg)
        print "sending: " + msg
        print (sock.recv(BUFFER_SIZE).strip())


    print('Test complete. Press [ENTER] to kill instances.')
    input()

    print('Deleting instances.')
    for name in instance_names:
        operation = delete_instance(compute, project, zone, name)
        wait_for_operation(compute, project, zone, [operation['name']])

def main():
    project = "just-clover-107416"
    zone = "us-central1-f"
    instances = []

    for i in range(8):
        instances.append("instance-{0}".format(i))

    run(project, zone, instances)

if __name__ == '__main__':
    main()
