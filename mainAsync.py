import asyncio
import logging
from cterasdk import AsyncGlobalAdmin, settings, Object
from pathlib import Path
import os
import aiofiles

settings.sessions.management.ssl = False

async def save_cursor(cursor):
    print(cursor)
    """Use this function to persist the cursor"""

async def get_fullpath(admin, event):
    ancestors = await admin.notifications.ancestors(event)  
    cloud_folder = await admin.v1.api.get(f'/objs/{event.folder_id}')
    fullpath = Path(cloud_folder.webDavPartialUrl).joinpath(
        Path(*[ancestor.name for ancestor in ancestors[1:]])).as_posix()
    response = await admin.io.webdav.download(fullpath)
    return fullpath, response

async def get_localpath(fullpath):
    local_path = fullpath.lstrip('/').replace('%20', ' ')
    return local_path

async def mkdir_local(local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

async def download_file(local_path, response):
    async with aiofiles.open(local_path, 'w+b') as f:
        async for chunk in response.chunk():
            await f.write(chunk)

async def process_event(admin, event):
    """Process an event"""
    if event.type == 'file' and not event.deleted:
        fullpath, response = await get_fullpath(admin, event)
        local_path = await get_localpath(fullpath)
        await mkdir_local(local_path)
        print(f'Downloading: {fullpath}...')
        await download_file(local_path, response)
    else:
        print(f'{event.name} is a folder or a deleted file, Skipping Download...')

async def worker(admin, queue):
    """Sample worker thread"""
    while True:
        event = await queue.get()
        try:
            await process_event(admin, event)
        except Exception as e:
            logging.getLogger().error(f' {e} Error Message')
        finally:
            queue.task_done()  # Service will not produce events unless all tasks are done.

async def main():
    cursor = None
    queue = asyncio.Queue()  # Shared queue between producer and consumer threads
    async with AsyncGlobalAdmin('192.168.27.202') as admin:
        await admin.login('admin', 'password1!')
        """Start event producer service."""
        admin.notifications.service.run(queue, save_cursor, cursor=cursor)
        """Start multiple event consumers to process events concurrently"""
        num_workers = 10  # Number of concurrent workers
        consumers = [asyncio.create_task(worker(admin, queue)) for _ in range(num_workers)]
        await asyncio.gather(*consumers)
        await admin.logout()

if __name__ == '__main__':
    asyncio.run(main())
