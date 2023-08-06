import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import yaml
import os
from course_search.config.core import CONFIG_FILE_PATH

params = yaml.safe_load(open(CONFIG_FILE_PATH))
# api_key = params["get_embeddings"]["api_token"]
# api_key = os.environ.get("API_KEY")

api_key = os.environ['OPENAI_API_KEY']


def import_csv(file_path, use_cols=None):
    """
    loads a csv file into memory
    :input:
        file_path: str, directory path of the csv file to be imported
        use_cols: list, collection of the column headers to be imported
    :output:
        df: pandas DataFrame, dataframe of the loaded csv file
    """
    df = pd.read_csv(file_path, usecols=use_cols, low_memory=False)
    print("File has", df.shape[0], "rows")

    return df


def save_csv_file(df, destination_path):
    """
    save data to csv file without index
    :input:
        df: pandas DataFrame, finalised data to be saved to disk
        destination_path: str, file directory where the data should be saved to
    :output:
        Nil
    """
    df.to_csv(destination_path, index=False)
    print("Done saving csv file")

    return


def search_courses(df, query, n=5, threshold=0.7, pprint=False):
    """
    search through course data and find and rank search results based on cosine similarity between query and course content
    :input:
        df: pandas DataFrame, input dataframe with content embeddings
        query: str, search query input by user
        n: int, number of top ranked results to display
        threshold: float, cut-off similarity score for search results
        pprint: True/False, determines if results are printed out in console
    :output:
        final_json: json, json formatted search results
    """
    course_embedding = get_embedding(
        query,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, course_embedding))

    results = (
        df.sort_values("similarity", ascending=False).head(n)
    )

    results = results.query(f'similarity > {threshold}')
    
    output = {}
    _list = []
    keys = range(len(results))
    
    for title, obj, aot, skill, sim in zip(
        results['Course Title'], results['Course Objective'], 
        results["course_skill_list"], results['Area Of Training'], 
        results.similarity):
        results_dic = {
            "course_title": title,
            "course_objective": obj,
            "course_skills": skill,
            "area_of_training": aot,
            "similarity_score": np.round(sim, 2)
        }
        _list.append(results_dic)
    
    for i in keys:
        output[i] = _list[i]
    if len(output) == 0:
        final_json = {}
    else:
        final_json = {
            "search_results": output
        }

    if pprint:
        i = 1
        for r in results_final['Course Title']:
            print(f"{i}. Course Title: {r[:100]}")
            print()
            i += 1

    return final_json
