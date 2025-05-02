# evaluation_script.py (Modified TEST_SET)
import json
import os
import sys

# Ensure the app directory is in the Python path
# This allows importing 'app.engine' and 'app.evaluation' directly
# Adjust if your script/project structure is different
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
# print(f"Project Root: {project_root}") # Debug print
# print(f"Sys Path: {sys.path}")        # Debug print


from app.engine import get_recommendations, load_assessments
from app.evaluation import precision_at_k, recall_at_k, mean_reciprocal_rank

# --- Configuration ---
K = 5 # Evaluate Precision and Recall at K=5

# --- Enhanced Test Set ---
# Reviewed expected_ids: focus on relevance, not predicted rank.
# Added more diverse queries.
TEST_SET = [
    {
        "query": {
            "job_title": "Software Engineer",
            "job_level": "Professional",
            "competencies": ["problem solving", "python programming", "collaboration", "algorithmic thinking"]
        },
        # Python is most specific, then problem solving/algo tests, then general behavioral
        "expected_ids": ["SHL008", "SHL001", "SHL004", "SHL002", "SHL010"]
    },
    {
        "query": {
            "job_title": "Customer Service Agent",
            "job_level": "Entry",
            "competencies": ["customer focus", "interpersonal skills", "problem solving", "resilience"]
        },
        # SJT Cust Svc is key, then general skills/behavioral relevant to entry/service
        "expected_ids": ["SHL006", "SHL001", "SHL009", "SHL002", "SHL005"] # Added OPQ/MQ as potentially relevant behavioral fits
    },
    {
        "query": {
            "job_title": "Finance Manager",
            "job_level": "Managerial",
            "competencies": ["numerical reasoning", "data analysis", "decision making", "leadership", "strategic thinking"]
        },
        # Numerical is core, Mgmt SJT/OPQ for leadership/decision, Deductive/Inductive for thinking
        "expected_ids": ["SHL003", "SHL007", "SHL002", "SHL004", "SHL001"]
    },
    {
        "query": {
            "job_title": "Remote Project Coordinator",
            "job_level": "Professional",
            "competencies": ["time management", "collaboration", "adaptability", "communication"]
        },
        # RemoteWorkQ is specific, OPQ/MQ cover general work style/motivation, Verbal for communication
        "expected_ids": ["SHL010", "SHL002", "SHL005", "SHL009"]
    },
    {
        "query": {
            "job_title": "Data Scientist",
            "job_level": "Professional",
            "competencies": ["data analysis", "critical thinking", "python programming", "reasoning"]
        },
        # Numerical/Cognitive tests are highly relevant, Python skill test
        "expected_ids": ["SHL003", "SHL001", "SHL004", "SHL008", "SHL009"] # Added Verbal as 'reasoning' can involve text
    },
    # --- Added Queries ---
    {
        "query": {
            "job_title": "Marketing Assistant",
            "job_level": "Entry",
            "competencies": ["communication", "collaboration", "adaptability"]
        },
        # Focus on softer skills, general cognitive ability. SJT-CS might have overlap.
        "expected_ids": ["SHL009", "SHL002", "SHL005", "SHL001", "SHL006"] # Verbal, OPQ, MQ, Inductive, SJT-CS
    },
    {
        "query": {
            "job_title": "Senior HR Business Partner",
            "job_level": "Managerial", # Could also be Professional, let's test Managerial
            "competencies": ["interpersonal skills", "influence", "decision making", "people management"]
        },
        # Behavioral and situational judgment are key here.
        "expected_ids": ["SHL002", "SHL007", "SHL005", "SHL004"] # OPQ, SJT Mgmt, MQ, Deductive (for decision making)
    },
    {
        "query": {
            "job_title": "Graduate Trainee - General Management",
            "job_level": "Entry",
            "competencies": ["problem solving", "learning agility", "adaptability", "drive"] # Learning agility not explicitly in data - tests adaptability scoring
        },
        # General cognitive, motivation, and broad behavioral.
        "expected_ids": ["SHL001", "SHL003", "SHL009", "SHL005", "SHL002"] # Inductive, Numerical, Verbal, MQ, OPQ
    }
]

# (Rest of the evaluation_script.py remains the same)
# ... function run_evaluation()...
# ... if __name__ == "__main__": ...

def run_evaluation():
    """Runs the evaluation process and prints results."""
    print("--- Starting Evaluation ---")

    all_recommended_ids = []
    all_relevant_ids = []
    precisions = []
    recalls = []

    # Ensure engine uses the correct data file path
    # No changes needed here if imports work correctly

    print(f"Evaluating {len(TEST_SET)} test queries (K={K})...\n")

    for i, test_case in enumerate(TEST_SET):
        query = test_case["query"]
        relevant_ids = test_case["expected_ids"]
        # Ensure relevant IDs list is not empty for calculations
        if not relevant_ids:
             print(f"Query {i+1}: SKIPPING - No expected IDs defined.")
             continue

        print(f"Query {i+1}: Level='{query['job_level']}', Competencies={query['competencies']}")
        print(f"  Expected Relevant IDs ({len(relevant_ids)}): {relevant_ids}")


        # Get recommendations from the engine
        # Requesting more results internally allows MRR to look beyond K=5 if needed
        internal_max_results = 10 # Get more results internally for a better MRR calculation base
        recommendations = get_recommendations(
            query["job_title"],
            query["job_level"],
            query["competencies"],
            max_results=internal_max_results
        )

        # IDs list for MRR (uses up to internal_max_results)
        recommended_ids_for_mrr = [rec["assessment"]["id"] for rec in recommendations]
        # IDs list truncated at K for P@K, R@K
        recommended_ids_at_k = recommended_ids_for_mrr[:K]

        print(f"  Recommended IDs (Top {K}): {recommended_ids_at_k}")


        # Calculate metrics for this query
        p_at_k = precision_at_k(recommended_ids_at_k, relevant_ids, K)
        r_at_k = recall_at_k(recommended_ids_at_k, relevant_ids, K) # Recall still based on finding within top K

        precisions.append(p_at_k)
        recalls.append(r_at_k)
        # For MRR, use the full list (up to internal_max_results) and the full relevant list
        all_recommended_ids.append(recommended_ids_for_mrr)
        all_relevant_ids.append(relevant_ids)

        print(f"  Precision@{K}: {p_at_k:.2f}")
        print(f"  Recall@{K}:    {r_at_k:.2f}\n")


    # Calculate overall average metrics
    valid_queries = len(precisions) # Number of queries actually processed
    if valid_queries == 0:
        print("No valid queries processed. Cannot calculate average metrics.")
        return None

    avg_precision = sum(precisions) / valid_queries
    avg_recall = sum(recalls) / valid_queries
    # MRR calculation uses the lists stored in all_recommended_ids and all_relevant_ids
    mrr = mean_reciprocal_rank(all_recommended_ids, all_relevant_ids)

    print("--- Evaluation Summary ---")
    print(f"Total Queries Evaluated: {valid_queries} (out of {len(TEST_SET)})")
    print(f"K value for Precision/Recall: {K}")
    print(f"Average Precision@{K}: {avg_precision:.3f}")
    print(f"Average Recall@{K}:    {avg_recall:.3f}")
    # MRR is calculated based on the rank of the *first* relevant item found within the recommendations generated
    print(f"Mean Reciprocal Rank (MRR): {mrr:.3f}")
    print("--- Evaluation Complete ---")

    return {
        "avg_precision_at_k": avg_precision,
        "avg_recall_at_k": avg_recall,
        "mrr": mrr,
        "k": K,
        "num_queries_evaluated": valid_queries
    }

if __name__ == "__main__":
    results = run_evaluation()
    if results:
        print("\nEvaluation finished successfully.")
        # Optional: Save results
        # with open("evaluation_results_refined.json", "w") as f:
        #    json.dump(results, f, indent=2)