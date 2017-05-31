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
    print label, doc_id, 'connected'
    message.channel_session['doc_id'] = doc_id
    message.reply_channel.send({"accept": True})


@channel_session
def ws_receive(message):
    doc_id = message.channel_session['doc_id']
    content = json.loads(message['text'])
    message = content['message']
    print doc_id, message, 'message'
    Group('doctor{}'.format(doc_id)).send({'text': message})


@channel_session
def ws_disconnect(message):
    doc_id = message.channel_session['doc_id']
    print doc_id, 'disconnected'
    Group('doctor{}'.format(doc_id)).discard(message.reply_channel)
