from caching import CachingBTGC
import os

if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    CachingBTGC.dump_to_json(log_local=True)
    