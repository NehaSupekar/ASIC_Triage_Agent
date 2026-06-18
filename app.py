import streamlit as st
import os
import pandas as pd
from vector_engine import LogVectorEngine

db = LogVectorEngine()

st.set_page_config(page_title="ASIC Triage Dashboard", page_icon="🤖", layout="wide")

st.title("🤖 ASIC Triage Agent V2 Dashboard")
st.markdown("Real-time automated error signature clustering and multi-agent architectural triage analysis.")
st.markdown("---")

# Force refresh button
if st.button("🔄 Force Refresh Database"):
    st.rerun()

# Load fresh collection data
collection = db.collection
data = collection.get(include=["metadatas", "documents"])

if not data or not data["ids"]:
    st.info("📂 The ChromaDB directory is currently empty. Drop a new `.log` file into your `./logs/` folder to wake up the engine!")
else:
    # Process dataframe
    records = []
    for idx, doc_id in enumerate(data["ids"]):
        meta = data["metadatas"][idx]
        records.append({
            "File Name": doc_id,
            "Cluster ID": meta.get("cluster_id", "Unknown"),
            "Timestamp": meta.get("timestamp", "Just Now")
        })
    
    df = pd.DataFrame(records)
    
    # Render KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logs Processed", len(df))
    col2.metric("Unique Error Clusters", df["Cluster ID"].nunique())
    col3.metric("Hardware Acceleration", "Apple M4 (Metal)")
    
    st.markdown("---")
    
    # Display split columns
    left_col, right_col = st.columns([1, 1.2])
    
    with left_col:
        st.subheader("🗄️ Database Inventory")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with right_col:
        st.subheader("🕵️‍♂️ Cluster Deep-Dive & Root Cause Analysis")
        
        unique_clusters = sorted(df["Cluster ID"].unique())
        selected_cluster = st.selectbox("Select an Error Cluster to inspect:", unique_clusters)
        
        # Pull metadata for the selected cluster explicitly
        cluster_meta = None
        for meta in data["metadatas"]:
            if meta.get("cluster_id") == selected_cluster:
                cluster_meta = meta
                break
        
        if cluster_meta and "analysis_report" in cluster_meta:
            st.markdown("#### 🚨 Latest Swarm Architect Verdict:")
            st.write(cluster_meta["analysis_report"])
        else:
            st.info(f"💡 No cached report found for {selected_cluster}. Showing shortcut matching routing state.")