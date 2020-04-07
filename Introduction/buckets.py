import boto3

custom_session = boto3.session.Session(profile_name="s3_developer")


s3_re = custom_session.resource(service_name="s3",region_name="us-east-2")
print("Using Resource Object")
for each_bucket in s3_re.buckets.all():
    print(each_bucket)


s3_cli = custom_session.client(service_name="s3",region_name="us-east-2")
print("Using Client Object")
for each_bucket in s3_cli.list_buckets().get('Buckets'):
    print(each_bucket.get('Name'))

