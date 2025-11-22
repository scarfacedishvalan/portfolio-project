import numpy as np
import spacy
import re
import pandas as pd
from rapidfuzz import fuzz, process
from numpy.linalg import norm
import ast
from blm_helpers import collapse_consecutive_symbols, extract_percent_expressions, fuzzy_match_pc, get_chunks, cosine_similarity, get_number, get_investor_view_single, get_investor_views

def load_embeddings(file_path):
    embeddings = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            vector = np.array(values[1:], dtype=np.float32)
            embeddings[word] = vector
    return embeddings


if __name__ == "__main__":
    dlist = []
    error_list = []
    df = pd.read_excel(r"C:\Python\data\blm_training\training_data.xlsx")
    blm_embeddings = load_embeddings(r"C:\Users\abhir\blm2.txt")
    assets =  [f"Asset#{i}#" for i in range(1, 11)]
    # P, q = get_investor_views(["Asset4 will beat Asset8 by 4%", "Asset5 will outperform Asset3 by 6%", "Asset1 will lag Asset2 by 3%"], blm_embeddings, assets)

    for row in df.to_dict("records"):
        try:
            prompt, true_P, true_q = row["Prompt"], np.array([ast.literal_eval(row["true_P"])]), np.array([row["true_q"]])
            glove_ft_P, glove_ft_q = get_investor_view_single(row["Prompt"], blm_embeddings, assets)
            glove_ft_P_match, glove_ft_q_match = np.array_equal(glove_ft_P, true_P), np.isclose(true_q[0], glove_ft_q[0]) 
            d = {'Prompt': prompt, 'true_P': true_P, 'true_q': true_q, 
                "glove_ft_P": glove_ft_P, "glove_ft_q": glove_ft_q, 
                "glove_ft_P_match": glove_ft_P_match, "glove_ft_q_match": glove_ft_q_match}
        except Exception as e:
            print(str(e))
            d = {'Prompt': prompt, 'true_P': true_P, 'true_q': true_q, 
                "glove_ft_P": np.nan, "glove_ft_q": np.nan, 
                "glove_ft_P_match": False, "glove_ft_q_match": False}
        dlist.append(d)
    df_all_test_results = pd.DataFrame(dlist)

    b=2