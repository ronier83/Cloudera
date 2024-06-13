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


'''
curl --location 'https://192.168.27.202/admin/v2/api/metadata/list' \
--header 'Cookie: JSESSIONID=018DFB1756A1D8BE5FDB0F37C80CB6C7' \
--header 'Content-Type: application/json' \
--data '{

    "max_results":2000,
    "folder_ids" : [40],
    "cursor":""
}'
'''

'''
curl --location 'https://192.168.27.202/admin/v2/api/metadata/ancestors' \
--header 'Cookie: JSESSIONID=C3B48E16EC14EBB1FDAFA0D669A50A86' \
--header 'Content-Type: application/json' \
--data '{
    "folder_id": 16,
    "guid":"4fbc5aca-71d7-4bbf-9928-695d3b2dc711:562"
}'
'''

'''
curl --location 'https://192.168.27.202/admin/v2/api/metadata/longpoll' \
--header 'Cookie: JSESSIONID=1EB69BACD3A3C56700063DAB7E039E95' \
--header 'Content-Type: application/json' \
--data '{
    "folder_ids": [15, 20],
  "cursor": "eyJjdXJzb3IiOiJ7XCJjbG91ZEZvbGRlcnNDdXJzb3JcIjo0LFwiZmlsZXNDdXJzb3JcIjpcIk1URTFQVEk2TVRNMk5USTdNakE5TWpvd093PT1cIn0iLCJmb2xkZXJJZHMiOlsyMCwxNV0sInJlc2V0Rm9sZGVySWRzIjpbXX0=",
  "timeout": "2000"
}'
'''