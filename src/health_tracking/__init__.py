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


import re
import os
import io
import shutil
import zipfile

import pandas as pd
import xml.etree.ElementTree as ET

from . import constants


class Singleton(type):
    """
    Is used as `metaclass` to achieve a singleton pattern.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppleHealthParser(metaclass=Singleton):
    """
    Parse and gives access to Apple Health App dump data.

    Args:
        zip_dump_path (str, optional): Path to the zipped data dump. Defaults to constants.ZIP_PATH.
        unzip_path (str, optional): Path to the unzipped data dump. Defaults to constants.UNZIP_PATH.
        force_unzip (bool, optional): Flag to force unzipping the data again. Can be useful for new data. Defaults to False.
    """

    def __init__(
        self,
        zip_dump_path: str = constants.ZIP_PATH,
        unzip_path: str = constants.UNZIP_PATH,
        force_unzip: bool = False
    ) -> None:

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

        self._tree = ET.parse(constants.XML_PATH)
        self._health_data = self._tree.getroot()

        # element types
        self._export_date = None
        self._me = None
        self._workouts = None
        self._workout_types = None
        self._activity_summaries = None
        self._records = None
        self._correlations = None
        self._clinical_records = None

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

    def _extract_elements_of_type(self, element_type: str) -> pd.DataFrame:
        """
        Returns a ``DataFrame`` with the elements of ``element_type``. Do not use by your own!

        Args:
            element_type (str): Need to fit one of ``constants.ELEMENT_TAGS``

        Raises:
            ValueError: If wrong ``element_type`` is given

        Returns:
            pd.DataFrame: of given ``element_type`` or ``None`` if empty
        """

        if element_type not in constants.ELEMENT_TAGS:
            raise ValueError(f"'element_type' need to be one of: {constants.ELEMENT_TAGS}")

        elements = self._tree.findall(element_type)
        result = pd.DataFrame([element.attrib for element in elements])

        result = self._fix_data_types(result)

        return None if result.empty else result

    def extract_workouts(self) -> (pd.DataFrame, set):
        """
        Returns ``Workout`` elements and ``set`` of all workout existing types. Shortens the workout types.

        Returns:
            (pd.DataFrame, set): of type ``Workout`` or ``None`` if empty and set of available workout types
        """

        # increase performace by do not parse again.
        if self._workouts is None and self._workout_types is None:

            self._workouts = self._extract_elements_of_type(constants.WORKOUT_TAG)
            self._workouts[constants.WORKOUT_TYPE] = self._workouts.apply(
                lambda row: re.match(constants.WORKOUT_REGEX, row[constants.WORKOUT_TYPE]).group(1).lower(),
                axis=1
            )
            self._workout_types = set(self._workouts[constants.WORKOUT_TYPE])

        return self._workouts, self._workout_types

    def extract_me(self) -> pd.DataFrame:
        """
        Returns ``Me`` elements.

        Returns:
            pd.DataFrame: of type ``Me`` or ``None`` if empty
        """

        # increase performace by do not parse again.
        if self._me is None:
            self._me = self._extract_elements_of_type(constants.ME_TAG)

        return self._me

    def extract_records(self) -> pd.DataFrame:
        """
        Returns ``Record`` elements.

        Returns:
            pd.DataFrame: of type ``Record`` or ``None`` if empty
        """

        # increase performace by do not parse again.
        if self._records is None:
            self._records = self._extract_elements_of_type(constants.RECORD_TAG)

        return self._records

    def extract_correlations(self) -> pd.DataFrame:
        """
        Returns ``Correlation`` elements.

        Returns:
            pd.DataFrame: of type ``Correlation`` or ``None`` if empty
        """

        # increase performace by do not parse again.
        if self._correlations is None:
            self._correlations = self._extract_elements_of_type(constants.CORRELATION_TAG)

        return self._correlations

    def extract_activity_summaries(self) -> pd.DataFrame:
        """
        Returns ``ActivitySummary`` elements.

        Returns:
            pd.DataFrame: of type ``ActivitySummary`` or ``None`` if empty
        """

        # increase performace by do not parse again.
        if self._activity_summaries is None:
            self._activity_summaries = self._extract_elements_of_type(constants.ACTIVITY_SUMMARY_TAG)

        return self._activity_summaries

    def extract_clinical_records(self) -> pd.DataFrame:
        """
        Returns ``ClinicalRecord`` elements.

        Returns:
            pd.DataFrame: of type ``ClinicalRecord`` or ``None`` if empty
        """

        # increase performace by do not parse again.
        if self._clinical_records is None:
            self._clinical_records = self._extract_elements_of_type(constants.CLINICAL_RECORD_TAG)

        return self._clinical_records

    def get_export_date(self) -> pd.Timestamp:
        """
        Returns the ``pd.Timestamp`` of exporting.

        Returns:
            pd.Timestamp: Export timestamp
        """

        # increase performace by do not parse again.
        if self._export_date is None:
            data_frame = self._extract_elements_of_type(constants.EXPORT_DATE_TAG)
            self._export_date = pd.to_datetime(data_frame["value"])[0]

        return self._export_date
