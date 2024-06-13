import logging
import asyncio
import os
import pathlib
import cterasdk.settings
from cterasdk import AsyncGlobalAdmin, core_types

async def main(event):
    cterasdk.settings.sessions.management.ssl = False  # for untrusted or self-signed certificates
    async with AsyncGlobalAdmin('192.168.27.102') as admin:
        await admin.login('admin', 'password1!')
        # Process the initial batch of objects
        if event.type == 'file' and not event.deleted:
            ancestors = await admin.notifications.ancestors(event)
            cloud_folder = await admin.v1.api.get(f'/   objs/{event.folder_id}')
            fullpath = Path(cloud_folder.webDavPartialUrl).joinpath(
                Path(*[ancestor.name for ancestor in ancestors[1:]])).as_posix()
            print(f'Downloading: {fullpath}...')
            # response = await admin._generic.get(f'/admin/webdav/{fullpath}')
            local_path = fullpath.lstrip('/').replace('%20', ' ')
            print(local_path)
            return local_path
        else:
            print(f'{event.name} is a Folder or Deleted, Skipping Download...')
        # Continue fetching while there are more objects

    await admin.logout()

if __name__ == '__main__':
    event = object()
    event.guid = ''
    event.folder_id = 23
    asyncio.run(main(event=event))
