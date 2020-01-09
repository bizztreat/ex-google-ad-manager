#!/usr/bin/env python
import os
import json

from googleads import ad_manager
from googleads import oauth2


service_path = "../service.json"

if not os.path.exists(service_path):
    raise Exception("Configuration not specified")

# OAuth2 credential info
key_file = service_path

oauth2_client = oauth2.GoogleServiceAccountClient(
    key_file, oauth2.GetAPIScope('ad_manager'))

ad_manager_client = ad_manager.AdManagerClient(
      oauth2_client, "ex-bizztreat-google-ad-manager")

print(ad_manager_client.GetService("NetworkService").getAllNetworks())


