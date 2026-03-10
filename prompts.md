Act as a Senior Data Scientist specializing in Identity and Access Management (IAM). I am currently building a clustering model for Role Mining, but my current feature engineering (One-Hot Encoding) is too simple and misses context.

I need you to write a Python script to implement two specific advanced feature engineering techniques.

Assume I have a pandas DataFrame named `hr_df` with the following columns: `user_id`, `job_title`, and `manager_id`.

Please implement the following:

1. NLP Embeddings for Job Titles (Semantic Similarity)
   - Problem: Standard encoding treats "Senior Engineer" and "Jr Engineer" as unrelated.
   - Solution: Use the `sentence-transformers` library (e.g., model 'all-MiniLM-L6-v2') to generate dense vector embeddings for the `job_title` column.
   - Output: Replace (or augment) the text column with these numerical vector features so the clustering model understands semantic closeness.

2. Graph Features for Organizational Structure (Hierarchy)
   - Problem: "Manager ID" is currently treated as a flat category, ignoring hierarchy.
   - Solution: Use the `networkx` library to build a directed graph from `user_id` and `manager_id`.
   - Feature 1: Calculate "Distance to CEO" (node depth/shortest path to the root).
   - Feature 2: Calculate "Team Size" (total number of direct and indirect reports).
   - Output: Add these two scalar features to `hr_df`.

Please provide the complete, runnable Python code to perform these transformations.









Act as a Senior Data Scientist specializing in Identity and Access Management (IAM).

I am improving the feature engineering for my role mining clustering model. My current aggregate features are simple counts and are not capturing enough business context or risk. I need you to write a Python function to generate more advanced, context-aware aggregate features.

Assume I have the following pandas DataFrames already loaded, which correspond to the schema in my project:
- `identities_df`
- `apps_df`
- `resources_df`
- `accounts_df`
- `account_entitlements_df`

Please write a single, well-documented Python function that takes these DataFrames as input and returns a new DataFrame containing the features below, indexed by `identity_id`.

**1. Risk-Weighted Aggregations (Business Context):**
   - **Goal:** Differentiate users based on the criticality of the access they hold.
   - **Logic:** Join across the tables to link an entitlement grant to its parent application's `business_criticality`.
   - **Required Features:**
     - `critical_access_count`: A count of entitlements belonging to 'Critical' applications.
     - `critical_access_ratio`: The ratio of a user's critical entitlements to their total entitlements.

**2. Peer-Relative Z-Scores (Statistical Context):**
   - **Goal:** Identify users who have an anomalous amount of access *relative to their direct peers*.
   - **Logic:** For each user, calculate the Z-score of their total entitlement count compared to the mean and standard deviation of their `department`.
   - **Required Feature:**
     - `access_zscore_vs_dept`: The calculated Z-score. Please ensure you handle departments with only one person to avoid division-by-zero errors.

**3. Temporal Velocity (Behavioral Context):**
   - **Goal:** Detect rapid accumulation of access, which can be a sign of privilege creep or an attack.
   - **Logic:** Use the `grant_date` from `account_entitlements_df` to count recent changes.
   - **Required Feature:**
     - `recent_grant_count_90d`: The total number of entitlements granted to the user within the last 90 days.

The final output should be a clean pandas DataFrame containing the `identity_id` and all the newly generated features, with any missing values handled appropriately (e.g., filled with 0).







Act as a Senior Data Scientist specializing in Identity and Access Management (IAM).

I need to perform the final assembly and scaling of my feature matrix (Step 4). My previous approach using simple `StandardScaler` failed because the data is highly skewed (a few admins have massive access) and the HR features were drowning out the actual access patterns.

Assume I have three DataFrames ready to merge, indexed by `identity_id`:
- `access_svd_df`: The reduced dimensionality vectors of user entitlements (from TruncatedSVD).
- `hr_features_df`: Encoded HR attributes (embeddings or one-hot).
- `aggregate_features_df`: Numerical counts (e.g., `total_entitlements`, `risk_score`).

Please write a Python function to perform the following advanced assembly and scaling:

1. **Log-Transformation for Skew:**
   - Identify count-based columns in `aggregate_features_df` (e.g., `total_entitlements`, `total_accounts`).
   - Apply `np.log1p` (log(x+1)) to these columns to normalize the power-law distribution.

2. **Robust Scaling:**
   - Apply `sklearn.preprocessing.RobustScaler` to the aggregate features. This uses the median and IQR, making it resilient to the extreme outliers common in IAM data.

3. **Strategic Feature Weighting:**
   - I want the actual access patterns (SVD components) to be the primary driver of the clusters.
   - Multiply the `access_svd_df` values by a weight of **2.0**.
   - Keep HR and Aggregate features at a weight of **1.0**.

4. **Final Assembly:**
   - Concatenate all processed frames into a single `final_feature_matrix`.
   - Ensure the index (`identity_id`) is preserved.

Provide the complete, runnable code.




Act as an expert Machine Learning Engineer. I am working on a Jupyter Notebook for an IAM (Identity and Access Management) Peer Group Analysis project following the CRISP-DM methodology. 

I have already completed the Data Understanding, Data Preparation, and Modeling phases. 
Here is a summary of the current state of my notebook:
1. Feature Engineering: I created HR features (one-hot encoded `department`, `job_title`, `location`), a binary User-Entitlement access matrix, and aggregate features (scaled counts of total and high-risk entitlements). I reduced this combined matrix using TruncatedSVD into `X_reduced`.
2. Modeling: I applied K-Means (k=20) to `X_reduced` to discover peer groups, and DBSCAN to flag anomalies. 
3. Merging: I mapped the results back to the original identities DataFrame, resulting in a DataFrame named `df_identities_enriched`. 
4. The `df_identities_enriched` DataFrame contains the following columns: `identity_type`, `status`, `location`, `cost_center`, `department`, `job_title`, `manager_id`, `kmeans_peer_group` (int), `dbscan_label` (int), and `is_anomaly` (boolean).
5. Existing Visualization: We are strictly using `plotly.express` and `plotly.graph_objects` for all charts.

Please write the Python code cells to execute Phase 5: Evaluation from CRISP-DM. 

Specifically, I need code to accomplish the following in the notebook:

### Step 1: Cluster Profiling (Peer Group Analysis)
* We need to understand what defines each K-Means cluster. Write code to group `df_identities_enriched` by `kmeans_peer_group`.
* For each group, calculate the most frequent (mode) `department` and `job_title`, and count the total number of users in that cluster. 
* Output this as a summary DataFrame called `cluster_profiles`.
* Create a Plotly Express bar chart showing the size of each cluster, colored or grouped by the dominant department. 

### Step 2: Anomaly Deep Dive
* Filter `df_identities_enriched` to isolate the anomalies (`is_anomaly == True`) into a DataFrame called `df_anomalies`.
* Write code to analyze *where* these anomalies are coming from. Group the anomalies by `department` and `job_title` to find where the most risk lies.
* Create a Plotly Express bar chart showing the count of Anomalies by Department.

### Step 3: Business Impact Summary
* Write a final code cell that prints out a formatted executive summary for the security team (e.g., total users, total peer groups discovered, total anomalies flagged, and the top 3 departments with the highest amount of anomalies).

