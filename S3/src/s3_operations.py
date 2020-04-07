import boto3
import json
import os
import threading 
import sys

from boto3.s3.transfer import TransferConfig

BUCKET_NAME = 'haolu-boto3-s3-2020'
WEBSITE_BUCKET_NAME = 'lhatpku-aws.com'

def s3_client():
    s3 = boto3.client('s3')
    return s3

def s3_resource():
    s3 = boto3.resource('s3')
    return s3

'''
Create bucket and assign bucket policy
'''
def create_bucket(bucket_name):
    return s3_client().create_bucket(
        Bucket = bucket_name,
        CreateBucketConfiguration = {
            'LocationConstraint':'us-east-2'
        }
    )

def create_bucket_policy():
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AddPerm",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:*"],
                "Resource": ["arn:aws:s3:::haolu-boto3-s3-2020/*"]
            }
        ]
    }

    policy_string = json.dumps(bucket_policy)

    return s3_client().put_bucket_policy(
        Bucket = BUCKET_NAME,
        Policy = policy_string
    )

''' 
List buckets
'''
def list_buckets():
    return s3_client().list_buckets()

''' 
Get the policy of a certain bucket
'''
def get_bucket_policy():
    return s3_client().get_bucket_policy(Bucket=BUCKET_NAME)

'''
Get the bucket encryption
'''
def get_bucket_encryption():
    return s3_client().get_bucket_encryption(Bucket=BUCKET_NAME)

'''
Update bucket policy
'''
def update_bucket_policy(bucket_name):
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': [
                    's3:DeleteObject',
                    's3:GetObject',
                    's3:PutObject'
                ],
                'Resource':'arn:aws:s3:::'+bucket_name+'/*'
            }
        ]
    }

    policy_string = json.dumps(bucket_policy)

    return s3_client().put_bucket_policy(
        Bucket = bucket_name,
        Policy = policy_string
    )

'''
Provide server side encryption
'''
def server_side_encrypt_bucket():
    return s3_client().put_bucket_encryption(
        Bucket = BUCKET_NAME,
        ServerSideEncryptionConfiguration = {
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm':'AES256'
                    }
                }
            ]
        }
    )
'''
Delete the bucket
'''
def delete_bucket():
    return s3_client().delete_bucket(Bucket=BUCKET_NAME)

'''
Upload Small file
'''
def upload_small_file():
    file_path = os.path.join(os.path.dirname(__file__),'readme.txt')
    return s3_client().upload_file(file_path,BUCKET_NAME,'readme.txt')

'''
Upload Large File
'''
def upload_large_file():
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)
    file_path = os.path.join(os.path.dirname(__file__),'python_data_science.pdf')
    key_path = 'multipart_files/python_data_science.pdf'

    s3_resource().meta.client.upload_file(file_path,BUCKET_NAME,key_path,
                                            ExtraArgs={'ACL':'public-read','ContentType':'text/pdf'},
                                            Config=config,
                                            Callback=ProgressPercentage(file_path))

class ProgressPercentage(object):
    def __init__(self,filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self,bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100 
            sys.stdout.write(
                "\r%s %s / %s (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size, percentage
                )
            )
            sys.stdout.flush()

'''
Read Objects and Files
'''
def read_object_from_bucket():
    object_key = 'readme.txt'
    return s3_client().get_object(Bucket=BUCKET_NAME,Key=object_key)

'''
Versioning Bucket Files
'''
def version_bucket_files():
    s3_client().put_bucket_versioning(
        Bucket = BUCKET_NAME,
        VersioningConfiguration = {
            'Status': 'Enabled'
        }
    )

'''
Lifecycle Policy
'''
def put_lifecycle_policy():
    '''
    Refer: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_lifecycle
    '''
    lifecycle_policy = {
        "Rules":[
            {
                "ID": 'Move readme file to Glacier',
                "Prefix": "readme",
                "Status": "Enabled",
                "Transitions": [
                    {
                        "Date": "2020-04-06T00:00:00.000Z",
                        "StorageClass": "GLACIER"
                    }
                ]
            },
            {
                "Prefix": "",
                "Status": "Enabled",
                "NoncurrentVersionTransitions": [
                    {
                        "NoncurrentDays": 2,
                        "StorageClass": "GLACIER"
                    }
                ],
                "ID": "Move old versions to Glacier"
            }
        ]
    }
    s3_client().put_bucket_lifecycle_configuration(
        Bucket = BUCKET_NAME,
        LifecycleConfiguration = lifecycle_policy
    )

'''
Static Website
'''
def host_static_website():
    s3 = boto3.client('s3',region_name='us-east-2')

    s3.create_bucket(
        Bucket = WEBSITE_BUCKET_NAME,
        CreateBucketConfiguration = {
            'LocationConstraint': 'us-east-2'
        }
    )

    update_bucket_policy(WEBSITE_BUCKET_NAME)

    website_configuration = {
        'ErrorDocument': {'Key':'error.html'},
        'IndexDocument': {'Suffix':'index.html'}
    }

    s3_client().put_bucket_website(
        Bucket = WEBSITE_BUCKET_NAME,
        WebsiteConfiguration = website_configuration
    )

    index_file = os.path.join(os.path.dirname(__file__),'index.html')
    error_file = os.path.join(os.path.dirname(__file__),'error.html')

    s3_client().put_object(Bucket=WEBSITE_BUCKET_NAME,ACL='public-read',Key='index.html',
                            Body=open(index_file).read(),ContentType='text/html')
    s3_client().put_object(Bucket=WEBSITE_BUCKET_NAME,ACL='public-read',Key='error.html',
                            Body=open(error_file).read(),ContentType='text/html')

def route_53_record_for_s3_website():
    website_dns_name = "s3-website.us-east-2.amazonaws.com"
    redirect_dns_name = "s3-website.us-east-2.amazonaws.com"

    route53 = boto3.client('route53')

    domain = WEBSITE_BUCKET_NAME
    www_redicrect = 'www.'+WEBSITE_BUCKET_NAME

    change_batch_payload = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': 'Z2O1EMRO9K5GLX', # https://docs.aws.amazon.com/general/latest/gr/s3.html
                        'DNSName': website_dns_name,
                        'EvaluateTargetHealth': False
                    }
                }
            },
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': www_redicrect,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': 'Z2O1EMRO9K5GLX',
                        'DNSName': redirect_dns_name,
                        'EvaluateTargetHealth': False
                    }
                }
            }
        ]
    }

    return route53.change_resource_record_sets(
        HostedZoneId = 'Z2Q0BALH33K6BV',
        ChangeBatch=change_batch_payload
    )

                                    
if __name__ == '__main__':
    
    # print(create_bucket(BUCKET_NAME))
    # print(create_bucket_policy())
    
    # print(list_buckets())
    
    # print(get_bucket_policy())

    # print(get_bucket_encryption())

    # print(update_bucket_policy(BUCKET_NAME))

    # print(server_side_encrypt_bucket())

    # print(delete_bucket())

    # upload_small_file()

    # upload_large_file()

    # print(read_object_from_bucket())

    # put_lifecycle_policy()

    # host_static_website()

    route_53_record_for_s3_website()