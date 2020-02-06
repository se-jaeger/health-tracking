# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'health-tracking'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound


##########################################


import os
import io
import shutil
import zipfile

import pandas as pd
import xml.etree.ElementTree as ET

from . import constants


class AppleHealthParser(object):

    def __init__(
        self,
        zip_dump_path: str = constants.ZIP_PATH,
        unzip_path: str = constants.UNZIP_PATH,
        force_unzip: bool = False
    ) -> None:
        """
        Parse and gives access to Apple Health App dump data.

        Args:
            zip_dump_path (str, optional): Path to the zipped data dump. Defaults to constants.ZIP_PATH.
            unzip_path (str, optional): Path to the unzipped data dump. Defaults to constants.UNZIP_PATH.
            force_unzip (bool, optional): Flag to force unzipping the data again. Can be useful for new data. Defaults to False.
        """

        # give information about may changing Version
        print("AppleHealthParser is tested for HealthKit Export Version: 11")

        # handle some cases
        if force_unzip:
            shutil.rmtree(unzip_path)

        if not os.path.exists(unzip_path):
            with open(zip_dump_path, "rb") as file:
                zip_file_bytes = io.BytesIO(file.read())
                zipped_export = zipfile.ZipFile(zip_file_bytes)
                zipped_export.extractall(os.path.split(unzip_path)[0])  # need path to dir not file

        self.tree = ET.parse(constants.XML_PATH)
        self.health_data = self.tree.getroot()

    def _fix_data_types(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """
        Fix the data types of a extracted ``DataFrame``.

        Args:
            data_frame (pd.DataFrame): Extracted ``DataFrame``

        Returns:
            pd.DataFrame: ``DataFrame`` with fixed data types
        """

        result = data_frame.apply(pd.to_numeric, errors='ignore')

        for column in result.columns:
            if "date" in column.lower():
                try:
                    result[column] = pd.to_datetime(result[column])
                except:

                    # just catch to keep code running
                    pass

        return result

    def extract_elements_of_type(self, element_type: str) -> pd.DataFrame:
        """
        Returns a ``DataFrame`` with the elements of ``element_type``.

        Args:
            element_type (str): Need to fit one of ``constants.ELEMENT_TAGS``

        Raises:
            ValueError: If wrong ``element_type`` is given

        Returns:
            pd.DataFrame: of given ``element_type`` or `None` if empty
        """

        if element_type not in constants.ELEMENT_TAGS:
            raise ValueError(f"'element_type' need to be one of: {constants.ELEMENT_TAGS}")

        elements = self.tree.findall(element_type)
        result = pd.DataFrame([element.attrib for element in elements])

        result = self._fix_data_types(result)

        return None if result.empty else result

    #### for convenience
    def extract_workouts(self) -> pd.DataFrame:
        """
        For convenience. Returns `Workout` Elements.

        Returns:
            pd.DataFrame: of type `Workout` or `None` if empty
        """
        return self.extract_elements_of_type(constants.WORKOUT_TAG)

    def extract_me(self) -> pd.DataFrame:
        """
        For convenience. Returns `Me` Elements.

        Returns:
            pd.DataFrame: of type `Me` or `None` if empty
        """
        return self.extract_elements_of_type(constants.ME_TAG)

    def extract_records(self) -> pd.DataFrame:
        """
        For convenience. Returns `Record` Elements.

        Returns:
            pd.DataFrame: of type `Record` or `None` if empty
        """
        return self.extract_elements_of_type(constants.RECORD_TAG)

    def extract_correlations(self) -> pd.DataFrame:
        """
        For convenience. Returns `Correlation` Elements.

        Returns:
            pd.DataFrame: of type `Correlation` or `None` if empty
        """
        return self.extract_elements_of_type(constants.CORRELATION_TAG)

    def extract_activity_summaries(self) -> pd.DataFrame:
        """
        For convenience. Returns `ActivitySummary` Elements.

        Returns:
            pd.DataFrame: of type `ActivitySummary` or `None` if empty
        """
        return self.extract_elements_of_type(constants.ACTIVITY_SUMMARY_TAG)

    def extract_clinical_records(self) -> pd.DataFrame:
        """
        For convenience. Returns `ClinicalRecord` Elements.

        Returns:
            pd.DataFrame: of type `ClinicalRecord` or `None` if empty
        """
        return self.extract_elements_of_type(constants.CLINICAL_RECORD_TAG)

    def get_export_date(self) -> pd.Timestamp:
        """
        For convenience. Returns the ``pd.Timestamp`` of exporting.

        Returns:
            pd.Timestamp: Export timestamp
        """
        data_frame = self.extract_elements_of_type(constants.EXPORT_DATE_TAG)
        return pd.to_datetime(data_frame["value"])[0]
