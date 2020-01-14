#!/usr/bin/env python
import os
import sys
import json

from subprocess import Popen
from googleads import ad_manager
from googleads import oauth2

FILE_BUFFER = 16 * 1024


def main():
    """Main function encapsulating everything this extractor does
    """
    config_path = sys.argv[1] if len(sys.argv) == 2 else "/data/config.json"

    if not os.path.exists(config_path):
        raise Exception(
            "Configuration not specified, was expected at '{}'".format(config_path))

    with open(config_path, encoding="utf-8") as conf_file:
        conf = json.load(conf_file)["parameters"]

    # Store credentials in a file
    with open("./service.json", "w", encoding="utf-8") as service_file:
        json.dump(conf["#service_account"], service_file)

    # OAuth2 credential info
    key_file = "./service.json"

    oauth2_client = oauth2.GoogleServiceAccountClient(
        key_file,
        oauth2.GetAPIScope('ad_manager')
    )

    ad_manager_client = ad_manager.AdManagerClient(
        oauth2_client,
        "ex-bizztreat-google-ad-manager",
        network_code=conf["network_code"]
    )

    downloader = ad_manager_client.GetDataDownloader(version="v201911")

    # test report job
    report_job = conf["report_job"]

    print("Waiting for job completion...")
    job = downloader.WaitForReport(report_job)

    print("job: {}".format(job))

    output_path = "./output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print("Job completed, downloading...")

    # download
    with open("./output/output.csv", "wb") as fid:
        downloader.DownloadReportToFile(
            job,
            "CSV",
            fid,
            use_gzip_compression=False,
            include_totals_row=False
        )

    # Remove "Dimension." from header
    #Popen("sed -i '1s/Dimension.//g' ./output/output.csv", shell=True)
    # Remove "Column." from header
    #Popen("sed -i '1s/Column.//g' ./output/output.csv", shell=True)

if __name__ == "__main__":
    main()
