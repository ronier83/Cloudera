import logging
import asyncio
import cterasdk.settings
from cterasdk import AsyncGlobalAdmin, core_types

async def main():
    cterasdk.settings.sessions.management.ssl = False  # for untrusted or self-signed certificates
    async with AsyncGlobalAdmin('192.168.27.202') as admin:
        await admin.login('admin', 'password1!')
        tenantadmin = core_types.UserAccount('svc')
        mdc_tenantadmin = core_types.CloudFSFolderFindingHelper('Research Project', tenantadmin)
        cloud_drivers = [mdc_tenantadmin]

        metadatalist = await admin.notifications.get(cloudfolders=cloud_drivers)
        
        # Process the initial batch of objects
        for obj in metadatalist.objects:
            print(obj)

        # Continue fetching while there are more objects
        while metadatalist.more:
            cursor = metadatalist.cursor
            print(metadatalist.cursor)
            metadatalist = await admin.notifications.get(cloudfolders=cloud_drivers, cursor=cursor)
            for obj in metadatalist.objects:
                print(obj)

        await admin.logout()

if __name__ == '__main__':
    asyncio.run(main())
