import logging

import litestar as ls

from random_pycon_2024_bot import controller
from random_pycon_2024_bot import deps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


app = ls.Litestar(
    route_handlers=[controller.RootController],
    plugins=[deps.db_plugin],
    on_startup=[deps.init_db, deps.get_tg_app],
    on_shutdown=[deps.close_tg_app],
)
