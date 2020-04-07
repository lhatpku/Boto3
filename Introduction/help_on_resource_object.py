import boto3
from pprint import pprint

aws_mag_con = boto3.session.Session(profile_name="root")

# IAM, EC2 and S3 Console
iam_con_re = aws_mag_con.resource(service_name="iam",region_name="us-east-2")
ec2_con_re = aws_mag_con.resource(service_name="ec2",region_name="us-east-2")
s3_con_re = aws_mag_con.resource(service_name="s3",region_name="us-east-2")

## IAM Users
# List all iam users
for each_item in iam_con_re.users.all():
    print(each_item.user_name)

'''
for each_item in iam_con_re.users.limit(1):
    print(each_item.user_name)
'''

## S3 Buckets
for each_item in s3_con_re.buckets.all():
    print(each_item.name)