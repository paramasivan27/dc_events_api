from fastapi import FastAPI, HTTPException, Query
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import os

app = FastAPI()

# Use environment variables for database connection settings
DB_NAME = os.getenv("DB_NAME", "POSTGRES_DB" )
DB_USER = os.getenv("DB_USER", "POSTGRES_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "host.docker.internal")  # Default to 'localhost', overridden by Docker environment
DB_PORT = os.getenv("DB_PORT", "5432")

@app.get("/events")
async def get_events(
    product_id: int,
    date: Optional[str] = Query(None, description="Filter by transaction date (YYYY-MM-DD)"),
    location_id: Optional[int] = Query(None, description= "Filter by location ID")
    ):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """SELECT event_id, 
                event_type, 
                product_id, 
                location_id,
                soh_impact, 
                transaction_date, 
                transaction_time 
            FROM DC_Event
            WHERE product_id = %s"""
        params = [product_id]

        if date:
            query += " AND transaction_date = %s"
            params.append(date)
        
        if location_id:
            query += " AND location_id = %s"
            params.append(location_id)

        # Query to get events for the given PRODUCT_ID
        cursor.execute(query, tuple(params))
        events = cursor.fetchall()

        cursor.close()
        conn.close()

        if not events:
            raise HTTPException(status_code=404, detail="No events found for the given PRODUCT_ID")

        return {"product_id": product_id, "events": events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))