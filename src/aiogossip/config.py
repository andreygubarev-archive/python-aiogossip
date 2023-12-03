import os

SEEDS = os.getenv("GOSSIP_SEEDS")
DEBUG = os.getenv("GOSSIP_DEBUG", False)
MUTEX_TTL = int(os.getenv("GOSSIP_MUTEX_TTL", 60))
