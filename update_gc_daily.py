from read_from_gc import PriceDataGC
from caching import CachingBTGC
import os

if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    PriceDataGC.update_gc_assets_data(log_local=True)
    CachingBTGC.dump_to_json(log_local=True)
    