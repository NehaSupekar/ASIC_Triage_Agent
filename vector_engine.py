import os
import re
import chromadb
from chromadb.utils import embedding_functions

class LogVectorEngine:
    def __init__(self):
        # 1. Initialize a persistent local database folder
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # 2. Use a lightweight, zero-cost default embedding model
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # 3. Create or get the collection for tracking failure signatures
        self.collection = self.chroma_client.get_or_create_collection(
            name="asic_failures",
            embedding_function=self.embedding_fn
        )

    def clean_log_text(self, file_path):
        """Reused from V1: Cleans dynamic noise out of raw text to focus on the bug signature"""
        with open(file_path, 'r') as f:
            text = f.read()
        
        # Strip timestamps, cycle times, and changing slack strings
        text = re.sub(r'\b\d{4,10}ns\b', '[TIME]', text)
        text = re.sub(r'Slack:\s*-?\d+\.\d+\s*ns', 'Slack: [X] ns', text)
        return text.strip()

    def add_or_query_log(self, file_path):
        """Checks if log matches an existing cluster, otherwise saves it as a new one"""
        log_name = os.path.basename(file_path)
        cleaned_content = self.clean_log_text(file_path)
        
        # If the DB is completely empty, add this as our first baseline point
        if self.collection.count() == 0:
            print(f"📦 First error signature detected. Seeding ChromaDB with {log_name}...")
            self.collection.add(
                documents=[cleaned_content],
                ids=[log_name],
                metadatas=[{"cluster_id": "Cluster_1"}]
            )
            return "Cluster_1", True # Return cluster name, and True meaning it's new

        # Query the vector space for the single closest match
        results = self.collection.query(
            query_texts=[cleaned_content],
            n_results=1
        )
        
        # Check semantic distance (Lower distance = higher match similarity)
        distance = results['distances'][0][0]
        matched_id = results['ids'][0][0]
        matched_cluster = results['metadatas'][0][0]['cluster_id']
        
        print(f"🔍 Distance check for {log_name}: {distance:.4f} against matching candidate {matched_id}")
        
        # Threshold limit: if distance < 0.4, they are nearly identical bugs
        if distance < 0.4:
            print(f"✅ Semantic Match Found! Associating {log_name} -> {matched_cluster}")
            return matched_cluster, False # Existing cluster, not new
        else:
            # Create a brand new cluster category dynamically
            new_cluster_id = f"Cluster_{self.collection.count() + 1}"
            print(f"⚠️ High distance delta. Generating new category: {new_cluster_id}")
            self.collection.add(
                documents=[cleaned_content],
                ids=[log_name],
                metadatas=[{"cluster_id": new_cluster_id}]
            )
            return new_cluster_id, True