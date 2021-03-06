from discord import Webhook, RequestsWebhookAdapter, Embed
import json

with open('./configuration.json') as json_file :
    config = json.load(json_file)

WEBHOOKS_TO_POST = [config.get("main-server-webhook")]
# WEBHOOKS_TO_POST = ["https://discordapp.com/api/webhooks/807510380380684308/7giR3QmowgmXGv1F1ZgrI-wxpzpYSYAuvIE7Efv3YJCK7dVURNxWoM0LA4C0OhP27tde"]

def sendWebhookMessage(username: str, avatar_url: str, content=None):
    for webhook in WEBHOOKS_TO_POST:
        print("Sending to Webhook " +  str(webhook) + " content: " + str(content))
        send_the_message(username, avatar_url, webhook, content=content)


def sendWebhookListEmbeds(username: str, avatar_url: str, embeds, content=None):
    for webhook in WEBHOOKS_TO_POST:
        print("Sending an embed to " + str(webhook))
        send_the_message(username, avatar_url, webhook, content=None, embeds=embeds)


def send_the_message(username, avatar_url, webhook, content=None, embeds=None):
    
    try:
        if content and not embeds:
            print("sending to webhook " + webhook)
            webhook = Webhook.from_url(url = webhook, adapter = RequestsWebhookAdapter())
            print("Sending to Webhook " +  str(webhook) + " content: " + str(content))
            webhook.send(content, username=username, avatar_url=avatar_url)
        
        else:
            if not content:
                content = ""

            if not avatar_url:
                avatar_url = "https://media.discordapp.net/attachments/306941063497777152/792210065523998740/image.pn"

            print(webhook)
            webhook = Webhook.from_url(url = webhook, adapter = RequestsWebhookAdapter())
            print("Sending to Webhook content: " + str(content))
            webhook.send(content=content, embeds=embeds, username=username, avatar_url=avatar_url)
    except:
        pass