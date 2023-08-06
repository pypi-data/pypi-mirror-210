This module will help you, to use module from OpenAi.

First, you need to write your API token from OpenAi with "aihelper.token('your token')
Then, you can write any message to ChatGpt 3-5. Use aihelper.message("your message"). Response will be in "chat_response".

Example of code:

import aihelper

aihelper.token("token")
aihelper.message(input(">>> "))
print(chat_response)