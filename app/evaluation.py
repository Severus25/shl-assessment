from collections import defaultdict

def precision_at_k(recommended_ids, relevant_ids, k):
    """Calculates Precision@K."""
    rec_k = recommended_ids[:k]
    intersect = set(rec_k).intersection(set(relevant_ids))
    return len(intersect) / k if k > 0 else 0

def recall_at_k(recommended_ids, relevant_ids, k):
    """Calculates Recall@K."""
    rec_k = recommended_ids[:k]
    intersect = set(rec_k).intersection(set(relevant_ids))
    return len(intersect) / len(relevant_ids) if relevant_ids else 0

def mean_reciprocal_rank(recommended_ids_list, relevant_ids_list):
    """Calculates Mean Reciprocal Rank (MRR)."""
    total_rr = 0
    query_count = len(recommended_ids_list)

    if query_count != len(relevant_ids_list):
        raise ValueError("Number of recommended lists and relevant lists must be equal.")

    if query_count == 0:
        return 0

    for rec_ids, rel_ids in zip(recommended_ids_list, relevant_ids_list):
        relevant_set = set(rel_ids)
        if not relevant_set: continue # Skip if no relevant items for this query

        rr = 0 # Reciprocal Rank for this query
        for i, rec_id in enumerate(rec_ids):
            if rec_id in relevant_set:
                rr = 1 / (i + 1)
                break # Found the first relevant item
        total_rr += rr

    return total_rr / query_count