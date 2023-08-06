# Telegram Bot API Wrapper
This is a Python wrapper for interacting with the Telegram Bot API. It provides a convenient way to send messages and receive updates from Telegram bots.

## Installation
To use this wrapper, you'll need Python 3.6 or above. You can install it using pip:

`pip install telegram-bot-api-wrapper`
## Usage
1. Import the TelegramClient class:

`from telegram_client import TelegramClient`
2. Create an instance of the TelegramClient class by providing your bot token:
```python
bot_token = 'YOUR_BOT_TOKEN'
client = TelegramClient(bot_token)
```

3. Use the available methods to interact with the Telegram Bot API. For example, to send a message:
```python
chat_id = 'TARGET_CHAT_ID'
message = 'Hello, world!'
client.send_message(chat_id, message)
```
4. To receive new messages, use the get_new_messages method:
```python
new_messages = client.get_new_messages()
for message in new_messages:
    print(message)
```
Refer to the docstrings in the code for more information about each method and its parameters.