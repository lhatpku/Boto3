import boto3 
import time
aws_con=boto3.session.Session(profile_name="ec2_developer")
ec2_con_re=aws_con.resource(service_name="ec2",region_name="us-east-2")
ec2_con_cli=aws_con.client(service_name="ec2",region_name="us-east-2")

instance_Id = input('Input the Instance ID: ')

'''
my_inst_ob=ec2_con_re.Instance(instance_Id)
print("Starting given instance....")
my_inst_ob.start()
my_inst_ob.wait_until_running()  #Resource waiter waits for 200sec(40 checks after every 5 sec)
print("Now your instance is up and running")
'''

'''
print("Starting ec2 instace...")
ec2_con_cli.start_instances(InstanceIds=[instance_Id]) # Can start multiple instances
waiter=ec2_con_cli.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_Id]) #40 checks after every 15 sec, multiple instances
print("Now your ec2 instace is up and running")
'''


my_inst_ob=ec2_con_re.Instance(instance_Id)
print("Starting given instance....")
my_inst_ob.start()
waiter=ec2_con_cli.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_Id])
print("Now your ec2 instace is up and running")
