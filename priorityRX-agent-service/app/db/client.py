import os
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, JSON, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./agent_demo.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # IMPORTANT for Celery
)
metadata = MetaData()

routing = Table('routing_decisions', metadata,
                Column('id', String, primary_key=True),
                Column('refill_id', String),
                Column('pharmacy', String),
                Column('score', Float),
                )

outcomes = Table('refill_outcomes', metadata,
                 Column('id', String, primary_key=True),
                 Column('refill_id', String),
                 Column('pharmacy', String),
                 Column('success', Boolean),
                 Column('time_to_fulfill_minutes', Integer),
                 )

def init_db():
    metadata.create_all(engine)

class DBClient:
    def __init__(self):
        init_db()

    def log_routing_decision(self, refill_id, pharmacy, pred):
        conn = engine.connect()
        ins = routing.insert().values(id=refill_id, refill_id=refill_id, pharmacy=pharmacy, score=pred.get('eta'))
        conn.execute(ins)
        conn.close()

    def log_outcome(self, refill_id, pharmacy, success=True, time_to_fulfill_minutes=60):
        conn = engine.connect()
        ins = outcomes.insert().values(id=refill_id, refill_id=refill_id, pharmacy=pharmacy, success=success, time_to_fulfill_minutes=time_to_fulfill_minutes)
        conn.execute(ins)
        conn.close()
