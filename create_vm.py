import googleapiclient.discovery
from six.moves import input
from oauth2client.client import GoogleCredentials
from google.cloud import compute_v1

# compute = googleapiclient.discovery.build('compute', 'v1')
credentials = GoogleCredentials.get_application_default()
service = googleapiclient.discovery.build('compute', 'v1', credentials = credentials)
compute_client = compute_v1.ZonesClient()

# List all regions
regions = compute_client.list(project='core-verbena-328218')

'''
Machine Type: g2-standard-4
GPU: nvidia-l4
Operating System: Deep Learning on Linux
Version: Deep Learning VM with CUDA 11.8 M116
'''
def create_instance(service, project, region, zone, name):
    # image_response = compute.images().getFromFamily(
    #     project='debian-cloud', family='debian-9').execute()
    # source_disk_image = image_response['selfLink']
    
    machine_type = "projects/core-verbena-328218/zones/%s/machineTypes/g2-standard-4" % zone
    accelaratorType = "projects/core-verbena-328218/zones/%s/acceleratorTypes/nvidia-l4" % zone
    
    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': "projects/ml-images/global/images/c0-deeplearning-common-gpu-v20240128-debian-11-py310",
                }
            },
            
        ],
        "guestAccelerators": [
            {
            "acceleratorCount": 1,
            "acceleratorType": accelaratorType,
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {
          "name": "External NAT",
          "networkTier": "PREMIUM"
        }
            ],
            "stackType": "IPV4_ONLY",
             "subnetwork": "projects/core-verbena-328218/regions/%s/subnetworks/default" % region
        }],
    
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        'scheduling': {
            'onHostMaintenance': 'TERMINATE'  # Disable live migration
        }
       
        
    }
    
    
    return service.instances().insert(
        project = project,
        zone = zone,
        body = config).execute()
    
    
def delete_instance(service, project, zone, name):
    return service.instances().delete(
        project = project,
        zone = zone,
        instance = name
    ).execute()
    
project_name = 'core-verbena-328218'
instance_name = 'tested'




# List all zones within the region
zones = compute_client.list(project='core-verbena-328218')
for zone in zones:
    # print(f"  Zone: {zone.name}")
    region = zone.name[:-2]
    try:
        create_instance(service, project_name, region ,zone.name, instance_name)
        print(f'Instance created successfully in the region: {zone.name}  \n \n')
        # delete_instance(service, project_name, zone.name, instance_name)
        
    except:
        print(f'A g2-standard-4 VM instance with 1 nvidia-l4 accelerator(s) is currently unavailable in the Region: {region} Zone: {zone.name}') 
# create_instance(service, project_name, 'us-east1', 'us-east1-d', 'tested')