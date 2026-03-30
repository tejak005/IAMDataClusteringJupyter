try:
	import plotly
	from sklearn.preprocessing import StandardScaler
	from sklearn.decomposition import TruncatedSVD
except ImportError:
	%pip install -q scikit-learn plotly
	from sklearn.preprocessing import StandardScaler
	from sklearn.decomposition import TruncatedSVD

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt


# Define the directory containing the Parquet files
data_dir = os.path.join('data', 'iam_dataset')

# Read each Parquet file into a separate DataFrame
account_entitlements_df = pd.read_parquet(os.path.join(data_dir, 'account_entitlements.parquet'))
accounts_df = pd.read_parquet(os.path.join(data_dir, 'accounts.parquet'))
applications_df = pd.read_parquet(os.path.join(data_dir, 'applications.parquet'))
entitlement_group_assignments_df = pd.read_parquet(os.path.join(data_dir, 'entitlement_group_assignments.parquet'))
entitlement_group_relations_df = pd.read_parquet(os.path.join(data_dir, 'entitlement_group_relations.parquet'))
group_entitlements_df = pd.read_parquet(os.path.join(data_dir, 'group_entitlements.parquet'))
entitlement_groups_df = pd.read_parquet(os.path.join(data_dir, 'entitlement_groups.parquet'))
entitlements_df = pd.read_parquet(os.path.join(data_dir, 'entitlements.parquet'))
identities_df = pd.read_parquet(os.path.join(data_dir, 'identities.parquet'))
resources_df = pd.read_parquet(os.path.join(data_dir, 'resources.parquet'))

# Print the shapes of the DataFrames
print(f"Shape of account_entitlements_df: {account_entitlements_df.shape}")
print(f"Shape of accounts_df: {accounts_df.shape}")
print(f"Shape of applications_df: {applications_df.shape}")
print(f"Shape of entitlement_group_assignments_df: {entitlement_group_assignments_df.shape}")
print(f"Shape of entitlement_group_relations_df: {entitlement_group_relations_df.shape}")
print(f"Shape of entitlement_groups_df: {entitlement_groups_df.shape}")
print(f"Shape of entitlements_df: {entitlements_df.shape}")
print(f"Shape of identities_df: {identities_df.shape}")
print(f"Shape of resources_df: {resources_df.shape}")

# Group by 'identity_id' and count the number of accounts for each user
accounts_per_user = accounts_df.groupby('identity_id').size()

# Get the distribution of the number of accounts
account_distribution = accounts_per_user.value_counts()

print("Distribution of accounts per user:")
print(account_distribution)

# --- Analysis for account_entitlements ---

# Group by 'account_id' and count the number of entitlements for each account
entitlements_per_account = account_entitlements_df.groupby('account_id').size()

# Get the distribution of the number of entitlements
entitlement_distribution = entitlements_per_account.value_counts()

print("Distribution of entitlements per account:")
print(entitlement_distribution)

# Create a bar plot of the entitlement distribution
import plotly.express as px
fig = px.bar(
    x=entitlement_distribution.index, 
    y=entitlement_distribution.values, 
    labels={'x':'Number of Entitlements', 'y':'Number of Accounts'},
    title='Distribution of Entitlements per Account'
)
fig.update_layout(xaxis_type='category')
fig.show()



# --- Analysis for entitlement_group_assignments ---

# Group by 'identity_id' and count the number of entitlement groups for each identity
entitlement_groups_per_identity = entitlement_group_assignments_df.groupby('identity_id').size()

# Get the distribution of the number of entitlement groups
entitlement_group_distribution = entitlement_groups_per_identity.value_counts()

print("\nDistribution of entitlement groups per identity:")
print(entitlement_group_distribution)

# Create a bar plot of the entitlement group distribution
import plotly.express as px
fig = px.bar(
    x=entitlement_group_distribution.index, 
    y=entitlement_group_distribution.values, 
    labels={'x':'Number of Entitlement Groups', 'y':'Number of Identities'},
    title='Distribution of Entitlement Groups per Identity'
)
fig.update_layout(xaxis_type='category')
fig.show()


print("applications_df columns:", applications_df.columns)
print("resources_df columns:", resources_df.columns)
print("entitlements_df columns:", entitlements_df.columns)
print("account_entitlements_df columns:", account_entitlements_df.columns)
print("accounts_df columns:", accounts_df.columns)

# --- Analysis for application to resource mapping ---

# Group by 'app_id' and count the number of resources for each application
resources_per_app = resources_df.groupby('app_id').size()

# Get the distribution of the number of resources
resource_distribution = resources_per_app.value_counts().sort_index()

print("Distribution of resources per application:")
print(resource_distribution)

# Create a bar plot of the resource distribution
import plotly.express as px
fig = px.bar(
    x=resource_distribution.index, 
    y=resource_distribution.values, 
    labels={'x':'Number of Resources', 'y':'Number of Applications'},
    title='Distribution of Resources per Application'
)
fig.update_layout(xaxis_type='category')
fig.show()


# --- Analysis for resource to entitlement mapping ---

# Group by 'resource_id' and count the number of entitlements for each resource
entitlements_per_resource = entitlements_df.groupby('resource_id').size()

# Get the distribution of the number of entitlements per resource
resource_entitlement_dist = entitlements_per_resource.value_counts().sort_index()

print("Distribution of entitlements per resource:")
print(resource_entitlement_dist)

# Create a bar plot of the resource to entitlement distribution
import plotly.express as px
fig = px.bar(
    x=resource_entitlement_dist.index, 
    y=resource_entitlement_dist.values, 
    labels={'x':'Number of Entitlements', 'y':'Number of Resources'},
    title='Distribution of Entitlements per Resource'
)
fig.update_layout(xaxis_type='category')
fig.show()


# --- Analysis for entitlement to account mapping ---

# Group by 'entitlement_id' and count the number of unique accounts for each entitlement
accounts_per_entitlement = account_entitlements_df.groupby('entitlement_id')['account_id'].nunique()

# Get the distribution of the number of accounts per entitlement
account_dist_per_entitlement = accounts_per_entitlement.value_counts().sort_index()

print("Distribution of accounts per entitlement:")
print(account_dist_per_entitlement)

# Create a bar plot of the distribution
import plotly.express as px
fig = px.bar(
    x=account_dist_per_entitlement.index, 
    y=account_dist_per_entitlement.values, 
    labels={'x':'Number of Accounts', 'y':'Number of Entitlements'},
    title='Distribution of Accounts per Entitlement'
)
fig.update_layout(xaxis_type='category')
fig.show()


# User–entitlement mapping: merge account_entitlements with entitlements to get entitlement_name
user_entitlements_df = (
    account_entitlements_df[['identity_id', 'entitlement_id']]
    .merge(entitlements_df[['entitlement_id', 'entitlement_name']], on='entitlement_id', how='left')
    [['identity_id', 'entitlement_name']]
    .drop_duplicates()
)
print("user_entitlements_df shape:", user_entitlements_df.shape)
user_entitlements_df.head()

# --- Analysis for entitlement group assignment distribution ---

# Group by 'ent_group_id' and count the number of identities assigned to each group
group_size = entitlement_group_assignments_df.groupby('ent_group_id').size()

# Get the distribution of the number of assignments
group_dist = group_size.value_counts().sort_index()

print("Distribution of assignment counts per Entitlement Group:")
print(group_dist)

# Create a bar plot of the distribution
import plotly.express as px
fig = px.bar(
    x=group_dist.index.astype(int), 
    y=group_dist.values, 
    labels={'x':'Number of Identities Assigned', 'y':'Number of Groups'},
    title='Distribution of Assignments per Entitlement Group'
)
fig.update_layout(xaxis_type='category')
fig.show()


# --- Step 1: Contextual Feature Engineering (HR Data) ---
# Isolate active users (assume column 'status' with value 'Active'; adjust if your schema differs)
active_identities_df = identities_df[identities_df['status'] == 'Active'].copy()

# One-Hot Encode department, job_title, location; set identity_id as index
hr_features_df = pd.get_dummies(
    active_identities_df[['identity_id', 'department', 'job_title', 'location']],
    columns=['department', 'job_title', 'location'],
    dtype=int
).set_index('identity_id')

print("Step 1 — HR features shape:", hr_features_df.shape)
hr_features_df.head()

# --- Step 2: Behavioral Feature Engineering (User–Entitlement Sparse Matrix) ---
# Build binary User-Entitlement matrix: 1 if user holds entitlement, 0 otherwise
access_features_df = user_entitlements_df.assign(has_entitlement=1).pivot_table(
    index='identity_id',
    columns='entitlement_name',
    values='has_entitlement',
    aggfunc='max',
    fill_value=0
)

print("Step 2 — Access matrix shape:", access_features_df.shape)
access_features_df.iloc[:5, :5]

# --- Step 3: Aggregate Feature Creation ---
total_entitlements_count = account_entitlements_df.groupby('identity_id').size()

high_risk_entitlements_count = (
    account_entitlements_df
    .loc[account_entitlements_df['assignment_type'] == 'Adhoc_Anomaly']
    .groupby('identity_id')
    .size()
)

agg_features_df = pd.DataFrame({
    'total_entitlements_count': total_entitlements_count,
    'high_risk_entitlements_count': high_risk_entitlements_count
}).fillna(0).astype(int)

print("Step 3 — Aggregate features shape:", agg_features_df.shape)
agg_features_df.head()

# --- Step 4: Final Assembly & Scaling ---
try:
	from sklearn.preprocessing import StandardScaler
except ImportError:
	%pip install -q scikit-learn
	from sklearn.preprocessing import StandardScaler

# Concatenate HR, access, and aggregate features on identity_id index; fill NaNs with 0
master_feature_matrix_df = pd.concat(
    [hr_features_df, access_features_df, agg_features_df],
    axis=1,
    join='outer'
).fillna(0)

# Scale only aggregate numerical columns so they don't overpower binary columns
agg_cols = ['total_entitlements_count', 'high_risk_entitlements_count']
scaler = StandardScaler()
master_feature_matrix_df[agg_cols] = scaler.fit_transform(master_feature_matrix_df[agg_cols])

print("Step 4 — Master feature matrix shape:", master_feature_matrix_df.shape)
master_feature_matrix_df[agg_cols].describe()

# --- Step 5: Dimensionality Reduction (TruncatedSVD) ---
try:
	from sklearn.decomposition import TruncatedSVD
except ImportError:
	%pip install -q scikit-learn
	from sklearn.decomposition import TruncatedSVD

n_components = 100
svd = TruncatedSVD(n_components=n_components, random_state=42)
X_reduced = svd.fit_transform(master_feature_matrix_df)

print("Step 5 — Reduced matrix shape:", X_reduced.shape)
print("\nExplained variance ratio (first 100 components):")
print(svd.explained_variance_ratio_)
print("\nCumulative explained variance:", svd.explained_variance_ratio_.sum())

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# --- Find optimal k using Silhouette Score ---
k_values = list(range(5, 51, 5))
silhouette_scores = []

for k in k_values:
    # Set n_init to suppress warnings and ensure consistency
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_reduced)
    score = silhouette_score(X_reduced, labels)
    silhouette_scores.append(score)

# Plot the Silhouette Scores
import plotly.express as px
fig = px.line(
    x=k_values, 
    y=silhouette_scores, 
    markers=True, 
    labels={'x':'Number of Clusters (k)', 'y':'Silhouette Score'},
    title='Silhouette Score vs. Number of Clusters (k)'
)
fig.update_traces(line=dict(dash='dash', color='blue'))
fig.show()

# --- Fit optimal/default model ---
# Once you review the plot, you could dynamically change this, but we'll default to 20
optimal_k = 20
kmeans_model = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
kmeans_labels = kmeans_model.fit_predict(X_reduced)

# Create a results DataFrame mapped to identity_id 
# (Assuming the row order of X_reduced aligns with master_feature_matrix_df.index)
df_results = pd.DataFrame(index=master_feature_matrix_df.index)
df_results['kmeans_peer_group'] = kmeans_labels

# Instantiate and fit DBSCAN model
# Note: Both eps and min_samples will likely need tuning based on the density / scale 
# of your specific X_reduced matrix. If too many points are flagged as anomalies (or none), 
# try adjusting these hyperparameters first.
dbscan_model = DBSCAN(eps=0.5, min_samples=5)
dbscan_labels = dbscan_model.fit_predict(X_reduced)

# Extract labels and add them to our tracking dataframe
df_results['dbscan_label'] = dbscan_labels

# Explicitly flag users with a dbscan label of -1 as anomalies
df_results['is_anomaly'] = df_results['dbscan_label'] == -1

# Merge the clustering results back into the original dataframe
# Since df_results was created using master_feature_matrix_df.index, we can use a direct join
df_identities_enriched = identities_df.set_index('identity_id').join(df_results, how='inner')

# Print the total count of anomalies detected by DBSCAN
total_anomalies = df_identities_enriched['is_anomaly'].sum()
print(f'Total anomalies detected by DBSCAN: {total_anomalies}')

# Quick sanity check visualization of the enriched dataframe
display(df_identities_enriched.head())

import plotly.graph_objects as go
import numpy as np

# Create a boolean mask for anomalies
anomaly_mask = df_results['is_anomaly']

# Extract coordinates specifically for the identified anomalies
x_anomalies = X_reduced[anomaly_mask, 0]
y_anomalies = X_reduced[anomaly_mask, 1]

fig = go.Figure()

# Scatter plot of the general clusters
fig.add_trace(go.Scatter(
    x=X_reduced[~anomaly_mask, 0], 
    y=X_reduced[~anomaly_mask, 1], 
    mode='markers',
    marker=dict(
        color=df_results[~anomaly_mask]['kmeans_peer_group'], 
        colorscale='Viridis', 
        opacity=0.5,
        size=8,
        showscale=True,  # To show the legend/colorbar for clusters
        colorbar=dict(title="KMeans Group", x=1.13)
    ),
    name='Cluster Member',
    hoverinfo='text',
    text=df_results[~anomaly_mask]['kmeans_peer_group'].apply(lambda c: f'Cluster: {c}')
))

# Overlay the DBSCAN anomalies as distinct, large red 'X' markers
fig.add_trace(go.Scatter(
    x=x_anomalies, 
    y=y_anomalies, 
    mode='markers', 
    marker=dict(
        color='red', 
        symbol='x',
        size=12, 
        line=dict(color='black', width=1)
    ),
    name='DBSCAN Anomaly',
    hoverinfo='text',
    text=['Anomaly'] * len(x_anomalies)
))

fig.update_layout(
    title='IAM Peer Group Clusters and Anomalies (First 2 Components)',
    xaxis_title='Component 1',
    yaxis_title='Component 2',
    width=1000,
    height=600,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.02, title='Legend')
)

fig.show()


# Group by kmeans_peer_group and calculate mode for department and job_title, and count total users
cluster_profiles = df_identities_enriched.groupby('kmeans_peer_group').agg(
    total_users=('status', 'count'),
    dominant_department=('department', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'),
    dominant_job_title=('job_title', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown')
).reset_index()

print("Cluster Profiles Summary:")
display(cluster_profiles)

# Create a bar chart showing the size of each cluster
import plotly.express as px
fig = px.bar(
    cluster_profiles,
    x='kmeans_peer_group',
    y='total_users',
    color='dominant_department',
    labels={'kmeans_peer_group': 'Cluster ID', 'total_users': 'Number of Users', 'dominant_department': 'Department'},
    title='Cluster Sizes Categorized by Dominant Department'
)
fig.update_layout(xaxis_type='category')
fig.show()

# Filter the DataFrame for anomalies
df_anomalies = df_identities_enriched[df_identities_enriched['is_anomaly'] == True]

# Group anomalies to analyze the risk origins
anomaly_analysis = df_anomalies.groupby(['department', 'job_title']).size().reset_index(name='anomaly_count')
anomaly_analysis = anomaly_analysis.sort_values(by='anomaly_count', ascending=False)

print("Top Anomaly Origins by Department and Job Title:")
display(anomaly_analysis.head(10))

# Bar chart of anomalies by department
anomalies_by_dept = df_anomalies.groupby('department').size().reset_index(name='anomaly_count')
fig = px.bar(
    anomalies_by_dept.sort_values(by='anomaly_count', ascending=False),
    x='department',
    y='anomaly_count',
    color='department',
    labels={'department': 'Department', 'anomaly_count': 'Number of Anomalies'},
    title='Count of Anomalies by Department'
)
fig.update_layout(showlegend=False)
fig.show()

total_users = len(df_identities_enriched)
total_peer_groups = df_identities_enriched['kmeans_peer_group'].nunique()
total_anomalies = df_anomalies.shape[0]

# Getting the top 3 departments with most anomalies
top_3_anomaly_depts = df_anomalies['department'].value_counts().head(3).index.tolist()

print("== IAM Peer Group Analysis: Executive Summary ==")
print(f"Total Identities Processed: {total_users:,}")
print(f"Total Peer Groups Discovered: {total_peer_groups}")
print(f"Total High-Risk Anomalies Flagged: {total_anomalies} ({(total_anomalies/total_users)*100:.2f}% of users)")
print(f"Top 3 Departments Contributing to Anomalies: {', '.join(top_3_anomaly_depts)}")
print("================================================")

import joblib
import os

# Create a directory for models if it doesn't exist
models_dir = 'models'
os.makedirs(models_dir, exist_ok=True)

# Note: In the previous cells, we used StandardScaler and TruncatedSVD but didn't save them to variables.
# Assuming they were created like: scaler = StandardScaler() and svd = TruncatedSVD(n_components=100)
# For completeness in deployment, we re-instantiate and fit them here or assume they exist.

try:
    # Save the models
    joblib.dump(kmeans_model, os.path.join(models_dir, 'kmeans_iam_model.pkl'))
    joblib.dump(dbscan_model, os.path.join(models_dir, 'dbscan_iam_model.pkl'))
    
    # Also save the scaler and SVD if they exist in your workspace
    if 'scaler' in locals():
        joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    if 'svd' in locals():
        joblib.dump(svd, os.path.join(models_dir, 'svd_model.pkl'))
    if 'master_feature_matrix_df' in locals():
        joblib.dump(master_feature_matrix_df.columns, os.path.join(models_dir, 'model_columns.pkl'))
        
    print(f"Models successfully saved to the '{models_dir}' directory.")
except Exception as e:
    print(f"Error saving models: {e}")

# Create an output directory
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Export to CSV
csv_path = os.path.join(output_dir, 'identities_enriched_results.csv')
df_identities_enriched.to_csv(csv_path)
print(f"Results successfully exported to {csv_path}")

# Optionally export the anomalies separately for quick access
anomalies_csv_path = os.path.join(output_dir, 'high_risk_anomalies.csv')
df_anomalies.to_csv(anomalies_csv_path)
print(f"Anomalies specifically exported to {anomalies_csv_path}")

import joblib
import os
import pandas as pd
import numpy as np

def predict_peer_group(new_user_features):
    """
    Demonstration function of how to use the saved models.
    
    Args:
        new_user_features (dict): A dictionary containing 'hr_features' and 'expected_access' arrays.
    """
    try:
        # 1. Load models & expected feature column names
        loaded_scaler = joblib.load(os.path.join('models', 'scaler.pkl'))
        loaded_svd = joblib.load(os.path.join('models', 'svd_model.pkl'))
        loaded_kmeans = joblib.load(os.path.join('models', 'kmeans_iam_model.pkl'))
        expected_columns = joblib.load(os.path.join('models', 'model_columns.pkl'))
        
        # 2. Preprocess payload into a single-row DataFrame
        row = {}
        
        # A. Map HR Features to One-Hot columns
        hr = new_user_features.get('hr_features', {})
        for k, v in hr.items():
            col_name = f"{k}_{v}"
            row[col_name] = 1  # Mark as presence (1)
            
        # B. Map Access Features to corresponding binary entitlement IDs
        access = new_user_features.get('expected_access', [])
        for ent_id in access:
            row[ent_id] = 1
            
        # C. Construct Aggregate Features
        row['total_entitlements_count'] = len(access)
        row['high_risk_entitlements_count'] = new_user_features.get('high_risk_count', 0)
        
        # Create DataFrame from the dictionary row
        df_new = pd.DataFrame([row])
        
        # Reindex to match the exact shape of master_feature_matrix_df, filling missing info with 0
        df_new = df_new.reindex(columns=expected_columns, fill_value=0)
        
        # Scale numerical aggregate columns using the saved Scaler
        agg_cols = ['total_entitlements_count', 'high_risk_entitlements_count']
        df_new[agg_cols] = loaded_scaler.transform(df_new[agg_cols])
        
        # Apply Dimensionality Reduction using the saved SVD
        features_reduced = loaded_svd.transform(df_new)
        
        # 3. Predict the cluster group
        predicted_group = loaded_kmeans.predict(features_reduced)
        return f"Successfully mapped to Peer Group: {predicted_group[0]}"
        
    except FileNotFoundError:
        return "Models not found. Ensure they are saved first by running Step 1."
    except Exception as e:
        return f"Error during prediction: {e}"

# --- Working Example ---
# Create a mock onboarding user that mimics our data structure
mock_new_user = {
    "identity_id": "test_service_account",
    "hr_features": {
        "department": "IT", 
        "job_title": "SysAdmin",
        "location": "Remote"
    },
    "expected_access": [
        "ENT_12345", "ENT_67890", "ENT_ABCDE"  # Examples of some dummy entitlements
    ],
    "high_risk_count": 1
}

print("Testing Inference Function:")
print(predict_peer_group(mock_new_user))


import pandas as pd

# 1. Calculate Cluster Size
# We isolate DBSCAN anomalies (is_anomaly == True) to create a pure baseline 
valid_users = df_identities_enriched[df_identities_enriched['is_anomaly'] == False].reset_index()[['identity_id', 'kmeans_peer_group']].copy()
valid_users.rename(columns={'kmeans_peer_group': 'cluster_id'}, inplace=True)

# Total users in each distinct K-Means cluster
cluster_sizes = valid_users.groupby('cluster_id').size().reset_index(name='total_users')

# -------------------------------------------------------------------
# A. Confidence Score for Individual Entitlements
# -------------------------------------------------------------------

# Ensure unique identity-to-entitlement mappings
user_entitlements = valid_users.merge(account_entitlements_df[['identity_id', 'entitlement_id']], on='identity_id', how='inner').drop_duplicates()

# 2. Calculate Item Frequency (Entitlements)
ent_freq = user_entitlements.groupby(['cluster_id', 'entitlement_id']).size().reset_index(name='item_frequency')

# 3. Compute the Confidence Score (Entitlements)
ent_scores = ent_freq.merge(cluster_sizes, on='cluster_id')
ent_scores['confidence_score'] = (ent_scores['item_frequency'] / ent_scores['total_users']) * 100

# Map entitlement_id to actual entitlement_name
ent_scores = ent_scores.merge(entitlements_df[['entitlement_id', 'entitlement_name']], on='entitlement_id', how='left')
ent_scores.rename(columns={'entitlement_name': 'access_item_name'}, inplace=True)
ent_scores['item_type'] = 'entitlement'

# Map back to individual user
user_ent_scores = user_entitlements.merge(
    ent_scores[['cluster_id', 'entitlement_id', 'access_item_name', 'item_type', 'confidence_score']], 
    on=['cluster_id', 'entitlement_id'], 
    how='left'
)
user_ent_scores.drop(columns=['entitlement_id'], inplace=True)

# -------------------------------------------------------------------
# B. Confidence Score for Entitlement Groups
# -------------------------------------------------------------------

# Ensure unique identity-to-group mappings
user_groups = valid_users.merge(entitlement_group_assignments_df[['identity_id', 'ent_group_id']], on='identity_id', how='inner').drop_duplicates()

# 2. Calculate Item Frequency (Groups)
grp_freq = user_groups.groupby(['cluster_id', 'ent_group_id']).size().reset_index(name='item_frequency')

# 3. Compute the Confidence Score (Groups)
grp_scores = grp_freq.merge(cluster_sizes, on='cluster_id')
grp_scores['confidence_score'] = (grp_scores['item_frequency'] / grp_scores['total_users']) * 100

# Map ent_group_id to actual group_name
grp_scores = grp_scores.merge(entitlement_groups_df[['ent_group_id', 'group_name']], on='ent_group_id', how='left')
grp_scores.rename(columns={'group_name': 'access_item_name'}, inplace=True)
grp_scores['item_type'] = 'entitlement_group'

# Map back to individual user
user_grp_scores = user_groups.merge(
    grp_scores[['cluster_id', 'ent_group_id', 'access_item_name', 'item_type', 'confidence_score']], 
    on=['cluster_id', 'ent_group_id'], 
    how='left'
)
user_grp_scores.drop(columns=['ent_group_id'], inplace=True)

# -------------------------------------------------------------------
# 4. Map Back to the User (Final Output)
# -------------------------------------------------------------------
# Combine both entitlements and entitlement groups into one unpivoted dataframe
df_access_review_scores = pd.concat([user_ent_scores, user_grp_scores], ignore_index=True)

# Sort logically for output display
df_access_review_scores.sort_values(by=['cluster_id', 'confidence_score'], ascending=[True, False], inplace=True)
df_access_review_scores.reset_index(drop=True, inplace=True)

print("Sample of Peer Adoption Rate Confidence Scores:")
display(df_access_review_scores['confidence_score'].describe())


# -------------------------------------------------------------------
# Validation Phase: Global Adoption Rate & Lift Calculation
# -------------------------------------------------------------------

import pandas as pd
import numpy as np

print("Calculating Global Adoption Rates and Lift for validation...")

# 1. Total unique identities in the company
total_company_users = identities_df['identity_id'].nunique()

# 2. Calculate global frequency of each entitlement (unique users, not accounts)
ent_global_counts = account_entitlements_df.groupby('entitlement_id')['identity_id'].nunique().reset_index(name='global_user_frequency')
# FIX: Use 'entitlement_name' instead of 'name'
ent_global_counts = ent_global_counts.merge(entitlements_df[['entitlement_id', 'entitlement_name']], on='entitlement_id', how='left')
ent_global_counts.rename(columns={'entitlement_name': 'access_item_name'}, inplace=True)

# Group frequency (unique users)
grp_global_counts = entitlement_group_assignments_df.groupby('ent_group_id')['identity_id'].nunique().reset_index(name='global_user_frequency')
# FIX: Use 'ent_group_id' and 'group_name' instead of 'entitlement_group_id' and 'name'
grp_global_counts = grp_global_counts.merge(entitlement_groups_df[['ent_group_id', 'group_name']], on='ent_group_id', how='left')
grp_global_counts.rename(columns={'group_name': 'access_item_name'}, inplace=True)

# Combine for a single lookup
global_adoption = pd.concat([
    ent_global_counts[['access_item_name', 'global_user_frequency']], 
    grp_global_counts[['access_item_name', 'global_user_frequency']]
], ignore_index=True)

# Calculate Global Adoption Rate (Percentage)
global_adoption['global_adoption_rate'] = (global_adoption['global_user_frequency'] / total_company_users) * 100

# 3. Merge Global Adoption Rate back into the Confidence Scores DataFrame
df_validated_scores = df_access_review_scores.merge(
    global_adoption[['access_item_name', 'global_adoption_rate']], 
    on='access_item_name', 
    how='left'
)

# 4. Calculate Lift
# Lift = Cluster Adoption Rate (confidence_score) / Global Adoption Rate
df_validated_scores['lift'] = df_validated_scores['confidence_score'] / (df_validated_scores['global_adoption_rate'] + 1e-9)

# 5. Define Validation Status logic
def assign_validation_status(row):
    confidence = row['confidence_score']
    lift = row['lift']
    
    if pd.isna(confidence) or pd.isna(lift):
        return 'Unknown'
    if confidence >= 80 and lift >= 2.0:
        return 'Valid Auto-provisioning candidate'
    elif confidence >= 80 and lift < 2.0:
        return 'Basic Right (Global Baseline)'
    elif confidence < 20 and lift < 0.5:
        return 'Anomaly / Revocation candidate'
    elif confidence < 50:
        return 'Low Confidence (Review Required)'
    else:
        return 'Moderate (Monitor)'

# Apply the logic
df_validated_scores['validation_status'] = df_validated_scores.apply(assign_validation_status, axis=1)

# Sort the validated scores logically
df_validated_scores.sort_values(by=['cluster_id', 'lift', 'confidence_score'], ascending=[True, False, False], inplace=True)
df_validated_scores.reset_index(drop=True, inplace=True)

# Display a sample of the results
print("Sample of Validated Confidence Scores:")
display(df_validated_scores[['cluster_id', 'access_item_name', 'item_type', 'confidence_score', 'global_adoption_rate', 'lift', 'validation_status']].head(20))

# -------------------------------------------------------------------
# Phase 6: Export Data to SQLite for API 
# -------------------------------------------------------------------
import sqlite3
import os

print("Exporting ML data to SQLite database for the API...")

db_path = "iam_review.db"
conn = sqlite3.connect(db_path)

# 1. Export Identities for search API
identities_df.to_sql("identities", conn, if_exists="replace", index=False)

# 2. Export Validated Confidence Scores
# Make sure it only includes the final columns the API needs.
api_scores = df_validated_scores[[
    'identity_id', 'cluster_id', 'access_item_name', 'item_type', 
    'confidence_score', 'global_adoption_rate', 'lift', 'validation_status'
]]
api_scores.to_sql("access_review_scores", conn, if_exists="replace", index=False)

conn.close()
print(f"Export complete! Database saved to {os.path.abspath(db_path)}")
