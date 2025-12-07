import sys
from pyspark.sql import functions as F
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ================ READ RAW JSON DATA ==========
bucket = "sports-analytics-data-platform"
raw_path = f"s3://{bucket}/raw/league=PL/"
df = spark.read.json(raw_path)

#============= LIGHT TRANSFORMATION =============
df_clean = df.dropDuplicates().na.drop()

#============= WRITE PARQUET OUTPUT ==============
processed_path = f"s3://{bucket}/processed/league=PL/"
df_clean.write.mode("overwrite").parquet(processed_path)

job.commit()
