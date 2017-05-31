import json

from channels import Group
from channels.auth import channel_session_user_from_http
from channels.sessions import channel_session


@channel_session_user_from_http
def ws_connect(message):
    label = message['path'].strip('/').split('/')[0]
    doc_id = message.http_session['doc_id']
    if label == 'doctor':
        Group('doctor{}'.format(doc_id)).add(message.reply_channel)
    message.channel_session['doc_id'] = doc_id
    message.reply_channel.send({"accept": True})


@channel_session
def ws_receive(message):
    doc_id = message.channel_session['doc_id']
    forward_message = json.loads(message['text'])['message']
    Group('doctor{}'.format(doc_id)).send({'text': forward_message})


@channel_session
def ws_disconnect(message):
    doc_id = message.channel_session['doc_id']
    Group('doctor{}'.format(doc_id)).discard(message.reply_channel)


channel_routing = {
    'websocket.connect': ws_connect,
    'websocket.receive': ws_receive,
    'websocket.disconnect': ws_disconnect,
}
