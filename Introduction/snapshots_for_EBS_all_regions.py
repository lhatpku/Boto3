import boto3

session = boto3.session.Session(profile_name="root")
ec2_client = session.client(service_name="ec2",region_name="us-east-2")

all_regions = []
for each_region in ec2_client.describe_regions()['Regions']:
    all_regions.append(each_region.get('RegionName'))

for each_region in all_regions:

    print("Working on {}".format(each_region))

    ec2_client = session.client(service_name="ec2",region_name=each_region)
    list_of_volids = []

    f_prod_bkp = {"Name":"tag:Prod","Values":['backup','Backup']}

    paginator = ec2_client.get_paginator("describe_volumes")
    
    for each_page in paginator.paginate(Filters=[f_prod_bkp]):
        for each_vol in each_page['Volumes']:
            list_of_volids.append(each_vol['VolumeId'])

    snapids = []
    for each_volid in list_of_volids:
        print ("Taking snap of {}".format(each_volid))
        res = ec2_client.create_snapshot(
            Description="Taking snap with Lambda and cw",
            VolumeId = each_volid,
            TagSpecifications = [ 
                {
                    'ResourceType':'snapshot',
                    'Tags':[
                        {
                            'Key': 'Delete-on',
                            'Value': '90'
                        }
                    ]
                }
            ]
        )
        snapids.append(res.get('SnapshotId'))

    waiter = ec2_client.get_waiter("snapshot_completed")
    waiter.wait(SnapshotIds = snapids)

    print("Successfully completed snaps for the volumes of {}".format(list_of_volids))
