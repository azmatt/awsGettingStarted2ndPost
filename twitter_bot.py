### Twitter bot for AWS blog series
###

### Import libraries
import base64
import requests
import time
import boto3
from api_keys import *          #### Import API keys
from botocore.exceptions import ClientError


###Begin Twitter prerequisites
key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
b64_encoded_key = base64.b64encode(key_secret)
b64_encoded_key = b64_encoded_key.decode('ascii')

base_url = 'https://api.twitter.com/'
auth_url = '{}oauth2/token'.format(base_url)

auth_headers = {
    'Authorization': 'Basic {}'.format(b64_encoded_key),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

auth_data = {
    'grant_type': 'client_credentials'
}

auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

# Check status code okay
auth_resp.status_code

# Keys in data response are token_type (bearer) and access_token (your access token)
auth_resp.json().keys()

access_token = auth_resp.json()['access_token']

search_headers = {
    'Authorization': 'Bearer {}'.format(access_token)    
}
###End Twitter prerequisites

### Function to send email using AWS SES service

def sendEmail():
	time.sleep(.1)
	# Initial Email Values
	SENDER = "Your Email <youremail@gmail.com>" # The email you verified with AWS
	RECIPIENT = "whatever@gmail.com" #The email getting your alerts
	AWS_REGION = "us-west-2" #Your region
	SUBJECT = "Twitter Bot Alert"

	# The email body for recipients with non-HTML email clients.
	BODY_TEXT = ("Twitter Bot Alert Text")
				
	# The HTML body of the email.
	BODY_HTML = """<html>
	<head></head>
	<body>
     Hit for: {} <br />
     Text: {}  <br />
     ID#: {} <br />
     Created at: {} <br />
     User: {} <br />
	</body>
	</html>
				""".format(str(search_entry), str(x['full_text']), str(x['id']), str(x['created_at']), str(x['user']['screen_name']) )           

	# The character encoding for the email.
	CHARSET = "UTF-8"

	# Create a new SES resource and specify a region.
	client = boto3.client('ses',region_name=AWS_REGION)

	# Try to send the email.
	try:
		response = client.send_email(
			Destination={
				'ToAddresses': [
					RECIPIENT,
				],
			},
			Message={
				'Body': {
					'Html': {
						'Charset': CHARSET,
						'Data': BODY_HTML,
					},
					'Text': {
						'Charset': CHARSET,
						'Data': BODY_TEXT,
					},
				},
				'Subject': {
					'Charset': CHARSET,
					'Data': SUBJECT,
				},
			},
			Source=SENDER,
		)
	# Display an error if something goes wrong.	
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		print("Email sent! Message ID:"),
		print(response['MessageId'])

############End of Email Function


### List of search queries to monitor twitter for
search_queries = ['breach mega.nz -filter:retweets']


while True: ### Main Logic Below
    for search_entry in search_queries:
        print ('Searching For: ' + str(search_entry))
        search_params = {
            'q': search_entry,
            'result_type': 'recent',
            'count': 100,
            'tweet_mode':'extended' ### switches results from text to full text to avoid truncated results
        }

        search_url = '{}1.1/search/tweets.json'.format(base_url)

        search_resp = requests.get(search_url, headers=search_headers, params=search_params)

        search_resp.status_code

        tweet_data = search_resp.json()
        time.sleep(3)


        for x in tweet_data['statuses']:
            try:
                response = table.get_item(Key={ "tweet_id": x['id'] })
                item = response['Item']
                print(str(item) + ' is already in the database.')
            except:
                print('Hit for: ' + str(search_entry))
                print('Text: ' + str(x['full_text']) + '\n')
                print('ID#: ' + str(x['id']) + '\n')  
                print('Created at: ' + str(x['created_at']) + '\n')
                print('User: ' + str(x['user']['screen_name']) + '\n') 
                sendEmail()
                try:
                    table.put_item( Item={'tweet_id': x['id']	} ) 
                except:
                    print('Error in Database Insert')
                print('##################')
                
    print('Waiting Between Runs')        
    time.sleep(120)