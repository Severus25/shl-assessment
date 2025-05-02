# app/engine.py
import json
import os
import re
from collections import defaultdict

# Path setup remains the same...
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'shl_products.json')


# Load assessments function remains the same...
def load_assessments(filepath=DATA_FILE):
    """Loads assessment data from the JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return []

# Normalize text function remains the same...
def normalize_text(text):
    """Simple text normalization."""
    if not isinstance(text, str): return "" # Handle potential non-string input
    return re.sub(r'\W+', ' ', text.lower().strip())

# --- Refined Scoring Weights and Logic ---
JACCARD_WEIGHT = 12.0  # Slightly increased weight for competency overlap
EXACT_MATCH_BONUS = 2.5 # Increased bonus for direct competency name match
TITLE_KEYWORD_WEIGHT = 0.2 # Reduced weight for job title keywords
DESCRIPTION_KEYWORD_WEIGHT = 0.1 # Added separate, lower weight for description keywords
JOB_LEVEL_MISMATCH_PENALTY = -3.0 # Penalty if job levels are clearly incompatible

# Define job level hierarchy for mismatch penalty
JOB_LEVEL_ORDER = ["Entry", "Professional", "Managerial", "Executive"]
JOB_LEVEL_INDEX = {level: i for i, level in enumerate(JOB_LEVEL_ORDER)}

def get_recommendations(job_title, job_level, required_competencies, max_results=5):
    """
    Recommends assessments based on job level, competency matching, and keyword boosts/penalties.
    """
    assessments = load_assessments()
    if not assessments:
        return []

    if job_level not in JOB_LEVEL_INDEX:
        print(f"Warning: Provided job level '{job_level}' not recognized. Filtering might be affected.")
        target_level_index = -1 # Unknown level
    else:
        target_level_index = JOB_LEVEL_INDEX[job_level]


    normalized_competencies = set(normalize_text(c) for c in required_competencies if c) # Ensure c is not empty/None
    normalized_job_title = normalize_text(job_title)
    job_title_keywords = set(normalized_job_title.split())

    scored_assessments = []

    for assessment in assessments:
        assessment_levels = assessment.get("job_levels", [])
        assessment_competencies_raw = assessment.get("competencies", [])
        assessment_name = assessment.get("name", "")
        assessment_desc = assessment.get("description", "")

        # --- Initial Filtering (Job Level Compatibility) ---
        # Keep assessment if requested level is explicitly listed OR if levels are adjacent (e.g., Prof requested, assessment has Entry/Managerial)
        # More flexible than exact match, but we'll penalize larger gaps later.
        level_match = False
        min_assessment_level_idx = float('inf')
        max_assessment_level_idx = float('-inf')

        if not assessment_levels: # If assessment has no levels specified, assume it might be applicable? Or skip? Let's include for now.
             level_match = True
        else:
            for level in assessment_levels:
                 if level in JOB_LEVEL_INDEX:
                     idx = JOB_LEVEL_INDEX[level]
                     min_assessment_level_idx = min(min_assessment_level_idx, idx)
                     max_assessment_level_idx = max(max_assessment_level_idx, idx)
                     if level == job_level:
                         level_match = True
                         break # Found exact match

            # Allow adjacent levels if no exact match found and target level is known
            if not level_match and target_level_index != -1:
                 if (min_assessment_level_idx == target_level_index + 1) or \
                    (max_assessment_level_idx == target_level_index - 1):
                    level_match = True # Allow one level gap initially

        # Skip assessment if job level seems fundamentally incompatible
        # (e.g., requested Entry, assessment is only Managerial/Executive)
        # This check might be redundant if the penalty system works well, but adds safety.
        incompatible_level = False
        if target_level_index != -1 and assessment_levels:
             is_far_below = max_assessment_level_idx < target_level_index -1 # e.g., Prof requested, assess is only Entry
             is_far_above = min_assessment_level_idx > target_level_index + 1 # e.g., Prof requested, assess is only Exec
             if is_far_below or is_far_above:
                  incompatible_level = True
                  # print(f"Debug: Skipping '{assessment_name}' due to level incompatibility (req: {job_level}, has: {assessment_levels})")


        # Strict filtering: Only proceed if level seems compatible OR target level unknown
        # if not level_match or incompatible_level:
        # Relaxing this slightly - let scoring handle more, filter only extremes
        if incompatible_level:
            continue


        # --- Scoring ---
        score = 0.0
        assessment_competencies_norm = set(normalize_text(c) for c in assessment_competencies_raw)
        normalized_name = normalize_text(assessment_name)
        normalized_desc = normalize_text(assessment_desc)

        # 1. Competency Matching Score (Jaccard Index + Exact Match Bonus)
        intersection = len(normalized_competencies.intersection(assessment_competencies_norm))
        union = len(normalized_competencies.union(assessment_competencies_norm))
        if union > 0:
            jaccard_score = intersection / union
            score += jaccard_score * JACCARD_WEIGHT

        exact_matches = sum(1 for req_comp in normalized_competencies if req_comp in assessment_competencies_norm)
        score += exact_matches * EXACT_MATCH_BONUS

        # 2. Keyword Boost (Title and Description)
        title_keywords_in_name = job_title_keywords.intersection(normalized_name.split())
        score += len(title_keywords_in_name) * TITLE_KEYWORD_WEIGHT

        title_keywords_in_desc = job_title_keywords.intersection(normalized_desc.split())
        score += len(title_keywords_in_desc) * DESCRIPTION_KEYWORD_WEIGHT


        # 3. Job Level Match Score / Penalty
        level_score = 0.0
        if target_level_index != -1 and assessment_levels:
            if job_level in assessment_levels:
                level_score += 1.0 # Small bonus for exact level match
            else:
                # Calculate minimum distance
                min_dist = float('inf')
                for level in assessment_levels:
                    if level in JOB_LEVEL_INDEX:
                        dist = abs(JOB_LEVEL_INDEX[level] - target_level_index)
                        min_dist = min(min_dist, dist)

                if min_dist == 1:
                    level_score += 0.0 # No penalty/bonus for adjacent levels
                elif min_dist > 1:
                     # Apply penalty based on distance (e.g., -3 for 2 levels gap, -6 for 3 levels...)
                    level_score += JOB_LEVEL_MISMATCH_PENALTY * (min_dist -1)


        score += level_score

        # --- Store if score is positive ---
        if score > 0:
            scored_assessments.append({"assessment": assessment, "score": round(score, 2)})

    # Sort by score (descending)
    scored_assessments.sort(key=lambda x: x["score"], reverse=True)

    # Return top N results
    return scored_assessments[:max_results]


# Example Usage (for testing)
if __name__ == '__main__':
    # Add one of the new test cases
    test_title = "Senior HR Business Partner"
    test_level = "Managerial"
    test_competencies = ["interpersonal skills", "influence", "decision making", "people management"]
    recommendations = get_recommendations(test_title, test_level, test_competencies, max_results=5)
    print(f"\nRecommendations for {test_title} ({test_level}) requiring {test_competencies}:")
    if recommendations:
        for rec in recommendations:
            print(f"- {rec['assessment']['name']} (Score: {rec['score']}) Levels: {rec['assessment']['job_levels']}")
            # print(f"  Competencies: {', '.join(rec['assessment']['competencies'])}")
    else:
        print("No recommendations found.")

    test_title_2 = "Graduate Trainee - General Management"
    test_level_2 = "Entry"
    test_competencies_2 = ["problem solving", "learning agility", "adaptability", "drive"]
    recommendations_2 = get_recommendations(test_title_2, test_level_2, test_competencies_2, max_results=5)
    print(f"\nRecommendations for {test_title_2} ({test_level_2}) requiring {test_competencies_2}:")
    if recommendations_2:
         for rec in recommendations_2:
            print(f"- {rec['assessment']['name']} (Score: {rec['score']}) Levels: {rec['assessment']['job_levels']}")
    else:
        print("No recommendations found.")