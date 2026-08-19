import asyncio
import os
import sys
from sqlalchemy import text

# Ensure the backend package is importable and the .env file is loaded by running from the repo root
ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.database import get_mysql_engine

async def main():
    engine = get_mysql_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SHOW COLUMNS FROM courses LIKE 'color_hex'"))
        rows = result.fetchall()
        print('columns:', rows)

if __name__ == '__main__':
    asyncio.run(main())
