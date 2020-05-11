import boto3

### Twitter API Keys
client_key = 'yourKEYhere'
client_secret = 'yourSECREThere'

###Aws DB Config
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('aws_blog_twitter')
