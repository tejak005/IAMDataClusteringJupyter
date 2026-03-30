from fastapi import FastAPI, Depends, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import pandas as pd
import joblib
import os

app = FastAPI(title="IAM Discovery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Relative to this file's folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "iam_review.db")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
ANOMALIES_CSV = os.path.join(os.path.dirname(__file__), "..", "output", "high_risk_anomalies.csv")
ENRICHED_CSV = os.path.join(os.path.dirname(__file__), "..", "output", "identities_enriched_results.csv")

_cached_clusters = None

class Token(BaseModel):
    access_token: str
    token_type: str

class PredictRequest(BaseModel):
    department: str
    job_title: str
    location: str

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_dominant_attributes(cluster_id: int, cursor):
    # Get dominant department
    cursor.execute('''
        SELECT i.department, COUNT(DISTINCT i.identity_id) as cnt
        FROM identities i
        JOIN access_review_scores a ON i.identity_id = a.identity_id
        WHERE a.cluster_id = ?
        GROUP BY i.department
        ORDER BY cnt DESC
        LIMIT 1
    ''', (cluster_id,))
    dept_row = cursor.fetchone()
    dominant_department = dept_row["department"] if dept_row else "Unknown"

    # Get dominant job title
    cursor.execute('''
        SELECT i.job_title, COUNT(DISTINCT i.identity_id) as cnt
        FROM identities i
        JOIN access_review_scores a ON i.identity_id = a.identity_id
        WHERE a.cluster_id = ?
        GROUP BY i.job_title
        ORDER BY cnt DESC
        LIMIT 1
    ''', (cluster_id,))
    title_row = cursor.fetchone()
    dominant_job_title = title_row["job_title"] if title_row else "Unknown"
    
    return {
        "cluster_id": cluster_id,
        "dominant_department": dominant_department,
        "dominant_job_title": dominant_job_title
    }

@app.post("/api/auth/login", response_model=Token)
async def login(username: str = Form(...), password: str = Form(...)):
    # Mock authentication
    if username and password:
        return {"access_token": "mock_token_123", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.get("/api/anomalies")
def get_anomalies():
    try:
        df = pd.read_csv(ANOMALIES_CSV)
        cols = ['identity_id', 'identity_name', 'department', 'job_title', 'status']
        available_cols = [c for c in cols if c in df.columns]
        anomalies_df = df[available_cols].fillna("")
        if 'identity_name' in anomalies_df.columns:
            anomalies_df.rename(columns={'identity_name': 'name'}, inplace=True)
        anomalies = anomalies_df.to_dict(orient="records")
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clusters")
def get_clusters():
    global _cached_clusters
    if _cached_clusters is not None:
        return _cached_clusters
    try:
        df = pd.read_csv(ENRICHED_CSV)
        cluster_profiles = df.groupby('kmeans_peer_group').agg(
            total_users=('status', 'count'),
            dominant_department=('department', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'),
            dominant_job_title=('job_title', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown')
        ).reset_index()
        cluster_profiles.rename(columns={'kmeans_peer_group': 'cluster_id'}, inplace=True)
        _cached_clusters = cluster_profiles.to_dict(orient="records")
        return _cached_clusters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/identities/search")
def search_identities(query: str = "", limit: int = 100, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    search_term = f"%{query}%"

    cursor.execute('PRAGMA table_info(identities)')
    columns = [row["name"] for row in cursor.fetchall()]

    if "identity_name" in columns:
        cursor.execute('''
            SELECT identity_id, identity_name as name, department, job_title, status
            FROM identities 
            WHERE identity_id LIKE ? OR identity_name LIKE ? OR department LIKE ? OR job_title LIKE ?
            LIMIT ?
        ''', (search_term, search_term, search_term, search_term, limit))
    else:
        cursor.execute('''
            SELECT identity_id, department, job_title, status
            FROM identities 
            WHERE identity_id LIKE ? OR department LIKE ? OR job_title LIKE ?
            LIMIT ?
        ''', (search_term, search_term, search_term, limit))

    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/api/identities/{identityId}/access-review")
def get_access_review(identityId: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute('PRAGMA table_info(identities)')
    columns = [row["name"] for row in cursor.fetchall()]

    if "identity_name" in columns:
        cursor.execute('''
            SELECT identity_id, identity_name as name, department, job_title, status
            FROM identities 
            WHERE identity_id = ?
        ''', (identityId,))
    else:
        cursor.execute('''
            SELECT identity_id, department, job_title, status
            FROM identities 
            WHERE identity_id = ?
        ''', (identityId,))
    identity = cursor.fetchone()
    
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
        
    cursor.execute('''
        SELECT cluster_id, access_item_name, item_type, lift, global_adoption_rate, confidence_score, validation_status
        FROM access_review_scores 
        WHERE identity_id = ?
        ORDER BY confidence_score DESC
    ''', (identityId,))
    access_items = cursor.fetchall()
    
    peer_group_info = None
    if access_items and access_items[0]["cluster_id"] is not None:
        cluster_id = access_items[0]["cluster_id"]
        peer_group_info = get_dominant_attributes(cluster_id, cursor)
    
    return {
        "identity": dict(identity),
        "peer_group_info": peer_group_info,
        "access_items": [dict(row) for row in access_items]
    }

@app.post("/api/recommendations/predict")
def predict_recommendations(req: PredictRequest, db: sqlite3.Connection = Depends(get_db)):
    try:
        loaded_scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
        loaded_svd = joblib.load(os.path.join(MODELS_DIR, 'svd_model.pkl'))
        loaded_kmeans = joblib.load(os.path.join(MODELS_DIR, 'kmeans_iam_model.pkl'))
        expected_columns = joblib.load(os.path.join(MODELS_DIR, 'model_columns.pkl'))
        
        row = {}
        hr = {"department": req.department, "job_title": req.job_title, "location": req.location}
        for k, v in hr.items():
            col_name = f"{k}_{v}"
            row[col_name] = 1 
            
        row['total_entitlements_count'] = 0
        row['high_risk_entitlements_count'] = 0
        
        df_new = pd.DataFrame([row])
        df_new = df_new.reindex(columns=expected_columns, fill_value=0)
        
        agg_cols = ['total_entitlements_count', 'high_risk_entitlements_count']
        df_new[agg_cols] = loaded_scaler.transform(df_new[agg_cols])
        
        features_reduced = loaded_svd.transform(df_new)
        predicted_group = loaded_kmeans.predict(features_reduced)
        cluster_id = int(predicted_group[0])
        
        # Get recommendations for this cluster
        cursor = db.cursor()
        cursor.execute('''
            SELECT DISTINCT access_item_name, item_type, lift, global_adoption_rate, validation_status, confidence_score
            FROM access_review_scores
            WHERE cluster_id = ?
            ORDER BY confidence_score DESC
            LIMIT 10
        ''', (cluster_id,))
        recommendations = cursor.fetchall()
        
        peer_group_info = get_dominant_attributes(cluster_id, cursor)
        
        recs_out = []
        for r in recommendations:
            r_dict = dict(r)
            # The frontend multiplies confidence score by 100 for the predict endpoint
            r_dict['confidence_score'] = r_dict['confidence_score'] / 100.0
            recs_out.append(r_dict)
            
        return {
            "predicted_cluster_id": cluster_id,
           "peer_group_info": peer_group_info,
            "recommendations": recs_out
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
