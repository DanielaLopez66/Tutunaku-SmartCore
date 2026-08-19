import asyncio
import os
import sys
from sqlalchemy import text

# Ensure we run from the backend root so .env is loaded correctly
ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.database import get_mysql_engine

async def main():
    engine = get_mysql_engine()
    async with engine.begin() as conn:
        # Check whether the column already exists
        result = await conn.execute(text("SHOW COLUMNS FROM courses LIKE 'color_hex'"))
        exists = result.fetchone() is not None
        if not exists:
            await conn.execute(text("ALTER TABLE courses ADD COLUMN color_hex VARCHAR(7) NOT NULL DEFAULT '#FF6B6B'"))
        # Ensure any existing NULL values are fixed
        await conn.execute(text("UPDATE courses SET color_hex = '#FF6B6B' WHERE color_hex IS NULL"))
    print('Migration applied (column existed=' + str(exists) + ')')

if __name__ == '__main__':
    asyncio.run(main())
