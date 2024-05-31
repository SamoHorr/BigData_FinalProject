from kafka import KafkaProducer
import json

# Initialize KafkaProducer
producer = KafkaProducer(
        bootstrap_servers=['kafka:29092'],
        api_version=(0, 10, 0),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

print("before function...")
def send_rating(movie_id, user_id, rating):
    print("in function...")
    topic = 'ratings'
    rating_data = {'movie_id': movie_id, 'user_id': user_id, 'rating': rating}
    producer.send(topic, json.dumps(rating_data).encode('utf-8'))

print("Producer closing...")
producer.close()
