# aws-crossaccount

Cross Account Access example

This example python script (crossaccount.py) shows an example of using an IAM user in one account to assume a role in another and use the permissions attached to that role.

I've also done a writeup on Cross Account roles using this code as [a blog post](https://blog.johnwalker.tech/aws-cross-account-role-access-using-python)

To use:

prerequisites: python3, pip3

- (Optional) set up a virtual env environment
  - In the directory where the code is located run:
    - python3 -m venv .env
    - source .env/bin/activate
    - to exit the virtual env type deactivate when not using
- install the requirements (boto3 mainly)
  - pip3 install -r requirements.txt

- In AWS Target Account, create cross account role
  - The role should have a trusted entity of your source account
  - The role should have an ExternalID. This is a string you should create, it can be random
  - Take note of the Role ARN, you'll need this both in the script and in setting up the next IAM role

- In AWS Source Account, create IAM user with access to the sts:AssumeRole action. An example policy block is below. The resource is the RoleArn from the step above

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::123456789012:role/TargetAccountRole"
        }
    ]
}
```

To then use the code below you can get the parameters by calling the script with --help

```bash
python3 crossaccount.py --help
```

As a full example, once you have the credentials set up you can run:

```bash
python3 crossaccount.py --profile=prod --rolearn=arn:aws:iam::123456789012:role/TargetAccountRole --externalid=myexternalid --sessionname=devsession
```

Replacing the parameters to match your profile name, RoleARN, ExternalId and sessionname
