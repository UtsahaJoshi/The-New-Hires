import asyncio
from sqlalchemy import inspect
from database import engine

async def check():
    async with engine.connect() as conn:
        def get_columns(sync_conn):
            inspector = inspect(sync_conn)
            columns = inspector.get_columns('users')
            with open('schema.txt', 'w') as f:
                for col in columns:
                    f.write(f"{col['name']} - {col['type']}\n")
        
        await conn.run_sync(get_columns)

if __name__ == "__main__":
    asyncio.run(check())
