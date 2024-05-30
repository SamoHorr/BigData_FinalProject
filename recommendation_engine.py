from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, FloatType
from pyspark.ml.recommendation import ALS
from pymongo import MongoClient
from bson import ObjectId

def convert_to_json_serializable(recommended_movies):
    for movie in recommended_movies:
        # Convert ObjectId to string for JSON serialization
        movie['_id'] = str(movie['_id'])

#num_recommendations either default shows 5 or chosen nbr
def get_recommendations(user_id, num_recommendations=5):
    # Initializing Spark session
    spark = SparkSession.builder.appName('recommendation').getOrCreate()

    client = MongoClient('mongodb://localhost:27017/')
    db = client['MovieRecords']
    ratings_collection = db['movie_records']
    
    ratings_data = list(ratings_collection.find({}, {'_id': 0}))
    ratings_df = spark.createDataFrame(ratings_data)
    
    # verifying types
    ratings_df = ratings_df.withColumn("userId", ratings_df["userId"].cast(IntegerType()))
    ratings_df = ratings_df.withColumn("movieId", ratings_df["movieId"].cast(IntegerType()))
    ratings_df = ratings_df.withColumn("rating", ratings_df["rating"].cast(FloatType()))

    # Building the ALS model
    als = ALS(maxIter=10, regParam=0.1, userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
    model = als.fit(ratings_df)
    
    # Generating recommendations for the user
    user_df = spark.createDataFrame([(user_id,)], ["userId"])
    recommendations = model.recommendForUserSubset(user_df, num_recommendations)
    recommendations = recommendations.collect()
    
    # Collecting recommended movies
    recommended_movies = []
    if recommendations:
        for row in recommendations[0].recommendations:
            movie_id = row.movieId
            score = row.rating

            # Fetching movie info from MongoDB
            movie_info = db['movie_infos'].find_one({"movieId": movie_id})
            if movie_info:
                movie_info['score'] =  round(score, 1) 
                recommended_movies.append(movie_info)
    
    # Convert ObjectId fields to strings
    convert_to_json_serializable(recommended_movies)

    spark.stop()
    return recommended_movies

if __name__ == "__main__":
    user_id = 1
    recommendations = get_recommendations(user_id, num_recommendations=5)
    print("The recommendations -----------------------------")
    print(recommendations)
