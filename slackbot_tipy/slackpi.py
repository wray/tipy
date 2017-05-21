import os
import sys
import time
from slackclient import SlackClient

import bot_id


# constants
try:
    AT_BOT = "@" + bot_id.get_id()
    CHANNEL = bot_id.get_group_id()
    print(CHANNEL)
except TypeError:
    pass

# instantiate client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
        Need to determine an algorithm for student overloaded commands.
    """

    try:
        # get response from db (ti_python.py)
        # response = decipher_intent(prompt,response)
        print('handle_command')

    except:
        response += str(sys.exec_info()[0])

    print("["+response+"]")
    
    if len(response) == 0:
        response = "Reset to top of tree."

    # Split responses by %% and then add a delay in between
    # First test with separate postings, better approach will be
    # to use the chat.update command which will requires the ts back
    # from the orginial post.

    responses = response.split('%%')

    for response in responses:
    
        api_response = slack_client.api_call("chat.postMessage", channel=channel,
                                text=response, as_user=True)
        print(api_response)
        time.sleep(0.5)

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
            if output and 'text' in output and output['channel'] == CHANNEL:
                print("Entering Mission Control")
                #joe.slacklib.blink_green()
                wray.slacklib.mission_control(bot_id,output)

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



