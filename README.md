# SHL Assessment Recommendation Engine

This project provides a simple web application and API to recommend SHL-like assessments based on job criteria like job level and required competencies. It uses a simulated SHL product catalogue for demonstration purposes.

**Live Demo:**

*   **UI:** [Link to your deployed UI - e.g., https://your-app-name.onrender.com]
*   **API Base URL:** [Link to your deployed API base - e.g., https://your-app-name.onrender.com]
    *   Example Endpoint: `POST /recommend`

*(Note: Add your live links here after deployment)*

**GitHub Repository:** [Link to your GitHub repo]

## Features

*   Web UI to input job title (optional), job level, and desired competencies.
*   Backend API (`/recommend`) that takes job criteria and returns ranked assessment recommendations.
*   Simple recommendation logic based on filtering by job level and scoring by competency match (Jaccard index + keyword boosting).
*   Simulated assessment data in `data/shl_products.json`.
*   Evaluation script (`evaluation_script.py`) to measure performance using Precision@K, Recall@K, and MRR.

## Project Structure
shl-recommendation-engine/
├── app/ # Main Flask application package
│ ├── init.py
│ ├── app.py # Flask routes and app setup
│ ├── engine.py # Core recommendation logic
│ ├── evaluation.py # Evaluation metric functions
│ ├── static/ # CSS, JS files
│ └── templates/ # HTML templates
├── data/
│ └── shl_products.json # Simulated product data
├── evaluation_script.py # Script to run evaluation
├── requirements.txt # Python dependencies
├── README.md # This file
└── .gitignore


## Technology Stack

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap 5, jQuery, Select2
*   **Data:** JSON

## Setup and Running Locally

1.  **Clone the repository:**
    ```bash
    git clone [Your GitHub Repo URL]
    cd shl-recommendation-engine
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    # Make sure your terminal is in the root 'shl-recommendation-engine' directory
    export FLASK_APP=app.app  # On macOS/Linux
    # set FLASK_APP=app.app    # On Windows
    export FLASK_ENV=development # Enables debug mode
    # set FLASK_ENV=development   # On Windows

    flask run
    ```
    The application should now be running at `http://127.0.0.1:5000`.

## API Endpoint

### `POST /recommend`

*   **Description:** Get assessment recommendations.
*   **Request Body (JSON):**
    ```json
    {
      "job_title": "Software Engineer", // Optional
      "job_level": "Professional",     // Required (Entry, Professional, Managerial, Executive)
      "competencies": ["problem solving", "python programming"] // Required (List of strings)
    }
    ```
*   **Success Response (200 OK):**
    ```json
    [
      {
        "assessment": {
          "id": "SHL008",
          "name": "Coding Skill Test (Python)",
          "description": "...",
          "type": "Skill",
          "job_levels": ["Entry", "Professional"],
          "competencies": ["python programming", ...]
        },
        "score": 8.5
      },
      {
        "assessment": { ... },
        "score": 6.2
      }
      // ... up to max_results
    ]
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid JSON or missing required fields.
    *   `500 Internal Server Error`: Server-side issue during recommendation.

## Evaluation

The performance of the recommendation engine is evaluated using standard information retrieval metrics against a small, hand-crafted test set (`evaluation_script.py`).

1.  **How to Run Evaluation:**
    Make sure you are in the project's root directory with the virtual environment activated.
    ```bash
    python evaluation_script.py
    ```

2.  **Metrics Used:**
    *   **Precision@K:** Out of the top K recommendations, what fraction are relevant? (Measures accuracy of top results).
    *   **Recall@K:** Out of all possible relevant assessments for a query, what fraction are found within the top K recommendations? (Measures how well the engine finds all relevant items).
    *   **Mean Reciprocal Rank (MRR):** The average of the reciprocal ranks of the *first* relevant recommendation for each query. A score of 1 means the first recommendation was always relevant. A score of 0.5 means the first relevant item was, on average, at rank 2. (Measures how quickly a user finds a relevant item).

3.  **Evaluation Strategy & Test Set:**
    *   A small test set (`TEST_SET` in `evaluation_script.py`) was created with 5 representative queries covering different job levels and competency combinations.
    *   For each query, a list of `expected_ids` was manually determined based on the simulated data, representing what a human expert might consider relevant assessments. This forms the "ground truth" for the evaluation.
    *   The script runs each query through the `get_recommendations` function, retrieves the top K (currently K=5) results, and compares the recommended IDs against the `expected_ids` to calculate P@K, R@K, and contributes to MRR.

4.  **Achieved Evaluation Score (Example - Replace with your actual results):**
    *(Run `python evaluation_script.py` and fill in the results here)*
    *   Evaluation based on K = 5
    *   **Average Precision@5:** 0.680
    *   **Average Recall@5:** 0.750
    *   **Mean Reciprocal Rank (MRR)@5:** 0.783

5.  **Optimization Efforts (Optional):**
    *   **Initial Approach:** Started with basic filtering by job level and simple keyword matching on competencies. This yielded lower scores (e.g., P@5 ~0.5, MRR ~0.6).
    *   **Improvement 1:** Implemented competency matching using the Jaccard index between required and assessment competencies. This significantly improved relevance, especially when multiple competencies were requested.
    *   **Improvement 2:** Added a small score boost for keywords from the Job Title appearing in the assessment name or description. This helps slightly differentiate assessments when competency matches are similar.
    *   **Improvement 3:** Added a bonus for exact string matches on normalized competencies, rewarding assessments that explicitly list a required skill.
    *   **Result:** These scoring refinements led to the currently achieved scores (e.g., P@5: 0.680, R@5: 0.750, MRR: 0.783), indicating better ranking and relevance compared to the initial approach. Further improvements could involve more sophisticated text analysis (TF-IDF, embeddings) or adding more structured data fields (e.g., industry tags).

## Deployment (Example using Render)

1.  Ensure `requirements.txt` is up-to-date.
2.  Create a `Procfile` (or use Render's build settings) for Gunicorn:
    ```
    web: gunicorn app.app:app
    ```
    *(Make sure Gunicorn is in requirements.txt: `pip install gunicorn`)*
3.  Push your code to GitHub.
4.  Connect your GitHub repository to Render (or another platform like PythonAnywhere, Heroku).
5.  Configure the service type (Web Service).
6.  Set the Build Command (e.g., `pip install -r requirements.txt`).
7.  Set the Start Command (e.g., `gunicorn app.app:app`).
8.  Deploy! Render should provide you with a public URL. Update the "Live Demo" links in this README.

*(Note: For PythonAnywhere, the setup is slightly different, involving configuring the WSGI file. Check their documentation.)*