import socket
import time
from iot.aws import AWSPublisher
from iot.analog import RaspberryAnalogSensor


if __name__ == '__main__':
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    keys_path = os.path.join(base_dir, 'auth', 'light_sensor')
    root_cert_file = os.path.join(keys_path, 'root-CA.crt')
    certificate_file = os.path.join(keys_path, 'light_sensor.cert.pem')  # need add valid certificate
    private_key_file = os.path.join(keys_path, 'light_sensor.private.key')  # need add valid private key
    hostname = socket.gethostname()
    log_file = os.path.join(base_dir, 'light_publisher.log')
    publisher = AWSPublisher(log_file=log_file,
                             topic='$aws/things/light_sensor/shadow/update',  # need create thing on aws named light_sensor
                             root_cert_file=root_cert_file,
                             certificate_file=certificate_file,
                             private_key_file=private_key_file,
                             client_id=hostname,
                             address='hostname-xpto.iot.us-east-1.amazonaws.com')  # change to your broker name on aws
    while True:
        light_sensor = RaspberryAnalogSensor(pin=17)
        publisher.send({'light': light_sensor.read()}, debug=True)
        time.sleep(5)
