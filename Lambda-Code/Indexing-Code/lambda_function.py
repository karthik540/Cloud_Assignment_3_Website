import json
import urllib.parse
import boto3
import datetime
from pip._vendor import requests
import random
import base64

# Initialize AWS clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

# Added a comment

# Elasticsearch config
ES_URL = "https://search-photos-y2ghq7tpe3y4dciyevicpetcjq.aos.us-east-1.on.aws"
ES_INDEX = 'photos'  # Update with your Elasticsearch index name
ES_USER = 'cloud-ass1'
ES_PASSWORD = 'Cloud-ass1'
region = 'us-east-1'  # Adjust to your AWS region

headers = {"Content-Type": "application/json"}

print('Loading function')

def lambda_handler(event, context):
    # Extract bucket name and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    response = s3.get_object(Bucket=bucket, Key=key)
    
    base64_image=str(response['Body'].read())
    base64_image = base64_image.split("base64,")[1]
    base64_image = base64_image[:-1]
    
    print(f"base64 Image: {base64_image}")
    
    
    decoded_image = base64.b64decode(base64_image)
    
    print(f"decoded image: {decoded_image}")
    
    
    rec_response = rekognition.detect_labels(
        Image={'Bytes':decoded_image}, 
        MaxLabels=5
        )
    
    print(rec_response)
   
    metadata = s3.head_object(Bucket=bucket, Key=key)
    print(f"Metadata response = {metadata}")
    custom_labels_list = metadata.get('Metadata', {}).get('customlabels', '').split(',')
    
    print(f"custom labels: {custom_labels_list}")
    
    labels = [label['Name'] for label in rec_response['Labels']]
    if len(custom_labels_list) > 0:
        labels.append(custom_labels_list[0])
    print("Detected Labels:", labels)
    
    
    document = {
        "objectKey" : key,
        "bucket" : bucket,
        "createdTimestamp" : str(datetime.datetime.now()),
        "labels" : labels
    }
    
    print(document)
    
    index_number = random.randint(10000000, 99999999)
    print(f"{ES_URL}/{ES_INDEX}/_doc/{index_number}")
    es_response = requests.put(f"{ES_URL}/{ES_INDEX}/_doc/{index_number}?pretty",auth=(ES_USER, ES_PASSWORD), headers=headers, data=json.dumps(document))
    
    print(f"ES response : {es_response}")
    
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'statusCode': 200,
        'body': ""
    }
