# from pyspark.sql import SparkSession
# from pyspark.ml.recommendation import ALS
# from pyspark.sql import Row

# def train_model():
#     spark = SparkSession.builder.appName("MovieRecommendation").getOrCreate()

#     #loading
#     lines = spark.read.csv(r'hdfs:BigData_Final\ratings', header=True, inferSchema=True)
#     ratings = lines.rdd.map(lambda r: Row(userId=int(r['userId']), movieId=int(r['movieId']), rating=float(r['rating'])))
#     ratings_df = spark.createDataFrame(ratings)

#     #building the model 
#     als = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
#     model = als.fit(ratings_df)

#     #saving the trainedmodel
#     model.save(r"hdfs:BigData_Final\model")

#     spark.stop()

# def get_recommendations(user_id):
#     spark = SparkSession.builder.appName("MovieRecommendation").getOrCreate()

#     # loading the model
#     model = ALS.load(r"hdfs:BigData_Final\model")

#     #generation recommendation
#     user_df = spark.createDataFrame([Row(userId=user_id)])
#     recommendations = model.recommendForUserSubset(user_df, 10)
#     recommended_movies = recommendations.collect()[0].recommendations

#     spark.stop()
#     return recommended_movies
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, FloatType
from pyspark.ml.recommendation import ALS
from pymongo import MongoClient

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
            movie_info = db['movie_info'].find_one({"movieId": movie_id})
            if movie_info:
                movie_info['score'] = score 
                recommended_movies.append(movie_info)
    
    spark.stop()
    return recommended_movies

if __name__ == "__main__":
    user_id = 1
    recommendations = get_recommendations(user_id, num_recommendations=5)
    print("The recommendations -----------------------------")
    print(recommendations)
