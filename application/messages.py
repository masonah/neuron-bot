import logging
from expiringdict import ExpiringDict
from .db_interface import DBInterface

from .routes import app
from flask import Flask, request, make_response, Response

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ===== {user_id:last_message_block_id} to keep track of threading without slamming DB ===== #
# ===== what about replay in the event of a dropped bot message? ===== #
cache = ExpiringDict(max_len=100, max_age_seconds=1800) # 30 min expiry

db = DBInterface()


class Messages():

    def handle(self, client, message):
        text = message['text']
        slack_user_id = message['user']

        # if cache hit = use block_id as key, if miss start over core loop? or have some other trigger?
        # can we use the message table to see last response based on most recent timestamp?
        assert "abc123" in cache, "cache miss?"
        thread = cache[slack_user_id]
        if not thread:
            #cache miss
            print('cache missed')
        elif thread == 'intro_message':
            # ===== how to know what this is an answer to? have unique answer inputs for every prompt? ===== #
            # ===== what about having user respond in a thread to the question? ===== #
            # ===== keep track of last bot message ID in DB? what about cache? this would add a read/write for every message ===== #
            if text == 'Y' or text == 'y':
                self.start_core_loop(client, slack_user_id)
            elif text == 'N' or text == 'n':
                # ===== schedule core message loop for the next morning ===== #
                self.send_direct_message(client, "👋🏽 Ok, we'll try again tomorrow!", message['channel'])
            else:
                self.send_direct_message(client, "👋🏽 I'm not sure what you mean - please choose Y or N", message['channel'])
        elif thread == 'core_message_1':
            # ===== check what answers they provided for core message 1 ===== #
            self.send_direct_message(client, "You answered core message 1!",
                                     message['channel'])
        # ===== how to determine if part of core message loop? handle based on block ids?
        # block ids don't come from messages ===== #

    @staticmethod
    def start_core_loop(client, slack_user_id):
        try:
            # ===== PULL THESE FROM DATABASE BASED (AT RANDOM?) ===== #
            skill_1 = "first skill"
            skill_2 = "second skill"
            skill_3 = "third skill"
            skill_4 = "fourth skill"

            # ===== should we add reactions that they can click in response? ===== #
            response = client.chat_postMessage(
                channel=slack_user_id,
                blocks=[
                    {
                        "type": "section",
                        "block_id": "core_message_1",
                        "text": {
                            "type": "mrkdwn",
                            "text": "🧗‍️ What skills have you used in the last 48 hours?\n\n"
                                    f"1️⃣ {skill_1}\n\n"
                                    f"2️⃣ {skill_2}\n\n"
                                    f"3️⃣ {skill_3}\n\n"
                                    f"4️⃣ {skill_4}\n\n"
                                    "If you’ve used the skill, include the number. For example, 134 if you’ve used "
                                    "SKILL 1, SKILL 3, and SKILL 4."
                        }
                    }
                ]
            )
            block_id = response['message']['blocks'][0]['block_id']
            cache[slack_user_id] = block_id
        except SlackApiError as e:
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            logging.error(e.response)
            return make_response("", e.response.status_code)

    @staticmethod
    def send_direct_message(client, message, channel):
        try:
            # send user a response via DM
            response = client.chat_postMessage(
                # users=event['user'],
                channel=channel,
                text=message
            )
        except SlackApiError as e:
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            logging.error(e.response)
            return make_response("", e.response.status_code)

        # return make_response("", response.status_code)

    @staticmethod
    def send_intro_message(client, first_name, slack_user_id):
        text = db.create_message("intro_message")
        print(f"INTRO MESSAGE\n{text}")
        try:
            response = client.chat_postMessage(
                channel=slack_user_id,
                blocks=[
                    {
                        "type": "section",
                        "block_id": "intro_message",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hi {first_name} :wave:\n\n"
                                    ":thought_balloon: Imagine you have a dedicated skill coach. All they care about is "
                                    "helping you build competency in the highest value skills "
                                    ":chart_with_upwards_trend: without taking too much time away from your work. "
                                    "They keep track of what skills you’re using, suggest high value skills you may "
                                    "want to consider, and deliver actionable tips to remind you how to get 1% "
                                    "better every day.\n\n"
                                    "We are that skill coach, and we’re here to help you grow, achieve, and maximize "
                                    "your potential as an engineer! :rocket:\n\n"
                                    "• 3 quick questions about your work \n • 1 short piece of actionable content \n"
                                    " • 1 concrete example curated from the Neuron community\n\n"
                                    "Ready to get started? Reply Y or N"
                        }
                    }
                ]
            )
            block_id = response['message']['blocks'][0]['block_id']
            cache[slack_user_id] = block_id
        except SlackApiError as e:
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            logging.error(e.response)
            return make_response("", e.response.status_code)



