import os
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from vector_engine import LogVectorEngine
from agent_swarm import AgentSwarm

db_engine = LogVectorEngine()
swarm_engine = AgentSwarm()

class LogFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.log'):
            return
        
        time.sleep(0.5) 
        log_path = event.src_path
        filename = os.path.basename(log_path)
        print(f"\n⚡ [Agent Event] Processing incoming log: {filename}")
        
        cluster_id, is_new_bug = db_engine.add_or_query_log(log_path)
        
        if is_new_bug:
            print(f"🤖 New signature category found. Initializing multi-agent debate loop...")
            
            # 🛠️ FIX: Read the exact file text safely to ensure the LLM receives the payload
            with open(log_path, "r") as f:
                raw_log_content = f.read()
            
            # Run the async debate with explicit raw text
            analysis_result = asyncio.run(swarm_engine.execute_triage_debate(raw_log_content))
            
            # 🛠️ FIX: Update ChromaDB's persistent memory with the analysis report!
            try:
                db_engine.collection.update(
                    ids=[filename],
                    metadatas=[{
                        "cluster_id": cluster_id,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis_report": analysis_result # Storing the LLM summary right here
                    }]
                )
                print(f"💾 Multi-agent analysis report permanently cached inside ChromaDB for {cluster_id}.")
            except Exception as e:
                print(f"❌ Failed to save report to database: {e}")
                
            print("\n==================================================")
            print(f"🚨 FINAL ROOT CAUSE SUMMARY FOR {cluster_id}:")
            print(analysis_result)
            print("==================================================\n")
        else:
            print(f"⏭️ Auto-grouped into {cluster_id}. Skipping deep multi-agent debate cycle.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 ASIC Triage Backend Live. Monitoring ./logs/ directory natively...")
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path="./logs", recursive=False)
    observer.start()
    yield
    observer.stop()
    observer.join()

app = FastAPI(title="ASIC Triage Agent V2 Engine", lifespan=lifespan)