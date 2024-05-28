import json
import os
import redis
from flask import Flask, jsonify, render_template, request, redirect, url_for
from recommendation_engine import get_recommendations
# #creating a redis instance with the online service (version 1)
# redis_host = 'redis-14070.c82.us-east-1-2.ec2.redns.redis-cloud.com' 
# redis_port = 14070 
# redis_client =redis.Redis(
#   host='redis-14333.c8.us-east-1-2.ec2.redns.redis-cloud.com',
#   port=14333,
#   username='forwatching9322@gmail.com',
#   password='Bigd@ta2024')

# Redis creating instance with Docker
# Redis connection to bypass the redis connection issue 11001 
if 'DOCKER_ENV' in os.environ:
    # in Docker environment
    redis_client = redis.Redis(host='redis', port=6379)
else:
    # outside of Docker connect using localhost
    redis_client = redis.Redis(host='localhost', port=6379)

def get_recommendations_cache(user_id):
    # print("In the recommendations...")
    # print(user_id)

    try:
        # Verifying the Redis connection
        response = redis_client.ping()
        if response:
            print("Connected to Redis")
        else:
            print("Failed to connect to Redis")
    except redis.ConnectionError as e:
        print("Redis connection error:", e)

    try:
        # Checking if the recommendation is in cache
        recommendations_cache_key = f"recommendations:{user_id}"
        cached_recommendations = redis_client.get(recommendations_cache_key)
        print(recommendations_cache_key)
        print( "--------------------" + str(cached_recommendations))

        if cached_recommendations:
            # # If they are sending them for display
            print("Checking cache...")
            # recommendations = json.loads(cached_recommendations)
            # print("after load cached")
            # return jsonify(recommendations), 200
            #return cached_recommendations
            cached_recommendations_str = cached_recommendations.decode('utf-8')
            cached_recommendations_str = cached_recommendations_str.replace("'", '"')
            recommendations = json.loads(cached_recommendations_str)
            return jsonify(recommendations) , 200
        else:
            # If not generating them
            print("generating for cache...")
            recs = get_recommendations(user_id)
            # Storing them in cache
            print("Storing in cache...")
            redis_client.set(recommendations_cache_key, str(recs))
            print("after client set...")
            return jsonify(recs), 200
            # return recs
    except Exception as e:
        print("An unexpected error occurred:", e)
        return jsonify({'error': str(e)}), 500
