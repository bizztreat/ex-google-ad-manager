#!/usr/bin/env python
import os
import sys
import json

from logging import getLogger, basicConfig, DEBUG, INFO
from datetime import datetime

from googleads import ad_manager
from googleads.common import ZeepServiceProxy
from googleads import oauth2
from slugify import slugify

FILE_BUFFER = 16 * 1024
APPLICATION_NAME = "ex-bizztreat-google-ad-manager"
API_VERSION = "v201911"
OUTPUT_DIRECTORY = "/data/out/tables"


def list_network_codes(oauth2_client):
    """List network codes and print them so that the user can select.

    Arguments:
        oauth2_client {oauth2.client} -- Logged client
    """
    ad_manager_client = ad_manager.AdManagerClient(
        oauth2_client,
        APPLICATION_NAME,
        cache=ZeepServiceProxy.NO_CACHE
    )

    network_service = ad_manager_client.GetService(
        "NetworkService", version=API_VERSION)
    networks = network_service.getAllNetworks()
    print("="*15)
    print("Listing available networks:")
    for network in networks:
        print("Network code: {} (network name: {})".format(
            network["networkCode"],
            network["displayName"]
        ))
    print("="*15)
    print("Copy selected network's code to extractor's configuration.")


def main():
    """Main function encapsulating everything this extractor does
    """

    config_path = sys.argv[1] if len(sys.argv) == 2 else "/data/config.json"

    if not os.path.exists(config_path):
        raise Exception(
            "Configuration not specified, was expected at '{}'".format(config_path))

    with open(config_path, encoding="utf-8") as conf_file:
        conf = json.load(conf_file)["parameters"]

    basicConfig(
        format="[{asctime}] [{levelname}]: {message}",
        style="{",
        level=DEBUG if conf["debug"] else INFO
    )

    logger = getLogger(__name__)

    logger.debug("Running in DEBUG mode")

    logger.debug("Dumping service account")
    # Store credentials in a file
    with open("./service.json", "w", encoding="utf-8") as service_file:
        json.dump(json.loads(conf["#service_account"]), service_file)

    # OAuth2 credential info
    key_file = "./service.json"

    logger.info("Proceeding with OAuth2 authentication")
    oauth2_client = oauth2.GoogleServiceAccountClient(
        key_file,
        oauth2.GetAPIScope('ad_manager')
    )

    if conf["list_network_codes"]:
        logger.warning(
            "Running in 'List Network Codes' mode, nothing will be downloaded.")
        list_network_codes(oauth2_client)
        sys.exit(0)

    ad_manager_client = ad_manager.AdManagerClient(
        oauth2_client,
        APPLICATION_NAME,
        network_code=conf["network_code"]
    )

    downloader = ad_manager_client.GetDataDownloader(version=API_VERSION)

    # test report job
    report_job = {
        "reportQuery": conf["report_job"]
    }

    if report_job["reportQuery"]["dateRangeType"] != "CUSTOM_DATE":
        if "startDate" in report_job["reportQuery"]:
            del report_job["reportQuery"]["startDate"]
        if "endDate" in report_job["reportQuery"]:
            del report_job["reportQuery"]["endDate"]
    else:
        datetime_from = datetime.strptime(
            report_job["reportQuery"]["startDate"], "%Y-%m-%d")
        datetime_to = datetime.strptime(
            report_job["reportQuery"]["endDate"], "%Y-%m-%d")
        report_job["reportQuery"]["startDate"] = {
            "year": datetime_from.year,
            "month": datetime_from.month,
            "day": datetime_from.day
        }
        report_job["reportQuery"]["endDate"] = {
            "year": datetime_to.year,
            "month": datetime_to.month,
            "day": datetime_to.day
        }

    logger.info("Waiting for job completion")
    job = downloader.WaitForReport(report_job)

    output_path = OUTPUT_DIRECTORY
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    logger.info("Job completed, downloading")

    output_filename = slugify(conf["report_name"])

    # download
    with open(
            os.path.join(
                output_path,
                "{}.csv".format(output_filename)
            ), "wb") as fid:
        downloader.DownloadReportToFile(
            job,
            "CSV",
            fid,
            use_gzip_compression=False,
            include_totals_row=False
        )

if __name__ == "__main__":
    main()
