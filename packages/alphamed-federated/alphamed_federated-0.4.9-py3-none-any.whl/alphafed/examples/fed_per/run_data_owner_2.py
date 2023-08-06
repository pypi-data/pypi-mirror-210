import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHONPATH = os.path.join(CURRENT_DIR, os.pardir, os.pardir, os.pardir)
sys.path.insert(0, PYTHONPATH)

if True:
    from alphafed import logger
    from alphafed.examples.fed_per import DATA_OWNER_2_ID
    from alphafed.examples.fed_per.demos import (get_scheduler, get_task_id)


task_id = get_task_id()
scheduler = get_scheduler()
logger.debug(f'{type(scheduler)=}')
scheduler._run(id=DATA_OWNER_2_ID, task_id=task_id)
