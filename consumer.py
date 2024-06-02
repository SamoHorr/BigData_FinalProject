from kafka import KafkaConsumer
import json
import csv
import os

def ratings_consumer():
    # Initialize KafkaConsumer
    consumer = KafkaConsumer(
        'ratings',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ratings-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Listening to the 'ratings' topic...")

    # Define the CSV file path
    csv_file_path = 'ratings.csv'

    # Check if the file exists to determine if the header needs to be written
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['user_id', 'movie_id', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file does not exist
        if not file_exists:
            writer.writeheader()

        try:
            while True:
                msg_pack = consumer.poll(timeout_ms=1000)
                if msg_pack:
                    for tp, messages in msg_pack.items():
                        for message in messages:
                            print(f"Received message: {message.value}")
                            writer.writerow(message.value)
                else:
                    print("No messages.")
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()