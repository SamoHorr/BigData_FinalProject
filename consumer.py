from confluent_kafka import Consumer, KafkaError
import json
import csv
import os

def ratings_consumer():
    # Configure Kafka Consumer
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'test-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe(['ratings'])

    print("Listening to the 'ratings' topic...")

    # verifying directory
    csv_directory = 'ratings'
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    # Saving the message
    csv_file_path = os.path.join(csv_directory, 'ratings.csv')
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['user_id', 'movie_id', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # only if file doesn't exist
        if not file_exists:
            writer.writeheader()

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    print("No messages...")
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
                    elif msg.error():
                        print(f"Consumer error: {msg.error()}")
                else:
                    try:
                        message = json.loads(msg.value().decode('utf-8'))
                        print(f"Message received: {message}")
                        writer.writerow(message)
                        csvfile.flush()
                    except Exception as e:
                        print(f"Error processing message: {e}")
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()
