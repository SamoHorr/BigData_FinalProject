from kafka import KafkaProducer
import json

# Initialize KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Function to send user ratings to Kafka
def send_rating(movie_id, user_id, rating):
    topic = 'ratings'
    rating_data = {'movie_id': movie_id, 'user_id': user_id, 'rating': rating}
    producer.send(topic, json.dumps(rating_data).encode('utf-8'))

# Close the producer
producer.close()
