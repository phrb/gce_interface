import sys
import time

from six.moves import input
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import *

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
        "projects/debian-cloud/global/images/debian-7-wheezy-v20150320"
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
    sys.stdout.write('Waiting for operations to finish')
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

def run(project, zone, instance_name):
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)

    print('Checking Firewall allow-tcp rule')
    add_firewall_tcp_rule(compute, project, '8080')

    print('Creating instance.')

    operation = create_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, [operation['name']])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))

    for instance in instances:
        print('Instance running at IP: ')
        print(' - ' + get_natIP(instance))

    print('Press [ENTER] to kill instance.')
    input()

    print('Deleting instance.')
    operation = delete_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, [operation['name']])

def main():
    project = "just-clover-107416"
    zone = "us-central1-f"
    instance_name = 'demo-instance'
    run(project, zone, instance_name)

if __name__ == '__main__':
    main()
