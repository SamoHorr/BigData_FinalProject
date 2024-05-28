from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

def train_model():
    spark = SparkSession.builder.appName("MovieRecommendation").getOrCreate()

    #loading
    lines = spark.read.csv(r'hdfs:BigData_Final\ratings', header=True, inferSchema=True)
    ratings = lines.rdd.map(lambda r: Row(userId=int(r['userId']), movieId=int(r['movieId']), rating=float(r['rating'])))
    ratings_df = spark.createDataFrame(ratings)

    #building the model 
    als = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
    model = als.fit(ratings_df)

    #saving the trainedmodel
    model.save(r"hdfs:BigData_Final\model")

    spark.stop()

def get_recommendations(user_id):
    spark = SparkSession.builder.appName("MovieRecommendation").getOrCreate()

    # loading the model
    model = ALS.load(r"hdfs:BigData_Final\model")

    #generation recommendation
    user_df = spark.createDataFrame([Row(userId=user_id)])
    recommendations = model.recommendForUserSubset(user_df, 10)
    recommended_movies = recommendations.collect()[0].recommendations

    spark.stop()
    return recommended_movies
