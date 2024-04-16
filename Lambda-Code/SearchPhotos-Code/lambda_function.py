import json
import logging
import boto3
from pip._vendor import requests

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Added a comment

# Initialize Lex client
lex_client = boto3.client('lexv2-runtime')

#ElasticSearch Credentials

ES_URL = "https://search-photos-y2ghq7tpe3y4dciyevicpetcjq.us-east-1.es.amazonaws.com"
ES_USER = 'cloud-ass1'
ES_PASSWORD = 'Cloud-ass1'
headers = {"Content-Type": "application/json"}
host = ES_URL
region = 'us-east-1'

def lambda_handler(event, context):
    print("EVENT")
    print(event)
    # Function to extract labels
    def get_labels(query):
        # Send the query to Lex and get a response
        bot_query = ''
        if len(query) > 1:
            bot_query = f'I want {query[0]} and {query[1]}'
        else:
            bot_query = f'I want {query[0]}'
        print(bot_query)
        response = lex_client.recognize_text(
            botId='F3LCI14GEZ',  # Your bot ID
            botAliasId='TSTALIASID',  # Your bot alias ID
            localeId='en_US',  # The locale ID
            sessionId="test_session",  # Session ID
            text=bot_query  # The user input
        )

        # Log the Lex response
        logger.debug(f"Lex response: {response}")

        # Initialize labels list
        labels = []

        # Process the Lex response
        if 'interpretations' in response:
            for interpretation in response['interpretations']:
                intent = interpretation.get('intent', {})
                slots = intent.get('slots', {})

                # Extract and append Query1
                if 'Query1' in slots and slots['Query1'] is not None:
                    query1_slot = slots['Query1']
                    if 'value' in query1_slot and query1_slot['value'] is not None:
                        label = query1_slot['value'].get('interpretedValue', None)
                        if label is not None:  # Corrected syntax here
                            labels.append(label)

                # Extract and append Query2
                if 'Query2' in slots and slots['Query2'] is not None:
                    query2_slot = slots['Query2']
                    if 'value' in query2_slot and query2_slot['value'] is not None:
                        label = query2_slot['value'].get('interpretedValue', None)
                        if label is not None:  # Corrected syntax here
                            labels.append(label)

        # Fallback splitting if Query2 is not recognized and only one label is present
        if len(labels) == 1:
            parts = labels[0].split(" and ")
            if len(parts) > 1:
                # Replace the single item with two new items
                labels = [parts[0].strip(), parts[1].strip()]
            else:
                # Just in case there's extra whitespace
                labels[0] = labels[0].strip()

        # Log the final labels
        logger.debug(f"Final labels: {labels}")
        return labels
        
    def get_image_path(labels):
        unique_labels = []
        for x in labels:
            if x not in unique_labels:
                unique_labels.append(x)
                
        labels = unique_labels
        
        return_response = []
        
        for label in labels:
            labels_cus = [label]
            label_dictionary = {
                "labels": labels_cus
            }
            path = host + '/_search?q=labels:'+label
            print(path)
            response = requests.get(path, headers=headers,
                                auth=(ES_USER, ES_PASSWORD))
            print("response from ES", response)
            
            dict1 = json.loads(response.text)
            hits_count = dict1['hits']['total']['value']
            print("DICT : ", dict1)
            
            
            for k in range(0, hits_count):
                img_obj = dict1["hits"]["hits"]
                bucket_name = dict1["hits"]["hits"][k]["_source"]["bucket"]
                key_name = dict1["hits"]["hits"][k]["_source"]["objectKey"]
                img_link = 'https://s3.amazonaws.com/' + str(bucket_name) + '/' + str(key_name)
                label_dictionary['url'] = img_link
                break
            return_response.append(label_dictionary)
            
        return return_response
    
    # Get labels from the query
    query = event["multiValueQueryStringParameters"]["q"]
    print(query)
    get_labels_response = get_labels(query)
    
    
    if len(get_labels_response) == 0:
        return
    else:
        return_response = get_image_path(get_labels_response)
        
    final_response = {
        "result" : return_response
    }

    
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'statusCode': 200,
        'body': json.dumps(final_response)
    }
