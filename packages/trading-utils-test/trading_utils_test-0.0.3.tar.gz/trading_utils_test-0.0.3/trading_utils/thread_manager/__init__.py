import uuid
import smiley as sm
from threading import Thread
from logger import get_trading_logger
import asyncio
import concurrent

logger = get_trading_logger()
informers = sm.smiley_collection()


async def thread_executor(app, process, spy_smiley, *args):
    try:
        logger.info('Executing thread', extra={'thread_request_info': {'app': app, 'process': process}})
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, process, app.app_context(), *args)

        spy_smiley.set_response(result)
        spy_smiley.set_status(200, 'SUCCESS')

    except Exception as e:
        spy_smiley.set_status(500, 'ERROR')
        logger.error(f"Failed executing thread. Message: {e}", exc_info=True)


def run_in_thread(app, process_to_run, *args):
    logger.info('Executing process in thread', extra={'process_request_info': {'app': app, 'process': process_to_run}})
    thread_id = str(uuid.uuid4())
    spy_smiley = sm.smiley(thread_id)
    informers.add(spy_smiley)
    worker_loop = asyncio.new_event_loop()
    worker = Thread(target=sm.start_loop, args=(worker_loop,))
    worker.start()
    asyncio.run_coroutine_threadsafe(thread_executor(
        app, process_to_run, spy_smiley, *args), loop=worker_loop)
    spy_smiley.set_status(201, 'RUNNING')

    return thread_id


def get_thread_status(idx):
    informers_reporting = informers.get()
    logger.info('Fetching thread status. Alive informers available in log data', extra={'alive_informers': informers_reporting})
    informer = informers_reporting[idx]
    reported_status = informer.get_status()

    return reported_status


def get_thread_result(idx):
    informers_reporting = informers.get()
    informer = informers_reporting[idx]
    response = informer.get_response()
    informers.remove_by_id(idx)

    return response
