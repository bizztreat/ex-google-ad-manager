#!/usr/bin/env python
import os
import sys
import json

from googleads import ad_manager
from googleads import oauth2

def main():
    """Main function encapsulating everything this extractor does
    """
    config_path = sys.argv[1] if len(sys.argv) == 2 else "/data/config.json"

    if not os.path.exists(config_path):
        raise Exception("Configuration not specified, was expected at '{}'".format(config_path))

    with open(config_path, encoding="utf-8") as conf_file:
        conf = json.load(conf_file)["parameters"]

    ## Store credentials in a file
    with open("/tmp/service.json", "w", encoding="utf-8") as service_file:
        json.dump(conf["service_account"], service_file)

    # OAuth2 credential info
    key_file = "/tmp/service.json"

    oauth2_client = oauth2.GoogleServiceAccountClient(
        key_file,
        oauth2.GetAPIScope('ad_manager')
        )

    ad_manager_client = ad_manager.AdManagerClient(
        oauth2_client,
        "ex-bizztreat-google-ad-manager"
        )

    print(ad_manager_client.GetService("NetworkService").getAllNetworks())

if __name__ == "__main__":
    main()
