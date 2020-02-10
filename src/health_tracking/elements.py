import pandas as pd

from . import AppleHealthParser, constants


class Elements(object):
    """
    Parent class for parse and hold the ``Elements`` in the Apple Health App dump data.

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

        self._parser = AppleHealthParser(zip_dump_path, unzip_path, force_unzip)

    def __getitem__(self, type: str) -> pd.DataFrame:
        """
        Get the ``DataFrame``s with the help of subscriptions.

        Args:
            type (str): One of the existing types or name of the element type for the whole data

        Raises:
            ValueError: If a incorrect ``type`` is give

        Returns:
            pd.DataFrame: The ``DataFrame`` of ``type``
        """
        raise NotImplementedError

    def column(self):
        """
        Returns column dames of ``DataFrame`` as list.

        Returns:
            list: All column names
        """
        raise NotImplementedError

    def update(self):
        """
        Triggers the reparsing of the Apple Health App dump data.
        """
        raise NotImplementedError
