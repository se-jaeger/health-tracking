import pandas as pd
import seaborn as sns

from . import AppleHealthParser, constants


class Workouts(object):
    """
    Parse and gives access to ``Workout`` data of a Apple Health App dump data.
    Provides plotting functionalities.

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

        def create_offset_column(row: pd.DataFrame) -> None:
            """
            Helper for creating offset column since the first training

            Args:
                row (pd.DataFrame): Workouts ``pd.DataFrame``
            """
            first_workout = row[constants.WORKOUT_COLUMN_DATE][0]
            row[constants.WORKOUT_COLUMN_OFFSET] = row.apply(lambda row: (row[constants.WORKOUT_COLUMN_DATE] - first_workout).days, axis=1)

        self._parser = AppleHealthParser(zip_dump_path, unzip_path, force_unzip)
        self.workouts, self.workout_types = self._parser.extract_workouts()
        self._valid_data_frames = [*[f"{workout_type}s" for workout_type in self.workout_types], "workouts"]

        # new column with the offset in days since the first workout
        create_offset_column(self.workouts)

        # create data frames for each workout type
        for workout_type in self.workout_types:
            type_df = self.workouts[self.workouts[constants.WORKOUT_TYPE] == workout_type].copy().reset_index(drop=True)
            type_df[constants.WORKOUT_COLUMN_MINUTES_PER_KM] = type_df.apply(calc_minutes_per_km, axis=1)

            # new column with the offset in days since the first workout of ``workout_type``
            create_offset_column(type_df)

            self.__setattr__(f"{workout_type.lower()}s", type_df)

    def __getitem__(self, workout_type: str) -> pd.DataFrame:
        """
        Get the ``DataFrame``s with the help of subscriptions.

        Args:
            workout_type (str): One of the existing ``workout_types`` or ``workouts`` for the whole data

        Raises:
            ValueError: If a incorrect ``workout_type`` is give

        Returns:
            pd.DataFrame: The ``DataFrame`` of type ``workout_type``
        """
        if workout_type not in self._valid_data_frames:
            raise ValueError(f"'workout_type' need to be one of: {self._valid_data_frames}\n\tGiven: {workout_type}")

        return self.__getattribute__(workout_type)

    def plot(
        self,
        x: str,
        y: str,
        plot_type: str,
        workout_type: str = "runnings",
        outlier: (int, int) = None,
        z: str = None,
        kind: str = "reg",
        xlim: (int, int) = 0.01,
        show_new_years: bool = True,
        legend: str = "brief"
    ):

        # check x, y, z parameter
        if x not in constants.WORKOUT_PLOTTING_CLOUMN or \
            y not in constants.WORKOUT_PLOTTING_CLOUMN or \
                (z is not None and z not in constants.WORKOUT_PLOTTING_CLOUMN):

            raise ValueError(
                f"Parameter 'x', 'y', and 'z' must be one of: {constants.WORKOUT_PLOTTING_CLOUMN}\n\tGiven: \tx: {x}\n\t\tx: {y}\n\t\tx: {z}"
            )

        # check workout_type parameter
        if workout_type in self._valid_data_frames:
            data = self.__getitem__(workout_type)

        else:
            raise ValueError(f"Parameter 'workout_type' must be one of: {self._valid_data_frames}\n\tGiven: {workout_type}")

        # check outlier parameter
        if outlier is not None:
            data = data[
                (data[y] <= outlier[1]) &
                (data[y] >= outlier[0])
            ]

            if data.empty:
                raise ValueError(f"Choose 'outlier' such that the resulting plotting data is not empty!\n\tGiven: {outlier}")

        # check xlim parameter
        if xlim is None:
            x_limits = (data[x].min(), data[x].max())

        elif type(xlim) == tuple:
            x_limits = xlim

        # ``xlim`` is interpreted as percentage value
        # subtract/add this percentage of data range to create
        elif type(xlim) == float and xlim < 1:
            upper = data[x].max()
            lower = data[x].min()
            x_range = upper - lower
            x_limits = (lower - xlim * x_range, upper + xlim * x_range)

        else:
            raise ValueError(f"Value of 'xlim' is invalid!\n\tGiven: {xlim}")

        # Plot or raise Exception
        if plot_type in ["joint", "jointplot", "joint_plot", "joint-plot", "joint plot"]:

            return sns.jointplot(x, y, data=data, kind=kind, xlim=x_limits)

        elif plot_type in ["scatter", "scatterplot", "scatter_plot", "scatter-plot", "scatter plot"]:

            scatter_plot = sns.scatterplot(x, y, data=data, hue=z, legend=legend)

            # FIXME: does not plot vlines
            if show_new_years:
                for new_year_offset in get_new_years_offsets(data):
                    scatter_plot.axvline(new_year_offset, data[y].min(), data[y].max())

            return scatter_plot

        else:
            raise ValueError(f"Parameter 'plot_type' is invalid!\n\tGiven: {plot_type}")


def calc_minutes_per_km(row: pd.DataFrame) -> pd.Series:
    """
    Helper function that calculates the pace as minutes per kilometer.
    Apply via: ``data_frame.applyc(alc_minutes_per_km, axis=1)``.

    Args:
        row (pd.DataFrame): Row of workouts ``pd.DataFrame`` as ``pd.Series``

    Returns:
        pd.Series: New column for workflow ``DataFrame``
    """
    result = 0

    # Calculation or downstream computations will fail if one of the operands is 0
    # would result in division by 0 or inf as result
    error_state = row[constants.WORKOUT_COLUMN_DURATION] == 0 or row[constants.WORKOUT_COLUMN_DISTANCE] == 0

    if not error_state:
        result = row[constants.WORKOUT_COLUMN_DURATION] / row[constants.WORKOUT_COLUMN_DISTANCE]

    return result


def get_new_years_offsets(workout_data_frame: pd.DataFrame) -> list:
    """
    Helper function that computes the offsets for new years since the first workout, in days.

    Args:
        workout_data_frame (pd.DataFrame): Workouts ``pd.DataFrame``

    Returns:
        list: elements are the offsets for new years in days
    """

    first_workout = workout_data_frame[constants.WORKOUT_COLUMN_DATE][0]
    last_workout = workout_data_frame[constants.WORKOUT_COLUMN_DATE][workout_data_frame.shape[0] - 1]

    new_years = last_workout.year - first_workout.year
    new_year_offsets = []

    for i in range(new_years):
        new_year_offset = pd.Timestamp(f"1.1.{first_workout.year + i + 1}", tz=first_workout.tz) - first_workout
        new_year_offsets.append(new_year_offset.days)

    return new_year_offsets
