import pprint
import sys
import argparse

import boto3
from botocore.exceptions import ClientError

# Using argparse to parse command line arguments, allows for --help to be used and adding constraints

parser = argparse.ArgumentParser()
parser.add_argument('--profile', '-p', help="The name of the profile stored in the aws credentials file", type=str, required=True)
parser.add_argument('--rolearn', '-r', help="The Role ARN in the target account", type=str, required=True)
parser.add_argument('--externalid', '-e', help="The External ID in the target account role", type=str, required=True)
parser.add_argument('--sessionname', '-s', help="The name you want to give to your session", type=str)

args = parser.parse_args()

# Required parameters
profile = args.profile
rolearn = args.rolearn
externalid = args.externalid

# Optional parameters
if (args.sessionname):
	sessionname = args.sessionname
else:
	sessionname = "newsession"

# Create a new boto3 session using the passed in profile
session = boto3.Session(profile_name = profile)

# Use try / except with the boto3 ClientError exception to catch errors from AWS, such as AccessDenied
# This allows us to provide feedback if the roles or access is not correct (or take other actions)
try: 
	# Use the session to call Secure token Service and assume the role.
	# This allows us to assume the role in the target account and use the permissions attached to it
	sts_client = session.client('sts')
	sts_response = sts_client.assume_role(
		RoleArn = rolearn,
		RoleSessionName = sessionname,
		ExternalId = externalid
	)
except ClientError as error:
	errorcode = error.response['Error']['Code']
	print("Error Assuming Role. Error code:", errorcode)
	sys.exit()

# Get our new temporary credentials. Checking each key is present just to ensure we have what we need
if ("Credentials" in sts_response):
	credentials = sts_response["Credentials"]
	if ("AccessKeyId" in credentials):
		temporary_access_key = credentials["AccessKeyId"]
	if ("SecretAccessKey" in credentials):
		temporary_secret_key = credentials["SecretAccessKey"]
	if ("SessionToken" in credentials):
		temporary_token = credentials["SessionToken"]

if (not temporary_access_key or not temporary_secret_key or not temporary_token):
	print("Error getting Temporary Credentials")
	sys.exit()

# Now we have credentials we can use boto3 as normal and we have the access level attached to the role in the target account
# as an example, for a role set up with the AmazonS3ReadOnlyAccess policy, we can list s3 buckets
try:
	# First we get a new s3 client, passing the temporary credentials in
	s3_client = session.client(
		's3',
		region_name = "eu-west-1",
		aws_access_key_id = temporary_access_key,
		aws_secret_access_key = temporary_secret_key,
		aws_session_token = temporary_token
	)
except ClientError as error:
	errorcode = error.response['Error']['Code']
	print("Error getting remote session using temporary credentials. Error code:", errorcode)
	sys.exit()

try:
	# next we list the buckets. Note that even though we are using the endpoint above in eu-west-1
	# s3 is global, so list buckets will return all buckets.
	# to get just one region, you can call get_bucket_location on each bucket returned and filter by the LocationConstraint 
	response = s3_client.list_buckets()
except ClientError as error:
	errorcode = error.response['Error']['Code']
	print("Error Listing S3 Buckets. Error code:", errorcode)
	sys.exit()

pprint.pprint(response)