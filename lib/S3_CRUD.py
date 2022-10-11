import os
import json
import boto3
import tempfile

from boto3.session import Session

#  awslocal s3 mb s3://bucket on first load 
os.environ['LOCALSTACK_S3_ENDPOINT_URL'] = 'http://localhost:4566'
os.environ['AWS_ACCESS_KEY_ID'] = 'guest'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'guest'
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-2'


# set up S3 session
session = Session()
if os.environ.get('LOCALSTACK_S3_ENDPOINT_URL'):
    s3 = session.resource("s3", endpoint_url=os.environ.get('LOCALSTACK_S3_ENDPOINT_URL'))
    client = boto3.client('s3',endpoint_url=os.environ.get('LOCALSTACK_S3_ENDPOINT_URL'))
else:
    s3 = session.resource("s3")
    client = boto3.client('s3')


def upload(file):
    s3.Bucket('bucket').upload_file(file.name, os.path.basename(file.name))

    return '{"upload" : "0"}'


def download(bucket, key): 
    s3.Bucket('bucket').download_file(key, '/data/' + str(key))
    return '{"download" : "0"}'


def delete(bucket,key):
    s3.Bucket(bucket).delete_objects(Delete={'Objects': [{'Key': key }]})

    # remove the temporary file after it has been uploaded 
    if os.path.exists('./data/' + str(key)):
        os.remove('./data/' + str(key))   
    return '{"delete" : "0"}'

def list(bucket):
    return client.list_objects(Bucket=bucket, Delimiter='/')






#  aws --endpoint-url=http://localhost:4572 s3 ls s3:<your-bucket-name>
# LIST SCHEMA
# {
#   "Contents": [
#     {
#       "ETag": "\"68b329da9893e34099c7d8ad5cb9c940\"", 
#       "Key": "README.md", 
#       "LastModified": "Fri, 09 Jul 2021 07:24:50 GMT", 
#       "Owner": {
#         "DisplayName": "webfile", 
#         "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
#       }, 
#       "Size": 1, 
#       "StorageClass": "STANDARD"
#     }, 
#     {
#       "ETag": "\"122bcfd265f8a6a1425603a9aa218b68\"", 
#       "Key": "run.sh", 
#       "LastModified": "Fri, 09 Jul 2021 07:23:28 GMT", 
#       "Owner": {
#         "DisplayName": "webfile", 
#         "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
#       }, 
#       "Size": 643, 
#       "StorageClass": "STANDARD"
#     }
#   ], 
#   "Delimiter": "/", 
#   "IsTruncated": false, 
#   "MaxKeys": 1000, 
#   "Name": "bucket", 
#   "ResponseMetadata": {
#     "HTTPHeaders": {
#       "accept-ranges": "bytes", 
#       "access-control-allow-headers": "authorization,content-type,content-length,content-md5,cache-control,x-amz-content-sha256,x-amz-date,x-amz-security-token,x-amz-user-agent,x-amz-target,x-amz-acl,x-amz-version-id,x-localstack-target,x-amz-tagging", 
#       "access-control-allow-methods": "HEAD,GET,PUT,POST,DELETE,OPTIONS,PATCH", 
#       "access-control-allow-origin": "*", 
#       "access-control-expose-headers": "x-amz-version-id", 
#       "connection": "close", 
#       "content-language": "en-US", 
#       "content-length": "864", 
#       "content-type": "application/xml; charset=utf-8", 
#       "date": "Fri, 09 Jul 2021 07:47:30 GMT", 
#       "last-modified": "Fri, 09 Jul 2021 07:24:50 GMT", 
#       "server": "hypercorn-h11", 
#       "x-amz-id-2": "MzRISOwyjmnupD60638E4ADF329467/JypPGXLh0OVFGcJaaO3KW/hRAqKOpIEEp", 
#       "x-amz-request-id": "D60638E4ADF32946"
#     }, 
#     "HTTPStatusCode": 200, 
#     "HostId": "MzRISOwyjmnupD60638E4ADF329467/JypPGXLh0OVFGcJaaO3KW/hRAqKOpIEEp", 
#     "RequestId": "D60638E4ADF32946", 
#     "RetryAttempts": 0
#   }
# }