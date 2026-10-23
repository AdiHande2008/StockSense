import sys
import os
import uvicorn

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.jobs.seed_data import seed_database

def main():
    print("=" * 65)
    print("  StockSense AI - Backend API & Machine Learning Engine")
    print("=" * 65)
    print("Initializing database and models...")
    seed_database(force=False)
    
    print("\n[READY] Starting FastAPI server on http://127.0.0.1:8000")
    print("[DOCS]  Swagger UI available at: http://127.0.0.1:8000/docs")
    print("=" * 65 + "\n")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
