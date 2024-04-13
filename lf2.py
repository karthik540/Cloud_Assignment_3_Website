import json
import logging
import boto3
from pip._vendor import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    # Extract the query from the Lex event
    # query = event['currentIntent']['slots']['QuerySlot']  # Assuming a slot named 'QuerySlot'
    query = "Animal"
    
    # Initialize the Lex V2 client
    # lex_client = boto3.client('lexv2-runtime')
    
    # # Call Amazon Lex to recognize the text (use your botId, botAliasId, and localeId)
    # response = lex_client.recognize_text(
    #     botId='F3LCI14GEZ',
    #     botAliasId='TSTALIASID',
    #     localeId='en_US',
    #     sessionId="test_session",  # Use a unique sessionId for your use case
    #     text=query
    # )

    # # Initialize keywords to None
    # q1_keyword = None
    # q2_keyword = None
    
    # # Parse the Lex V2 response to get slot values for q1 and q2
    # for interpretation in response.get('interpretations', []):
    #     intent = interpretation.get('intent', {})
    #     if intent.get('name') == 'SearchIntent':  # Replace with your actual intent name
    #         slots = intent.get('slots')
            
    #         # Extract specific slots q1 and q2 if they exist
    #         q1_slot = slots.get('Query1', {})
    #         q2_slot = slots.get('Query2', {})
            
    #         if q1_slot and 'value' in q1_slot:
    #             q1_keyword = q1_slot['value']['interpretedValue']
    #         if q2_slot and 'value' in q2_slot:
    #             q2_keyword = q2_slot['value']['interpretedValue']
    
    # Elasticsearch credentials and URL
    es_user = "cloud-ass1"
    es_password = "Cloud-ass1"
    es_url = "https://search-photos-y2ghq7tpe3y4dciyevicpetcjq.aos.us-east-1.on.aws"

    # Function to query Elasticsearch with the given keyword
    def query_elasticsearch(keyword):
        response = requests.get(f'{es_url}/_search?q=labels:{keyword}',
                                auth=(es_user, es_password),
                                headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            return response.json()  # Return the JSON response from Elasticsearch
        else:
            raise Exception(f"Error querying Elasticsearch: {response.text}")

    
    logger.debug("#####################")
    logger.debug(query_elasticsearch(query))
    logger.debug("#####################")
    
    # Define missing_keywords_list here to ensure its scope covers both the if-else structure and subsequent code that uses it
    # missing_keywords_list = []

    # If keywords exist, perform a search in Elasticsearch
    # results = []
    # if q1_keyword:
    #     results.append(query_elasticsearch(query))
        
    # if q2_keyword:
    #     results.append(query_elasticsearch(q2_keyword))

    # Construct the response message based on whether results were found
    # message_content = ""
    # if results:
    #     # If there are results, use them in the response message
    #     message_content = f'Elasticsearch results: {json.dumps(results)}'
    # else:
    #     # If there are no results, indicate no keywords were found
    #     if not q1_keyword:
    #         missing_keywords_list.append("q1")
    #     if not q2_keyword:
    #         missing_keywords_list.append("q2")
    #     missing_keywords_str = ", ".join(missing_keywords_list)
    #     message_content = 'No valid keywords were provided to search.' if not missing_keywords_list else f'Could not find keywords for: {missing_keywords_str}'
    
    # print("MESSAGE CONTENT")
    # print(message_content)
    
    # Use the message content in the response
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled' if results else 'Failed',
            'message': {
                'contentType': 'PlainText',
                'content': message_content
            }
        }
    }
