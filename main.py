import asyncio
import logging
from cterasdk import AsyncGlobalAdmin, settings, Object
from pathlib import Path
import os

settings.sessions.management.ssl = False


async def save_cursor(cursor):
    print(cursor)
    """Use this function to persist the cursor"""


async def process_event(admin, event):
    """Process an event"""
    if event.type == 'file' and not event.deleted:
        ancestors = await admin.notifications.ancestors(event)
        cloud_folder = await admin.v1.api.get(f'/   objs/{event.folder_id}')
        fullpath = Path(cloud_folder.webDavPartialUrl).joinpath(
            Path(*[ancestor.name for ancestor in ancestors[1:]])).as_posix()
        print(f'Downloading: {fullpath}...')
        response = await admin._generic.get(f'/admin/webdav/{fullpath}')
        local_path = fullpath.lstrip('/').replace('%20', ' ')
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'w+b') as fd:
            async for chunk in response.chunk():
                fd.write(chunk)
    else:
        print(f'{event.name} is a Folder or Deleted, Skipping Download...')


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
        """Start event consumer to process events"""
        consumer = asyncio.create_task(worker(admin, queue))
        await consumer
        await admin.logout()


if __name__ == '__main__':
    asyncio.run(main())
