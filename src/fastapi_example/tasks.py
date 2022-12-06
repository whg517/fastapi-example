import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Shanghai'))
