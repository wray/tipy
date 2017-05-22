import os
import sys
import time
import boto3
from boto3.dynamodb.conditions import Key
from slackclient import SlackClient

import bot_id

# constants
INIT_PROMPT = 'color'
try:
    AT_BOT = "@" + bot_id.get_id()
    CHANNEL = bot_id.get_group_id()
    print(CHANNEL)
except TypeError:
    pass

# connect to Dynamo
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(bot_id.CHANNEL_NAME + '_prompts')

# instantiate client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

prompts = {}

def decipher_intent(prompt_name, user_response):
    print(prompt_name,user_response)

    #node = monty_response[prompt_name]
    node = table.query(
        KeyConditionExpression=Key('prompt_now').eq(prompt_name)
        )['Items'][0]['prompt']
    
    # Essentially, return next prompt
    if not user_response:
        return prompt_name, node['text'], True if len(node['responses']) == 0 else False
    else:
        for resp in node['responses'].keys():
            response = node['responses'][resp]
            if response['utterances'] in user_response:
                return decipher_intent(response['next_prompt'],None)
        return (prompt_name,'Invalid Response: ' + node['text'],False)
    

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid prompts. If so, then acts on the command/prompt. If not,
        returns back what it needs for clarification.
    """

    try:
        prompt_name = INIT_PROMPT if not prompts.has_key(channel) else prompts[channel]
        prompt_name, prompt, end_session = decipher_intent(prompt_name,command)
        prompts[channel] = prompt_name if not end_session else prompts.pop(channel)
        bot_response = prompt        

    except:
        bot_response = str(sys.exec_info()[0])

    print("["+bot_response+"]")
    
    if len(bot_response) == 0:
        response = "Reset to top of tree."

    api_response = slack_client.api_call("chat.postMessage", channel=channel,
                                    text=bot_response, as_user=True)
    print(api_response)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    print(output_list)
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            print(command,channel)
            if command and channel:
                handle_command(command, channel)
                
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



