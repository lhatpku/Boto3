import boto3

# Root user
'''
aws_mag_con_root = boto3.session.Session(profile_name="root")
sts_con_cli = aws_mag_con_root.client(service_name="sts",region_name="us-east-2")
response = sts_con_cli.get_caller_identity()
print(response)
'''

# ec2 user
aws_mag_con_root = boto3.session.Session(profile_name="ec2_developer")
sts_con_cli = aws_mag_con_root.client(service_name="sts",region_name="us-east-2")
response = sts_con_cli.get_caller_identity()
print(response)
# Get Account ID
print(response.get('Account'))