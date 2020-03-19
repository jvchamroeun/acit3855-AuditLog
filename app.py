import connexion
from connexion import NoContent
from pykafka import KafkaClient
import json
import yaml
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


def audit_booking_details(offset):
    client = KafkaClient(hosts=app_config['kafka']['server'] + ":" + app_config['kafka']['port'])
    topic = client.topics[app_config['kafka']['topic']]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)

    bd_list = []
    for message in consumer:
        msg_str = message.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg['type'] == 'booking_details':
            bd_list.append(msg)

    if offset >= len(bd_list):
        return NoContent, 404

    print(bd_list[offset])

    return bd_list[offset], 200


def audit_freight_assignments():
    client = KafkaClient(hosts=app_config['kafka']['server'] + ":" + app_config['kafka']['port'])
    topic = client.topics[app_config['kafka']['topic']]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)

    fa_list = []
    for message in consumer:
        msg_str = message.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg['type'] == 'freight_assignment':
            fa_list.append(msg)

    if len(fa_list) == 0:
        return NoContent, 404

    print(fa_list[-1])

    return fa_list[-1], 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml")

if __name__ == "__main__":
    app.run(port=8110)

