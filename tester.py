# import json
# from kafka import KafkaProducer 

# try:
#     producer = KafkaProducer(
#         bootstrap_servers=['kafka:29092'],
#         api_version=(0, 10, 0),
#         value_serializer=lambda v: json.dumps(v).encode('utf-8')
#     )
#     print("Kafka connection successful!")
# except Exception as e:
#     print(f"Kafka connection failed: {e}")
#     exit(1)  # Exit if the connection to Kafka fails

# test_topic = 'test_topic'
# test_message = {'test_key': 'test_message'}
# print('Prepping to send message...')

# try:
#     future = producer.send(test_topic, test_message)
#     result = future.get(timeout=10)
#     print("Message sent successfully! Metadata:", result)
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     producer.flush()
#     producer.close()
#     print("Producer closed.")
from confluent_kafka import Producer
import json

producer_config = {
    'bootstrap.servers': 'kafka:29092'
}

producer = Producer(**producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_message(message):
    producer.produce('ratings', key=str(message['user_id']), value=json.dumps(message), callback=delivery_report)
    producer.flush()
