import numpy as np
import spacy
import re
from rapidfuzz import fuzz, process
from numpy.linalg import norm


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def fuzzy_match_pc(token, threshold=80):
        matches = process.extractOne(token, ["Percent", "%", "pc"], scorer=fuzz.ratio)
        if matches and matches[1] >= threshold:
            return matches[0]
        return None

def collapse_consecutive_symbols(text):
    # Match any non-alphanumeric, non-whitespace character repeated consecutively
    return re.sub(r'([^\w\s])(?:\s*\1)+', r'\1', text)

def extract_percent_expressions(text, keywords=["percent", "%", "pc"], threshold=80):
    """
    Extract number + fuzzy-matched unit (like 'percent', '%', 'pc') from text.

    Args:
        text (str): Input sentence to search.
        keywords (list): List of target words to match against (fuzzily).
        threshold (int): Minimum fuzzy score to count as a match (0-100).

    Returns:
        list of dict: Each dict contains 'full', 'number', 'unit', and 'matched_as'.
    """
    pattern = r'\d+(?:\.\d+)?\s*[a-zA-Z%]+%*'
    
    results = []

    for match in re.finditer(pattern, text):
        full = match.group()
        num_part_match = re.match(r'\d+(?:\.\d+)?', full)
        word_part = re.sub(r'^\d+(?:\.\d+)?\s*', '', full)

        if not num_part_match or not word_part:
            continue

        best_match = process.extractOne(word_part.lower(), keywords, scorer=fuzz.ratio)
        if best_match and best_match[1] >= threshold:
            results.append({
                "full": full,
                "word_part": word_part,
                "number": float(num_part_match.group())/100,
                "num_part_match": num_part_match,
                "unit": "pc",
                "matched_as": best_match[0],
                "score": best_match[1]
            })
        else:
            results.append({
                "full": full,
                "number": float(num_part_match.group()),
                "word_part": word_part,
                "num_part_match": num_part_match,
                "unit": "scalar",
                 "matched_as": best_match[0],
                "score": best_match[1]
            })
    if not results:
        number = get_number(text)
        results.append({
                "number": number
            })

    return results

def get_number(text):
    words = text.lower().split()
    
    # Regex for number with optional % and spaces
    pattern = r'-?\d*\.?\d+\s*%?'
    number = 0
    exists_percent = False
    for word in words:
        match = fuzzy_match_pc(word)
        if match:
            exists_percent = True
            break
    for word in words:
        match = re.search(pattern, word)
        if match:
            num_str = match.group().replace(" ", "")
            if "%" in num_str:
                exists_percent = True
                num_str
            number = float(num_str)
            break
    if exists_percent:
        number = number/100
    return number

def get_chunks(sentence, assets):
    # Process sentence with spaCy
    sentence = collapse_consecutive_symbols(sentence.strip())
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentence)

    # Function to perform fuzzy matching for asset extraction
    def fuzzy_match_asset(token, assets, threshold=80):
        matches = process.extractOne(token, assets, scorer=fuzz.ratio)
        if matches and matches[1] >= threshold:
            return matches[0]
        return None

    # Extract assets (with fuzzy matching and order preservation)
    extracted_assets = []
    # Extract action (beat/lag)
    action = None
    for token in doc:
        if token.pos_ == "VERB":
            action = token.text
    reverse = False
    reduced_sentence = sentence
    for token in doc:
        # Normalize token text (remove spaces, underscores, and convert to lowercase)
        normalized_token = token.text.lower().replace('_', ' ').strip()
        matched_asset = fuzzy_match_asset(normalized_token, [asset.lower() for asset in assets])
        if matched_asset:
            extracted_assets.append(matched_asset)
#             print(reduced_sentence.lower(), matched_asset)
            reduced_sentence = reduced_sentence.lower().replace(token.text.lower(), "")
        if token.dep_ == "agent" and token.lemma_ == "by" and token.head.text == action:
#             print("Found passive")
            reverse = True
    if reverse:
        extracted_assets = list(reversed(extracted_assets))

    # Extract percentage
#     number = get_number(reduced_sentence)
    numerical_matches = extract_percent_expressions(reduced_sentence)
    if len(numerical_matches) == 0:
        raise ValueError("No numerical expression found")
    
    if len(numerical_matches) > 1:
        raise ValueError("More than one numerical expressions found")
    
    match = numerical_matches[0]
    number = match['number']
        
    return extracted_assets, action, number


def get_investor_view_single(text, embeddings, all_assets, threshold=0.3):
    """
    Convert the investor's view text into the view matrix P and vector q
    based on cosine similarity for the relation.

    Parameters:
    - text (str): Investor's view text, e.g., "Asset1 will outperform Asset2 by 5%"
    - embeddings (dict): Word embeddings dictionary, e.g., {"outperform": vector1, "beat": vector2, ...}
    - n_assets (int): Total number of assets in the portfolio
    - threshold (float): Cosine similarity threshold to determine which asset beats which

    Returns:
    - P (ndarray): The view matrix (m x n)
    - q (ndarray): The view vector (m x 1)
    """
    
    # Step 1: Extract assets, action, and number using get_chunks
    assets, action, number = get_chunks(text, all_assets)
    n_assets = len(all_assets)
    
    # Step 2: Get the word embeddings for the action
    action_vector = embeddings.get(action, None)
    if action_vector is None:
        raise ValueError(f"Action '{action}' not found in the embeddings.")

    if len(assets) == 2:
        # Compare action vector with known relations, e.g., "beat"
        # Assuming we have a vector for "beat" as a reference
        beat_vector = embeddings.get("beat", None)
        if beat_vector is None:
            raise ValueError("Embedding for 'beat' not found.")

        # Compute cosine similarity between action and "beat"
        cosine_sim = cosine_similarity(action_vector, beat_vector)

        # Step 3: Determine the relation between the assets
        if cosine_sim > threshold:
            relation = 1  # Asset1 beats Asset2
        elif cosine_sim < -threshold:
            relation = -1  # Asset2 beats Asset1
        else:
            raise ValueError(f"Action relation: {cosine_sim} is unclear for {action}, similarity is too close to threshold (ref: beat).")

        # Step 4: Initialize P and q
        # P will be an m x n matrix, where m is the number of views (1 for now)
    #     print(n_assets)
        P = np.zeros((1, n_assets))
    #     print(P)
        q = np.zeros(1)

        # Map assets to indices (Assume assets are mapped from 0 to n-1)
        asset1_idx = int(assets[0].lower().replace("asset", "").replace("#", "")) - 1
        asset2_idx = int(assets[1].lower().replace("asset", "").replace("#", "")) - 1

        # Step 5: Fill the P matrix and q vector
        P[0, asset1_idx] = relation
        P[0, asset2_idx] = -relation  # Opposite relation for the second asset
        q[0] = number  # Magnitude of the view

        return P, q
    elif len(assets) == 1:
        return_vector = embeddings.get("return", None)
         # Compute cosine similarity between action and "beat"
        cosine_sim = cosine_similarity(action_vector, return_vector)
        relation = 1
        
        if cosine_sim < threshold:
            raise ValueError(f"Action relation: {cosine_sim} is unclear for {action}, similarity is too close to threshold (ref: return).")

        # Step 4: Initialize P and q
        # P will be an m x n matrix, where m is the number of views (1 for now)
        P = np.zeros((1, n_assets))
    #     print(P)
        q = np.zeros(1)

        # Map assets to indices (Assume assets are mapped from 0 to n-1)
        asset1_idx = int(assets[0].lower().replace("asset", "").replace("#", "")) - 1

        # Step 5: Fill the P matrix and q vector
        P[0, asset1_idx] = relation
        q[0] = number  # Magnitude of the view

        return P, q
    
def get_investor_views(texts, embeddings, all_assets, threshold=0.3):
    """
    Convert multiple investor views into a combined view matrix P and vector q.
    
    Parameters:
    - texts (list of str): List of investor view texts.
    - embeddings (dict): Pre-trained embeddings dictionary.
    - n_assets (int): Number of assets in the portfolio.
    - threshold (float): Cosine similarity threshold for relation determination.
    
    Returns:
    - P_final (ndarray): Combined view matrix.
    - q_final (ndarray): Combined view vector.
    """

    # Initialize lists to accumulate P and q for all views
    P_list = []
    q_list = []
    
    # Process each investor view one by one
    for text in texts:
        # Step 1: Extract assets, action, and number using get_chunks
        
        # Step 2: Get the P matrix and q vector for this view using get_investor_view_single
        P, q =  get_investor_view_single(text, embeddings, all_assets, threshold=0.3)
        
        # Append to the lists
        P_list.append(P)
        q_list.append(q)
    
    # Step 3: Combine all the views into a single matrix and vector
    P_final = np.vstack(P_list)  # Stack P matrices vertically
    q_final = np.concatenate(q_list)  # Stack q vectors
    
    return P_final, q_final