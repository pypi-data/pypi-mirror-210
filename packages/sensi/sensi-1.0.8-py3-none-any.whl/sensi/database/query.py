"""
modul-modul untuk query database
"""
import asyncio
import os
from functools import cache
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from sensi.database.models import (
    Likelihood,
    Prior,
    StopWords,
    Training,
)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dataset.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}?check_same_thread=False"
engine = create_async_engine(DB_URL)
session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def read_db(object) -> Any:
    async with engine.connect() as conn:
        return await conn.execute(select(object))


@cache
def read_stop_words() -> set:
    """Read all stop words"""
    stops = asyncio.run(read_db(StopWords))
    return {data.content for data in stops}


@cache
def read_all_training() -> dict:
    """Read all training dataset"""
    data = asyncio.run(read_db(Training))
    return {d.id: {"text": d.text, "label": d.label} for d in data}


@cache
def read_log_prior() -> float:
    """get prior value"""
    data = asyncio.run(read_db(Prior))
    data = [d.logprior for d in data]
    return data[0]


@cache
def read_log_likelihood() -> dict:
    """list all log likelihoods"""
    data = asyncio.run(read_db(Likelihood))
    return {d.text: d.loglikelihood for d in data}
