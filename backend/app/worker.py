"""One-shot ingest for cron: python -m app.worker"""
from app.db.session import Base, engine
from app.services.ingest import run_ingest

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print(f"Ingest complete: {len(run_ingest())} high-score events.")

