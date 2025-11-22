# ...existing code...
import numpy as np
from gensim.models import KeyedVectors

def build_kv_from_text(txt_path, out_kv_path):
    words = []
    vecs = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        first = f.readline()
        if not first:
            raise ValueError("Empty embeddings file")
        parts = first.rstrip().split()
        # detect header (two ints)
        has_header = False
        try:
            int(parts[0]); int(parts[1])
            has_header = True
        except Exception:
            has_header = False

        if has_header:
            # header consumed; read remaining lines
            for line in f:
                items = line.rstrip().split()
                if not items:
                    continue
                words.append(items[0])
                vecs.append(np.array(items[1:], dtype=np.float32))
        else:
            # first line was a vector line; include it then read rest
            words.append(parts[0])
            vecs.append(np.array(parts[1:], dtype=np.float32))
            for line in f:
                items = line.rstrip().split()
                if not items:
                    continue
                words.append(items[0])
                vecs.append(np.array(items[1:], dtype=np.float32))

    vecs = np.vstack(vecs)
    dim = vecs.shape[1]
    kv = KeyedVectors(vector_size=dim)
    kv.add_vectors(words, vecs)
    kv.save(out_kv_path)
    return kv

if __name__ == "__main__":
    txt_path = r"C:\Users\abhir\blm2.txt"
    out_kv = r"C:\Python\data\blm_kv.kv"
    # kv = build_kv_from_text(txt_path, out_kv)
    # load in app (memory-friendly)
    kv = KeyedVectors.load(out_kv, mmap='r')
    vec1 = np.array(kv['outperform'])  # example lookup
    vec2 = np.array(kv['lags'])
    sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print(f"Similarity between 'outperform' and 'beat': {sim}")
# ...existing code...