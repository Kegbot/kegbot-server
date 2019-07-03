from channels import Group


def ws_connect(message, api_endpoint):
    if api_endpoint == 'events':
        message.reply_channel.send({"accept": True})
        Group('api-%s' % api_endpoint).add(message.reply_channel)

def ws_disconnect(message, api_endpoint):
    Group('api-%s' % api_endpoint).discard(message.reply_channel)
