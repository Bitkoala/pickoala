import asyncio
from sqlalchemy import text
from app.database import engine

async def check_schema():
    print("Checking users table schema...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("DESCRIBE users"))
            columns = result.fetchall()
            found = False
            for col in columns:
                print(f"Column: {col[0]}")
                if col[0] == 'casdoor_id':
                    found = True
            
            if found:
                print("\nSUCCESS: 'casdoor_id' column found.")
            else:
                print("\nERROR: 'casdoor_id' column is MISSING from 'users' table.")
                print("This is likely the cause of the 500 error.")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
