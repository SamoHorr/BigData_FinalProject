from kafka import KafkaConsumer
import json

# Initialize KafkaConsumer
consumer = KafkaConsumer('my-topic', bootstrap_servers='localhost:9092', auto_offset_reset='earliest')

# Consume messages from the topic
for message in consumer:
    print(json.loads(message.value.decode('utf-8')))

# Close the consumer
consumer.close()
