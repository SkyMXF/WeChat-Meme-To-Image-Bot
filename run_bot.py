import json
import xml.etree.ElementTree
import http.server
import socketserver
import logging
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message, create_reply


LOGGER = logging.getLogger("MainLogger")

TOKEN = ""


class WeChatUserMsgRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # get args
        args = self.path.split("?")[1]
        args = args.split("&")
        args_dict = {}
        for arg in args:
            key, value = arg.split("=")
            args_dict[key] = value

        try:
            check_signature(TOKEN, args_dict["signature"], args_dict["timestamp"], args_dict["nonce"])
        except InvalidSignatureException:
            LOGGER.error("Invalid signature for verification.")
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(args_dict["echostr"].encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        LOGGER.debug("Got post data: " + str(post_data))
        self.send_response(200)
        self.end_headers()

        # parse xml data
        root = xml.etree.ElementTree.fromstring(post_data)
        to_user_name = root.find("ToUserName").text
        from_user_name = root.find("FromUserName").text
        create_time = root.find("CreateTime").text
        msg_type = root.find("MsgType").text
        media_id = root.find("MediaId").text

        LOGGER.info("To user name: " + to_user_name)
        LOGGER.info("From user name: " + from_user_name)
        LOGGER.info("Create time: " + create_time)
        LOGGER.info("Msg type: " + msg_type)
        LOGGER.info("Media id: " + media_id)

        # response


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

    with socketserver.TCPServer(("", port), WeChatUserMsgRequestHandler) as httpd:
        LOGGER.info("Server running on port: " + str(port))
        httpd.serve_forever()
