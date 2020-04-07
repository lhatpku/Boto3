from src.ec2.vpc import VPC
from src.ec2.ec2 import EC2
from src.client_locator import EC2Client

def main():

    '''
    VPC Set up
    '''
    # Create a VPC 
    ec2_client = EC2Client().get_client()
    vpc = VPC(ec2_client)

    vpc_response = vpc.create_vpc()
    print('VPC Created:' + str(vpc_response))

    # Add name tag to VPC
    vpc_name = 'Boto3-VPC'
    vpc_id = vpc_response['Vpc']['VpcId']
    vpc.add_name_tag(vpc_id,vpc_name)

    # Create and IGM
    igw_response = vpc.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    vpc.attach_igw_to_vpc(vpc_id,igw_id)

    '''
    Public Subnet
    '''
    # Create a public subnet
    public_subnet_response = vpc.create_subnet(vpc_id, '10.0.1.0/24')
    public_subnet_id = public_subnet_response['Subnet']['SubnetId']
    print('Subnet created for VPC ' + vpc_id + ':' + str(public_subnet_response))

    vpc.add_name_tag(public_subnet_id,'Boto3-Public_Subnet')

    # Create a public route table
    public_route_table_response = vpc.create_public_route_table(vpc_id)
    rtb_id = public_route_table_response['RouteTable']['RouteTableId']

    # Adding Internet Gateway to Public Route Table
    vpc.create_igw_route_to_public_route_table(rtb_id,igw_id)

    # Associate Public Subnet with Route Table 
    vpc.associate_subnet_with_route_table(public_subnet_id,rtb_id)

    # Allow auto-assign public ip address for subnet
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id)

    '''
    Private Subnet
    '''
    # Create a Private Subnet 
    private_subnet_response = vpc.create_subnet(vpc_id, '10.0.2.0/24')
    private_subnet_id = private_subnet_response['Subnet']['SubnetId']

    print("Create private subnet "+private_subnet_id+" for VPC "+vpc_id)

    vpc.add_name_tag(private_subnet_id,'Boto3-Private_Subnet') # Add name tag to private subnet

    '''
    EC2 Instances
    '''
    ec2 = EC2(ec2_client)

    # Create a key pair
    key_pair_name = 'Boto3-KeyPair'
    key_pair_response = ec2.create_key_pair(key_pair_name)

    print('Created Key Pair with name '+key_pair_name+':'+str(key_pair_response))

    # Create a Security Group
    public_security_group_name = 'Boto3-Public-SG'
    public_security_group_description = 'Public security group for public subnet internet access'
    public_security_group_response = ec2.create_security_group(public_security_group_name,public_security_group_description,vpc_id)
    public_security_group_id = public_security_group_response['GroupId']
    
    # Add Public Access to Security Group
    ec2.add_inbound_rule_to_sg(public_security_group_id)
    print('Added public access rule to Security Group '+ public_security_group_name)

    user_data = """#!/bin/bash
                yum update -y 
                yum install httpd24 -y
                service httpd start
                chkconfig httpd on
                echo "<html><body><h1>Hello from <b>Boto3</b> using Python!</h1></body></html>" > /var/www/html/index.html
                """
    
    # Launch Instance in Public Subnet
    ami_name = 'ami-0e01ce4ee18447327'
    ec2.launch_ec2_instance(ami_name,key_pair_name,1,1,public_security_group_id,public_subnet_id,user_data)
    print('Launching Public EC2 Instance using AMI '+ami_name)

    # Adding another Security Group for Private EC2 Instance
    private_security_group_name = 'Boto3-Private-SG'
    private_security_group_description = 'Private security group for private subnet internet access'
    private_security_group_response = ec2.create_security_group(private_security_group_name,private_security_group_description,vpc_id)
    private_security_group_id = private_security_group_response['GroupId']

    # Add rule to private security group
    ec2.add_inbound_rule_to_sg(private_security_group_id)

    # Launch Instance in Private Subnet
    ec2.launch_ec2_instance(ami_name,key_pair_name,1,1,private_security_group_id,private_subnet_id,'''''')
    print('Launching Private EC2 Instance using AMI '+ami_name)

def describe_instance():
    ec2_client = EC2Client().get_client()
    ec2 = EC2(ec2_client)
    ec2_responses = ec2.describe_ec2_instances()

    print(str(ec2_responses))

def modify_instance():
    ec2_client = EC2Client().get_client()
    ec2 = EC2(ec2_client)
    
    ec2.modify_ec2_instance('i-015b8168e8a1b0571')

def stop_instance():
    ec2_client = EC2Client().get_client()
    ec2 = EC2(ec2_client)
    
    ec2.stop_instance('i-015b8168e8a1b0571')

def start_instance():
    ec2_client = EC2Client().get_client()
    ec2 = EC2(ec2_client)
    
    ec2.start_instance('i-015b8168e8a1b0571')

def terminate_instance():
    ec2_client = EC2Client().get_client()
    ec2 = EC2(ec2_client)
    
    ec2.terminate_instance('i-015b8168e8a1b0571')


if __name__ == '__main__':
    stop_instance()
    # modify_instance()
    # describe_instance()
    # main()


