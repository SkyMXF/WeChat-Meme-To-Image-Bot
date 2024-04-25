import json
import logging
from flask import Flask, request
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message, create_reply

app = Flask(__name__)

LOGGER = logging.getLogger("MainLogger")

TOKEN = ""


@app.route('/memebot', methods=['GET', 'POST'])
def meme_bot():
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')

    # check signature
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        return 'Verification failed'

    if request.method == 'GET':
        # verification reply
        return echo_str
    else:
        # handle message
        msg = parse_message(request.data)
        if msg.type == 'text':
            reply = create_reply('echo: ' + msg.content, msg)
            return reply.render()
        else:
            reply = create_reply('Sorry, can not handle this for now', msg)
            return reply.render()


if __name__ == '__main__':

    # logging with time
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    LOGGER.info("Server started.")

    with open("config.json", "r") as f:
        config = json.load(f)

    port = config["local_port"]
    TOKEN = config["token"]

    LOGGER.info("Server running on port: " + str(port))
    app.run(port=port)
