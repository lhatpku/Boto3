import boto3
aws_mag_con=boto3.session.Session(profile_name="root")
ec2_con_re=aws_mag_con.resource(service_name="ec2",region_name="us-east-2")
sts_con_cli=aws_mag_con.client(service_name="sts",region_name="us-east-2")

response=sts_con_cli.get_caller_identity()
my_own_id=response.get('Account')

f_size={"Name":"volume-size","Values":['8']}  # The volume size is 8 Gibs

for each_snap in ec2_con_re.snapshots.filter(OwnerIds=[my_own_id],Filters=[f_size]):
	print(each_snap) 