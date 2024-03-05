import configparser
import json
from datetime import date, datetime
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)

async def main():
    url = input("Введите ссылку на чат или канал: ")
    channel = await client.get_entity(url)
    await dump_all_participants(channel), dump_all_messages(channel)

async def dump_all_participants(channel):
    offset_user = 0
    limit_user = 100
    all_participants = []

    while True:
        participants = await client(GetParticipantsRequest(
            channel, ChannelParticipantsSearch(''), offset_user, limit_user, hash=0
        ))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset_user += len(participants.users)

    all_users_details = []
    for participant in all_participants:
        all_users_details.append({
            "id": participant.id,
            "first_name": participant.first_name,
            "last_name": participant.last_name,
            "user": participant.username,
            "phone": participant.phone,
            "is_bot": participant.bot,
        })

    with open("channel_users.json", 'w', encoding="utf8") as f:
        json.dump(all_users_details, f, ensure_ascii=False, indent=4)


async def dump_all_messages(channel):
	offset_msg = 0    #
	limit_msg = 100  

	all_messages = []   
	total_messages = 0
	total_count_limit = 0  

	class DateTimeEncoder(json.JSONEncoder):
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break

	with open('channel_messages.json', 'w', encoding='utf8') as outfile:
		 json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder, indent=4)


async def main():
	url = input("Введите ссылку на канал или чат: ")
	channel = await client.get_entity(url)
	await dump_all_participants(channel)
	await dump_all_messages(channel)


with client:
	client.loop.run_until_complete(main())