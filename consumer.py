from kafka import KafkaConsumer
import json
import csv
import os

def ratings_consumer():
    #kafkaconsumer instance
    consumer = KafkaConsumer(
        'ratings',  
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Listening to the 'ratings' topic...")

    #saving the message
    csv_file_path = 'ratings/ratings.csv'
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['user_id', 'movie_id', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # only if file doesnt exists
        if not file_exists:
            writer.writeheader()

        try:
            while True:
                msg_pack = consumer.poll(timeout_ms=1000)
                if msg_pack:
                    for tp, messages in msg_pack.items():
                        for message in messages:
                            print(f"Message received: {message.value}")
                            writer.writerow(message.value)
                else:
                    print("No messages.")
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()


