
from auto_data_preprocessing.feature_engineering.base import *
from auto_data_preprocessing.feature_engineering.util import *

# df = pd.read_csv('https://firebasestorage.googleapis.com/v0/b/sendbucs-1535561019038.appspot.com/o/Data.csv?alt=media&token=2593af94-3541-43e7-90ec-13ca21c45773')

df = pd.read_csv('https://s3.amazonaws.com/cloud.autogonai/insurance_claims.csv')

x_train, x_test, y_train, y_test, x, y, obj, report = data_fit(
    df,
    x_slice=boundaries_to_indices(":-1", df),
    y_slice=boundaries_to_indices("-2", df),
    strategy_value="most_frequent",
    standard_scaler=False,
    normal_scaler=False,
    test_size_value=0.0,
    le_thresh=2,
    ohe_thresh=10,
    outlier_mode="auto",
    outlier_multiplier=1.5,
    excluded_columns=[],
    excluded_fillmissing_columns=[],
    excluded_encoding_columns=[],
    excluded_scaling_columns=[],
)

print(x)

print(x_train)