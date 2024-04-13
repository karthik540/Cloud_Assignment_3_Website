import json
import logging
import boto3
from pip._vendor import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize Lex client
lex_client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):
    
    def get_labels(query):
        
        response = lex_client.recognize_text(
            botId='F3LCI14GEZ',  # Your bot ID
            botAliasId='TSTALIASID',  # Your bot alias ID
            localeId='en_US',  # The locale
            sessionId="test_session",  # A session ID for your application, can be a random or specific string
            text=query  # The user input text
        )

        print("PRINTING")
        print(response)

        labels = []
        

        if 'interpretations' not in response:
            print("No interpretations found in the response.")
            return labels

        # Loop through each interpretation in the response
        for interpretation in response['interpretations']:
            intent = interpretation.get('intent', {})
            slots = intent.get('slots', {})
            for slot_key, slot_value in slots.items():
                # Check if the slot contains a value and if that value has an 'interpretedValue'
                if slot_value and 'value' in slot_value and 'interpretedValue' in slot_value['value']:
                    labels.append(slot_value['value']['interpretedValue'])

        #If no labels were found
        if not labels:
            print("No valid slots with labels found in the response.")
        
        print("LABELS")
        print(labels)
        return labels

    # Example usage of get_labels
    q1 = "birds and trees"
    labels_response = get_labels(q1)

    # Construct and return the response
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'statusCode': 200,
        'body': json.dumps("All good lads")
    }
-------


import json
import logging
import boto3

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize Lex client
lex_client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):

    # Function to extract labels
    def get_labels(query):
        # Send the query to Lex and get a response
        response = lex_client.recognize_text(
            botId='F3LCI14GEZ',  # Your bot ID
            botAliasId='TSTALIASID',  # Your bot alias ID
            localeId='en_US',  # The locale ID
            sessionId="test_session",  # Session ID
            text=query  # The user input
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

    
    # Get labels from the query
    labels_response = get_labels("I want photos of dogs")
    

    
    # Construct and return the response
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'statusCode': 200,
        'body': json.dumps({
            "message": "Processed the Lex response successfully",
            "labels": labels_response
        })
    }
