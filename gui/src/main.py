import logging
import sys
from pathlib import Path

from logging_config import configure_logging

configure_logging()
log = logging.getLogger("factorio_wfc.main")

log.info("=== Factorio WFC startup ===")
log.info("Python %s", sys.version.replace("\n", " "))
log.info("Executable: %s", sys.executable)
log.info("cwd: %s", Path.cwd())

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    log.info("Importing gui.app ...")
    from gui.app import main

    log.info("gui.app imported OK")
except Exception:
    log.exception("Startup failed while importing gui.app")
    raise

if __name__ == "__main__":
    try:
        log.info("Entering main() ...")
        main()
        log.info("main() returned (Dear PyGui loop ended)")
    except Exception:
        log.exception("Unhandled exception in main()")
        raise
