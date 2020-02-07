import os

# File paths

EXPORT_NAME = "export.zip"
EXPORT_DIR_NAME = "apple_health_export"
XML_NAME = "export.xml"

ZIP_PATH = os.path.join("../data/raw", EXPORT_NAME)
UNZIP_PATH = os.path.join("../data/interim", EXPORT_DIR_NAME)
XML_PATH = os.path.join(UNZIP_PATH, XML_NAME)


# XML structure

EXPORT_DATE_TAG = "ExportDate"
ME_TAG = "Me"
RECORD_TAG = "Record"
WORKOUT_TAG = "Workout"
CORRELATION_TAG = "Correlation"
ACTIVITY_SUMMARY_TAG = "ActivitySummary"
CLINICAL_RECORD_TAG = "ClinicalRecord"


ELEMENT_TAGS = {
    EXPORT_DATE_TAG,
    ME_TAG,
    RECORD_TAG,
    WORKOUT_TAG,
    CORRELATION_TAG,
    ACTIVITY_SUMMARY_TAG,
    CLINICAL_RECORD_TAG
}

# Workout Element

WORKOUT_TYPE = "workoutActivityType"
WORKOUT_COLUMN_OFFSET = "dayOffset"
WORKOUT_COLUMN_DATE = "creationDate"
WORKOUT_COLUMN_DISTANCE = "totalDistance"
WORKOUT_COLUMN_DURATION = "duration"
WORKOUT_COLUMN_MINUTES_PER_KM = "minutesPerKm"
WORKOUT_CLOUM_TOTAL_ENERGY = "totalEnergyBurned"

WORKOUT_PLOTTING_CLOUMN = {
    WORKOUT_COLUMN_OFFSET,
    WORKOUT_COLUMN_DISTANCE,
    WORKOUT_COLUMN_DURATION,
    WORKOUT_COLUMN_MINUTES_PER_KM,
    WORKOUT_CLOUM_TOTAL_ENERGY
}


# RegEx strings

WORKOUT_REGEX = r"^HKWorkoutActivityType(.+)$"
