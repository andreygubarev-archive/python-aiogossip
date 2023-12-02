import os

GOSSIP_SEEDS = os.getenv("GOSSIP_SEEDS")
GOSSIP_DEBUG = os.getenv("GOSSIP_DEBUG", False)
MUTEX_TTL = int(os.getenv("GOSSIP_MUTEX_TTL", 60))
