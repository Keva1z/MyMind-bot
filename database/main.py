import logging
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from .models import Base
from bot.config import config

logging.basicConfig(level=logging.INFO)

engine = create_async_engine(
    url=config.database_url,
    echo=False,
)
async_session = async_sessionmaker(engine)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logging.info("Database connected")