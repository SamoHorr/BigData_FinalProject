from contextlib import redirect_stderr
import webbrowser
from xml.etree.ElementTree import tostring
import redis
import json
from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
from flask_pymongo import PyMongo
from confluent_kafka import Producer
from consumer import ratings_consumer
from recommendation_engine import get_recommendations
from redis_caching import get_recommendations_cache

app = Flask(__name__)


# configuration 
app.config["MONGO_URI"] = "mongodb://localhost:27017/"
mongo = PyMongo(app)
# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['MovieRecords']
movies_collection = db['movie_records']
movie_info = db['movie_infos']

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize KafkaProducer
producer_config = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(**producer_config)

# login display
@app.route('/login')
def login_form():
    return render_template('login.html')

# login logic
@app.route('/login', methods=['POST'])
def login():
    print("login function")
    username = request.form['userID']
    # from db credential (userId)
    user = movies_collection.find({"userID": username})
    print(user)
    if user:
        print("user id value correct")
        return redirect(url_for('get_user_movies', userId=username))
    else:
        print("user id value incorrect")
        return redirect_stderr(url_for('login_form', error='Invalid username or password'))

# display the movies in grid
@app.route('/movies')
def get_movies():
    movies = list(movies_collection.find({}, {'_id': 0}))
    return render_template('index.html', movies=movies)

# display list depending on user
@app.route('/moviesById')
def get_user_movies():
    user_id = request.args.get('userId')
    print("user id values in get movies" + user_id)
    if user_id:
        user_id = int(user_id)
        movies_info = list(movie_info.find({}, {'_id': 0}))
        user_ratings = {movie['movieId']: movie['rating'] for movie in movies_collection.find({'userId': user_id})}
        for movie in movies_info:
            movie['user_rating'] = user_ratings.get(movie['movieId'], 0)
    else:
        movies_info = list(movie_info.find({}, {'_id': 0}))
    return render_template('index.html', movies=movies_info, userId=user_id)

#sumbitting ratings with kafka
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
@app.route('/submitRating', methods=['POST'])
def submit_rating():
    print('in the submit rating button')
    data = request.json
    movie_id = data.get('movie_id')
    user_id = data.get('user_id')
    rating = data.get('rating')

    if not all([movie_id, user_id, rating]):
        return jsonify({'error': 'Invalid request data'}), 400

    print("Before kafka...")
    topic = 'ratings'
    rating_data = {'movie_id': movie_id, 'user_id': user_id, 'rating': rating}
    print("====rating data:")
    print(rating_data)

    producer.produce('ratings', key=str(rating_data['user_id']), value=json.dumps(rating_data), callback=delivery_report)
    print('Message success...')
    producer.flush()

    print("after sending kafka...")
    userId_int = int(user_id)
    movieId_int = int(movie_id)
    rating_int = int(rating)
    result = movies_collection.update_many(
        {'userId': userId_int , 'movieId': movieId_int},
        {'$set': {'rating': rating_int}}, 
        upsert=True
    )
    print("mongo updated...")
    return jsonify({'message': 'Rating submitted successfully'}), 200

#consuming and saving the submitted ratings
@app.route('/consume')
def consume():
     result = ratings_consumer()
     if result:
         return jsonify({'message': 'Ratings consumed successfully'}), 200
     else:
         return jsonify({'message': 'No ratings to consume or an error occurred'}), 500
    
#generating user based recommendations
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def recommendations(user_id):
    # first version without redis
    #  print("in the recommendations...")
    #  print(user_id)
     
    #  try:
    #      recs = get_recommendations(user_id)
    #      return jsonify(recs), 200
    #  except Exception as e:
    #      print("An unexpected error occurred:", e)
    #      return jsonify({'error': str(e)}), 500
    #second version calling recommendation from redis caching logic file
    recommendations_response = get_recommendations_cache(user_id)
    print("in the recommendation_response of app.py")
    return recommendations_response
         
if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/login')
    app.run(debug=True)
    print("http://127.0.0.1:5000/movies")
    print("http://127.0.0.1:5000/login")
    print("http://127.0.0.1:5000/moviesById")