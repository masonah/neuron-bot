import os
import json
import logging

# from db_interface import DBInterface
from flask import current_app as app
from flask import Flask, request, make_response, Response
# from .models import db, User
from .db_interface import DBInterface
from .messages import Messages

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

from slashCommand import Slash

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_SIGNATURE = os.environ['SLACK_SIGNATURE']
slack_client = WebClient(SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNATURE)

logging.basicConfig(level=logging.DEBUG)
db = DBInterface()
messages = Messages()
# app = Flask(__name__)
BOT_ID = slack_client.api_call('auth.test')['user_id']


@app.route("/slack/event", methods=["POST"])
def handle_event():
    # ===== Verify Signature =====#
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response('invalid request', 403)
    else:
        slack_event = request.get_json()

        slack_event_type = slack_event['type']

        # ===== Check if Slack challenge ===== #
        # Needed to verify URL in slack
        if slack_event_type == 'url_verification':
            return make_response(slack_event['challenge'], 200, {'Content-type': 'text/plain'})
        elif slack_event_type == 'event_callback':
            handle_event_callback(slack_event['event'])
            return make_response('', 200)
        else:
            print('unknown event')
            return make_response('unknown event type', 500)
    return make_response('', 200)


# ===== used for interactive actions, like using modals ===== #
@app.route("/slack/interactive", methods=["POST"])
def handle_interactive():
    print('interactive')

    # ===== Verify Signature ===== #
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response('invalid request', 403)
    else:
        payload = json.loads(request.form['payload'])
        payload_type = payload['type']

        if payload_type == 'view_submission':
            # ===== modal submission ===== #
            submission_values = payload['view']['state']['values']
            user_values = payload['user']

            # ===== NEED TO SANITIZE ALL USER INPUT ===== #

            # ===== need to check type of modal based on block_ids ===== #

            first_name = submission_values['ob_first_name']['first_name']['value']
            last_name = submission_values['ob_last_name']['last_name']['value']
            email = submission_values['ob_email']['email']['value']
            slack_user_id = user_values['id']
            # ===== CREATE USER IN DATABASE ===== #
            user = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "slack_user_id": slack_user_id,
            }
            # ===== LOOK FOR SQL EXCEPTION FOR UNIQUE SLACK ID ===== #
            db_user = db.create_user(user)
            # print(f"{db_user} created.")

            messages.send_intro_message(slack_client, first_name, slack_user_id)
        else:
            print('unknown interaction')
            return make_response('unknown event type', 500)
    return make_response('', 200)


# ===== used for onboard slash command, needed to get user consent to start onboarding ===== #
@app.route("/slack/onboard", methods=["POST"])
def handle_command():
    print('onboard command')
    # ===== Verify Signature ===== #
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response('invalid request', 403)
    else:
        # ===== SEARCH FOR USER FIRST TO VERIFY NOT IN DB (DUPLICATE ONBOARD EVENT) ===== #
        user_id = request.form.get('user_id', None)
        channel_id = request.form.get('channel_id', None)
        trigger_id = request.form.get('trigger_id', None)

        onboard(user_id, channel_id, trigger_id)
        return make_response('', 200)


def handle_event_callback(event):
    if BOT_ID == event['user']:
        # we don't want to respond to messages from the bot itself
        return make_response('', 200)
    elif event['type'] == 'message':
        # get user and check onboard status
        messages.handle(slack_client, event)
        return make_response('', 200)
    # elif event['type'] == 'reaction': #look for reactions to previous message (use timestamp)
    elif event['type'] == 'app_home_opened':
        handle_app_home_opened(event)
    else:
        print(event)
        return make_response('not message type', 500)
    return make_response('', 200)


def handle_app_home_opened(event):
    print('app opened')

    slack_user_id = event['user']
    # ===== need to determine if first open for user onboarding and instruction ===== #
    user = db.get_user_by_slack_user_id(slack_user_id)

    # user = db_interface.get_user_with_slack_id(slack_user_id)

    # user not found in DB, or needs to be onboarded
    if user is None:
        # new user, tell them to do /onboard command
        messages.send_direct_message(slack_client, 'Welcome to Neuron! Use the /onboard command to get started.', event['channel'])
    else:
        # response will get sent to event route, where we'll need to parse messages
        print(user)
        messages.send_direct_message(slack_client, f'Hi {user.first_name}, what can I help you with?', event['channel'])


def onboard(user_id, channel_id, trigger_id):
    # ===== open view of onboard modal in slack channel, response goes to /slack/interactive endpoint ===== #
    try:
        slack_client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "Onboarding",
                    "emoji": True
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit",
                    "emoji": True
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                    "emoji": True
                },
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Hi! Please enter the following information to start using Neuron.",
                            "emoji": True
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "ob_first_name",
                        "element": {
                            "action_id": "first_name",
                            "type": "plain_text_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "First name",
                            "emoji": True
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "ob_last_name",
                        "element": {
                            "action_id": "last_name",
                            "type": "plain_text_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Last name",
                            "emoji": True
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "ob_email",
                        "element": {
                            "action_id": "email",
                            "type": "plain_text_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Email",
                            "emoji": True
                        }
                    }
                ]
            }
        )
        return make_response('', 200)
    except SlackApiError as err:
        code = err.response['error']
        return make_response(f"Failed to open onboarding modal due to {code}", 200)

    # data = {
    #     'email':'',
    #     'first_name':'',
    #     'last_name':'',
    #     'org':'',
    #     'slack_user_id':event['user']
    # }
    # user = db_interface.create_user(data)
    # first time user, needs to be created
    # messages.send_direct_message('Welcome to Neuron! What is your first and last name?', event)
    # return make_response('', 200)


# Start the Flask server
# if __name__ == "__main__":
#     commander = Slash("Hey there! It works.")
#     app.run(debug=True)
