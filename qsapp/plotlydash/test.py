
import dash_html_components as html

import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module TEST.py loaded")

test_layout = html.H1(children="TEST", className="h2 pt-3 pb-3")