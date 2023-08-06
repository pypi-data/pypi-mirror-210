import yaml
import os
from botocore.exceptions import NoCredentialsError
import boto3
import openai
from cachetools import cached

from course_search.utils import *
from course_search.config.core import CONFIG_FILE_PATH

params = yaml.safe_load(open(CONFIG_FILE_PATH))
index_file = params["merge_indices"]["indexed_file_path"]
s3_file_name = params["download"]["s3_file_name"]
bucket_name = params["download"]["bucket_name"]

api_key = os.environ.get("OPENAI_API_KEY")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

os.environ['OPENAI_API_KEY'] = api_key

openai.api_key = api_key

def download_file(bucket_name, file_key, local_dir):
    s3 = boto3.resource("s3", 
                        aws_access_key_id=aws_access_key_id, 
                        aws_secret_access_key=aws_secret_access_key)
    bucket = s3.Bucket(bucket_name)
    bucket.download_file(file_key, local_dir)

@cached(cache={})
def load_index(index_file):
    catalog_df = import_csv(file_path=index_file)
    catalog_df['embedding'] = catalog_df.embedding.apply(eval).apply(np.array)
    return catalog_df

def file_check(index_file):
    if not os.path.exists(index_file):
        download_file(bucket_name=bucket_name, file_key=s3_file_name, local_dir=index_file)
    
def search_for_courses(query, index_file, top_n=5, threshold=0.81):
    """
    input:
        :query: str, search query for courses
        :index_file: csv, collection of courses with ada gen2 embedding within
        :top_n: int, optional param, default returns top 5 courses
        :threshold: float, optional param, default set to 0.81 (returns courses that are at least 81% similar to search query)
    output:
        :result_json: json, contains course details and similarity score between search and course returned
    """
    file_check(index_file)
    
    # Load in the course catalog with embeddings
    catalog_df = load_index(index_file=index_file)
    print("file loaded")

    # call util function search_courses to return top matches in json
    result_json = search_courses(df=catalog_df, query=query.strip(), n=top_n, threshold=threshold, pprint=False)
    
    return result_json

# if __name__ == "__main__":
#     res = search_for_courses(query="pottery")
#     print(res)