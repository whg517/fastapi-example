import asyncio
import logging
import signal as system_signal

from fastapi_example.config import settings
from fastapi_example.log import init_log
from fastapi_example.restapi import RestAPI
from fastapi_example.tasks import scheduler
from fastapi_sqlalcmemy.extension import db

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)

logger = logging.getLogger(__name__)


class Server:
    def __init__(
            self,
    ):
        init_log()

        self._rest_api = RestAPI()

        self.should_exit = False
        self.force_exit = True

    async def start(self):
        """"""
        try:
            db.init_db(settings.DATABASE)
            self._rest_api.init()
            scheduler.start()
            await self._rest_api.start()

            self.install_signal_handlers()
            while not self.should_exit:
                # 暂时不做任何处理。
                await asyncio.sleep(0.001)
        except Exception as ex:
            logger.exception(ex)
        finally:
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        await self._rest_api.stop()

    def install_signal_handlers(self) -> None:
        """Install system signal handlers"""
        loop = asyncio.get_event_loop()

        try:
            for sig in HANDLED_SIGNALS:
                loop.add_signal_handler(sig, self.handle_exit, sig, None)
        except NotImplementedError:  # pragma: no cover
            # Windows
            for sig in HANDLED_SIGNALS:
                system_signal.signal(sig, self.handle_exit)

    def handle_exit(self, _sig, _frame):
        """Handle exit signal."""
        if self.should_exit:
            self.force_exit = True
        else:
            self.should_exit = True
