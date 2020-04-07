import boto3
from pprint import pprint

aws_mag_con = boto3.session.Session(profile_name="root")

# IAM, EC2 and S3 Console
iam_con_cli = aws_mag_con.client(service_name="iam",region_name="us-east-2")
ec2_con_cli = aws_mag_con.client(service_name="ec2",region_name="us-east-2")
s3_con_cli = aws_mag_con.client(service_name="s3",region_name="us-east-2")

'''
Display all IAM Users
EC2 Instances
and S3 Buckets
'''
# List all iam users using client object
response_users = iam_con_cli.list_users()
# pprint(response_users['Users'])

# List all ec2 instance ids
response_ec2 =  ec2_con_cli.describe_instances()
for each_item in response_ec2['Reservations']:
    for each_instance in each_item['Instances']:
        print(each_instance['InstanceId'])
    print('-'*20)

