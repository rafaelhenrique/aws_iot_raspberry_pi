# -*- coding: utf-8 -*-
import json
import ssl
import socket
import logging
import time
from datetime import datetime

import paho.mqtt.client as paho
from paho.mqtt.publish import _on_publish, _on_connect


def multiple(msgs, hostname="localhost", port=1883, client_id="", keepalive=60,
             tls=None, protocol=paho.MQTTv311,
             transport="tcp", logger=None, debug=False):
    """
    This is an modification from original function of paho mqtt python.
    Reference: https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/mqtt/publish.py#L60
    """

    if not isinstance(msgs, list):
        raise ValueError('msgs must be a list')

    client = paho.Client(client_id=client_id,
                         userdata=msgs, protocol=protocol, transport=transport)

    if debug and logger:
        client.enable_logger(logger)

    client.on_publish = _on_publish
    client.on_connect = _on_connect

    if tls is not None:
        if isinstance(tls, dict):
            client.tls_set(**tls)
        else:
            # Assume input is SSLContext object
            client.tls_set_context(tls)

    client.connect(hostname, port, keepalive)
    client.loop_forever()


def single(topic, payload=None, qos=0, retain=False, hostname="localhost",
           port=1883, client_id="", keepalive=60, tls=None,
           protocol=paho.MQTTv311, transport="tcp", logger=None,
           debug=False):
    """
    This is an modification from original function of paho mqtt python.
    Reference: https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/mqtt/publish.py#L156
    """
    msg = {'topic': topic, 'payload': payload, 'qos': qos, 'retain': retain}

    multiple([msg], hostname, port, client_id, keepalive, tls, protocol,
             transport, logger, debug)


class AWSPublisher(object):

    def __init__(self, topic, root_cert_file, certificate_file,
                 private_key_file, client_id, address, log_file='aws.log',
                 port=8883, keepalive=60):
        self.log_file = log_file
        self.logger = self.get_logger()
        self.topic = topic
        self.root_cert_file = root_cert_file
        self.certificate_file = certificate_file
        self.private_key_file = private_key_file
        self.client_id = client_id
        self.address = address
        self.port = port
        self.keepalive = keepalive

    def get_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def send(self, data, debug=False):
        """
        Publish message on topic AWS IoT Greengrass

        Paramether:
            data(dict): Some dict with data

        Returns:
            None
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %T")
        data.update({
            'timestamp': timestamp
        })
        payload = {
            "state": {
                "reported": data,
            }
        }

        try:
            single(
                self.topic,
                payload=json.dumps(payload), qos=0, retain=False,
                hostname=self.address, port=self.port,
                client_id=self.client_id,
                keepalive=self.keepalive,
                tls={
                    'ca_certs': self.root_cert_file,
                    'certfile': self.certificate_file,
                    'keyfile': self.private_key_file,
                    'tls_version': ssl.PROTOCOL_TLSv1_2,
                    'ciphers': None,
                },
                logger=self.logger,
                debug=debug)

        except socket.gaierror as e:  # For DNS resolution errors
            self.logger.exception('AWSPublisher exception')

        except ssl.SSLError as e:  # For connection errors
            self.logger.exception('AWSPublisher exception')


if __name__ == '__main__':
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    keys_path = os.path.join(base_dir, 'light_sensor')
    root_cert_file = os.path.join(keys_path, 'root-CA.crt')
    certificate_file = os.path.join(keys_path, 'light_sensor.cert.pem')  # need add valid certificate
    private_key_file = os.path.join(keys_path, 'light_sensor.private.key')  # need add valid private key
    hostname = socket.gethostname()
    publisher = AWSPublisher(log_file='publisher.log',
                             topic='$aws/things/light_sensor/shadow/update',  # need create thing on aws named light_sensor
                             root_cert_file=root_cert_file,
                             certificate_file=certificate_file,
                             private_key_file=private_key_file,
                             client_id=hostname,
                             address='hostname-xpto.iot.us-east-1.amazonaws.com')  # change to your broker name on aws
    import random
    while True:
        start = time.time()
        time.sleep(1)
        sample_value = random.random() * 10
        publisher.send({'light': sample_value}, debug=True)
        end = time.time() - start
        print("End time: {}".format(end))
