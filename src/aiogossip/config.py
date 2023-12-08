import os

SEEDS = os.getenv("AIOGOSSIP_SEEDS")
DEBUG = os.getenv("AIOGOSSIP_DEBUG", False)
MUTEX_TTL = int(os.getenv("AIOGOSSIP_MUTEX_TTL", 60))
LOG_LEVEL = os.getenv("AIOGOSSIP_LOG_LEVEL", "INFO")
