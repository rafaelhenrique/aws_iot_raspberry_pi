# -*- coding: utf-8 -*-
import os
import socket
import time
import logging
from datetime import datetime, timedelta

import boto3
from libsoc_zero.GPIO import Tilt
from iot.aws import AWSPublisher

base_dir = os.path.dirname(os.path.abspath(__file__))
keys_path = os.path.join(base_dir, 'auth', 'tilt_sensor')
root_cert_file = os.path.join(keys_path, 'root-CA.crt')
certificate_file = os.path.join(keys_path, 'tilt_sensor.cert.pem')  # need add valid certificate
private_key_file = os.path.join(keys_path, 'tilt_sensor.private.key')  # need add valid private key
hostname = socket.gethostname()
log_file = os.path.join(base_dir, 'tilt_publisher.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s => %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

publisher = AWSPublisher(log_file=log_file,
                         topic='$aws/things/tilt_sensor/shadow/update',  # need create thing on aws named tilt_sensor
                         root_cert_file=root_cert_file,
                         certificate_file=certificate_file,
                         private_key_file=private_key_file,
                         client_id=hostname,
                         address='hostname-xpto.iot.us-east-1.amazonaws.com')  # change to your broker name on aws

last_notification_sent = datetime.utcnow() + timedelta(hours=-1)


def send_sns_notification():
    global last_notification_sent

    seconds_ago = (datetime.utcnow() - last_notification_sent).seconds
    if seconds_ago > 600:
        sns_client = boto3.client(
            'sns',
            region_name='us-east-1',
            aws_access_key_id='MY-ACCESS-KEY',  # change to your access key
            aws_secret_access_key='secret',  # change to your secret key
        )
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:ACCOUNT:StormDetected',  # change to your topic ARN
            Message=('Atenção, foram detectados tremores na região dos sensores '
                     'grande risco de terremoto nos próximos minutos.'),
            MessageStructure='string',
            Subject='Alerta de terremoto')

        last_notification_sent = datetime.utcnow()
    else:
        logger.info('Notification not sended: seconds_ago={}'.format(seconds_ago))


def tilt_event():
    publisher.send({'tilt': 1}, debug=True)
    send_sns_notification()
    logger.warning("tilt 1")


if __name__ == '__main__':
    tilt = Tilt('GPIO_4')
    tilt.when_pressed(tilt_event)
    while True:
        publisher.send({'tilt': 0}, debug=True)
        time.sleep(5)
