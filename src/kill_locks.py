from sqlalchemy import text
from src.core.database import SessionLocal

db = SessionLocal()
try:
    print("Listing all connections...")
    result = db.execute(text("""
        SELECT pid, query, state, age(clock_timestamp(), query_start) 
        FROM pg_stat_activity 
        WHERE pid <> pg_backend_pid();
    """)).all()
    
    for row in result:
        print(f"Conn: PID={row[0]} | Query={row[1]} | State={row[2]} | Age={row[3]}")
        
    # Terminate all connections except ours
    print("Terminating connections...")
    terminated = db.execute(text("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE pid <> pg_backend_pid();
    """)).all()
    print(f"Terminated {len(terminated)} connections.")
    
except Exception as e:
    print("Error:", e)
finally:
    db.close()
