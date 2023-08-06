
from auto_data_preprocessing.feature_engineering.base import *

df = pd.read_csv('https://s3.amazonaws.com/cloud.autogonai/insurance_claims.csv')

x_train, x_test, y_train, y_test, x, y, obj, report = data_fit(
    df,
    x_slice=None,
    y_slice=None,
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