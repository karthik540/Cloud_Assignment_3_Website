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
    
    '''
    response = rekognition.detect_labels(
            Image={'Bytes':decoded_image},
            MaxLabels=5
        )
    '''
    print(rec_response)
    
    
    
    
    metadata = s3.head_object(Bucket=bucket, Key=key)
    print(f"Metadata response = {metadata}")
    custom_labels = metadata.get('Metadata', {}).get('customlabels', '').split(',')
    
    print(f"custom labels: {custom_labels}")
    
    labels = [label['Name'] for label in rec_response['Labels']]
    if len(custom_labels) > 0:
        labels.append(custom_labels[0])
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
    '''
    base64_image=str(response['Body'].read())
    
    print(response)
    print(base64_image)
    
    base64_image = base64_image.split("base64,")[1]
    base64_image = base64_image[:-1]
    
    print(f"before encoding : {base64_image}")
    
    
    base64_image = base64_image.encode('ascii')
    
    print(f"after encoding : {base64_image}")
    decoded_image = base64.b64decode(base64_image)
    print("image")
    print(decoded_image)
    
    metadata_response = s3.head_object(Bucket=bucket, Key=key)
    print(f"Metadata response = {metadata_response}")
    
    try:
        # Detect labels in the uploaded image using Rekognition
        
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=80
        )
        
        
        response = rekognition.detect_labels(
            Image={'Bytes':base64_image},
            MaxLabels=5
        )
        
        labels = [label['Name'] for label in response['Labels']]
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
        #response = requests.put(f"{ES_URL}/{ES_INDEX}/_doc/{index_number}?pretty",auth=(ES_USER, ES_PASSWORD), headers=headers, data=json.dumps(document))
        
        print("push response")
        #print(response)
        #print(response.content)
        
        if labels:
            img_paths = get_image_path(labels)
            print(f"Found images: {img_paths}")
        else:
            print("No labels detected that match database criteria.")
        
    except Exception as e:
        print(e)
        raise e
    '''

def get_image_path(labels):
    img_paths = []
    for label in labels:
        path = f"{ES_URL}/{ES_INDEX}/_search?q=labels:{label}"
        response = requests.get(path, auth=(ES_USER, ES_PASSWORD), headers=headers)
        #search_hits = response.json()['hits']['hits']
        search_hits = response.json()
        print("search hits ")
        print(search_hits)
        '''
        for hit in search_hits:
            img_bucket = hit["_source"]["bucket"]
            img_name = hit["_source"]["objectKey"]
            img_link = f'https://s3.amazonaws.com/{img_bucket}/{img_name}'
            img_paths.append(img_link)
        '''
    
    return img_paths
