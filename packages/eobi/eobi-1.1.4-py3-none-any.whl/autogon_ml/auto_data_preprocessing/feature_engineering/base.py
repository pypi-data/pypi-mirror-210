import pandas as pd
from dataprep.clean import clean_df
# # from AutoClean import AutoClean
# from autogon_ml.auto_data_preprocessing.AutoClean.autoclean import *
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    LabelEncoder,
    OneHotEncoder,
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
)
from sklearn.model_selection import train_test_split
import uuid
import os
import pickle
import numpy as np


def data_fit(
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
):
    """
    The goal of this function is to auto-feature engineer an tabular dataset applied to it and save the weight for transforrming new data
    Improvements:
    0. Clean code properly and add error handling
    1. Add more rules like remove columns with special character
    2. Handle outliers
    3. Convert data types or Fix datatypes issues
    4. Remove unnecessary columns
    5. Check for inconsistencies: Check for inconsistencies in the data, such as inconsistent date formats or inconsistent spelling of names.
    6. Handling text data: Text data can be cleaned by removing stop words, stemming, lemmatizing, and performing other techniques to remove noise and irrelevant information.
    """

    # Define the variables
    has_x = False  # check if x is defined
    has_y = False  # check if y is defined
    labelencoding_list = []  # define the labelencoding list object
    standard_scaler_weight = None  # Variable to hold standard scaler weight
    normalize_scaler_weight = None  # Variable to hold normalize scaler weight
    numerical_columns = []  # Variable to store scaled columns
    missingvalues_list = []  # define the missing value list object
    outlier_handlers = {}
    report = {}

    # Save the object to a pickle file
    # folder_uuid = str(uuid.uuid4())
    # # Create the folder if it doesn't exist
    # if not os.path.exists(folder_uuid):
    #     os.makedirs(folder_uuid)
    df = df.copy()

    for col in df.columns:
        if df[col].isnull().all():
            df.drop(col, axis=1, inplace=True)

    inferred_dtypes, cleaned_df = clean_df(df, report=False)
    print(f"x_slices: {x_slice}\ny_slices: {y_slice}")
    # Step 0: Feature Sampling
    if not x_slice and not y_slice:
        vf = cleaned_df.copy()
    else:
        if x_slice is not None:
            has_x = True
            x = cleaned_df.iloc[
                :, x_slice
            ]  # Replace 'target_variable' with the name of your target column
            x = pd.DataFrame(x)
        if y_slice is not None:
            has_y = True
            y = cleaned_df.iloc[
                :, y_slice
            ]  # Replace 'target_variable' with the name of your target column
            y = pd.DataFrame(y)
        if not has_x or not has_y:
            raise Exception("Provide both x and y slices")

    # Step 1: Extract seconds, minutes, hours, day of the week, month, or year as separate features from datetime columns
    if (has_x and has_y) == True:
        for column in x.columns:
            if (
                column in excluded_columns
                or x.columns.tolist().index(column) in excluded_columns
            ):
                continue
            if x[column].dtype == "datetime64[ns]":
                x[column + "_second"] = x[column].dt.second
                x[column + "_minute"] = x[column].dt.minute
                x[column + "_hour"] = x[column].dt.hour
                x[column + "_dayofweek"] = x[column].dt.dayofweek
                x[column + "_month"] = x[column].dt.month
                x[column + "_year"] = x[column].dt.year
                x = x.drop(columns=[column])
            elif x[column].dtype == "timedelta64[ns]":
                x[column + "_seconds"] = x[column].dt.seconds
                x = x.drop(columns=[column])

    else:
        for column in vf.columns:
            if (
                column in excluded_columns
                or vf.columns.tolist().index(column) in excluded_columns
            ):
                continue
            if vf[column].dtype == "datetime64[ns]":
                vf[column + "_second"] = vf[column].dt.second
                vf[column + "_minute"] = vf[column].dt.minute
                vf[column + "_hour"] = vf[column].dt.hour
                vf[column + "_dayofweek"] = vf[column].dt.dayofweek
                vf[column + "_month"] = vf[column].dt.month
                vf[column + "_year"] = vf[column].dt.year
                vf = vf.drop(columns=[column])
            elif vf[column].dtype == "timedelta64[ns]":
                vf[column + "_seconds"] = vf[column].dt.seconds
                vf = vf.drop(columns=[column])

    # Step 2: Remove missing data where datatype is text if available
    if (has_x and has_y) == True:
        for column in x.select_dtypes(include=["object"]):
            if (
                column in excluded_columns
                or x.columns.tolist().index(column) in excluded_columns
            ):
                continue
            missing_indices = (~x.notna()).any(axis=1)
            x = x.drop(x.index[missing_indices], axis=0)
            y = y.drop(y.index[missing_indices], axis=0)

    else:
        for column in vf.select_dtypes(include=["object"]):
            if (
                column in excluded_columns
                or vf.columns.tolist().index(column) in excluded_columns
            ):
                continue
            vf = vf.dropna(subset=[column])

    # Step 3: Handle numerical missing data using SimpleImputer with specified strategy
    if (has_x and has_y) == True:
        for index, column in enumerate(x.select_dtypes(include=np.number)):
            if (
                column in excluded_columns + excluded_fillmissing_columns
                or index in excluded_columns + excluded_fillmissing_columns
            ):
                continue
            missing_data_exists = x[column].isna().any()
            if missing_data_exists:
                imputer = SimpleImputer(strategy=strategy_value)
                x[column] = imputer.fit_transform(x[[column]])
                missingvalues_list.append(
                    {
                        "column_index": index,
                        "column_name": column,
                        "strategy_type": strategy_value,
                        "weight": pickle.dumps(imputer),
                        "dataset": "x",
                    }
                )
            else:
                pass
                # print("No missing data in column 'A'")

    else:
        for index, column in enumerate(vf.select_dtypes(include=np.number)):
            if (
                column in excluded_columns + excluded_fillmissing_columns
                or index in excluded_columns + excluded_fillmissing_columns
            ):
                continue
            missing_data_exists = vf[column].isna().any()
            # print(column, missing_data_exists)
            if missing_data_exists:
                imputer = SimpleImputer(strategy=strategy_value)
                vf[column] = imputer.fit_transform(vf[[column]])
                missingvalues_list.append(
                    {
                        "column_index": index,
                        "strategy_type": strategy_value,
                        "weight": pickle.dumps(imputer),
                        "dataset": "any",
                    }
                )
            else:
                pass

    # Step 4: Drop duplicate records
    if (has_x and has_y) == True:
        # drop duplicates in x and remove corresponding rows in Y
        duplicated_indices = x.duplicated()  # extract indices of duplicated rows
        x = x.drop_duplicates()  # drop duplicated rows in x
        y = y.drop(y.index[duplicated_indices], axis=0)  # drop corresponding rows in Y

    else:
        vf = vf.drop_duplicates()  # does not aply

    # Step 5: Apply label encoding to binary categorical columns and one-hot encoding to multiple categorical columns
    if (has_x and has_y) == True:
        for index, column in enumerate(y):
            if (
                column in excluded_columns + excluded_encoding_columns
                or index in excluded_columns + excluded_encoding_columns
            ):
                continue
            if (
                y[column].dtype == "object"
                and len(y[column].unique()) > 1
                and len(y[column].unique()) <= le_thresh
            ):
                # Binary column
                le = LabelEncoder()
                y[column] = le.fit_transform(y[column])
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "Le",
                        "weight": pickle.dumps(le),
                        "dataset": "y",
                    }
                )

            elif len(y[column].unique()) <= ohe_thresh:  # x[column].dtype == "object"
                # Multiple categories column
                ohe = OneHotEncoder(sparse=False)
                encoded = ohe.fit_transform(y[column].values.reshape(-1, 1))
                new_columns = []
                categories = ohe.categories_[0]
                # Attempt removing trailing zero from floats if present
                try:
                    categories = categories.astype("int")
                except:
                    pass
                # Save new columns and add them to the dataframe
                for i, category in enumerate(categories):
                    new_columns.append(column + "_" + str(category))
                    y[new_columns[-1]] = encoded[:, i]
                y = y.drop(columns=[column])
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "ohe",
                        "weight": pickle.dumps(ohe),
                        "new_columns": new_columns,
                        "dataset": "y",
                    }
                )

        for index, column in enumerate(x):
            if (
                column in excluded_columns + excluded_encoding_columns
                or index in excluded_columns + excluded_encoding_columns
            ):
                continue
            if (
                x[column].dtype == "object"
                and len(x[column].unique()) > 1
                and len(x[column].unique()) <= le_thresh
            ):
                # Binary column
                le = LabelEncoder()
                x[column] = le.fit_transform(x[column])
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "Le",
                        "weight": pickle.dumps(le),
                        "dataset": "x",
                    }
                )

            elif len(x[column].unique()) <= ohe_thresh:  # x[column].dtype == "object"
                # Multiple categories column
                ohe = OneHotEncoder(sparse=False)
                encoded = ohe.fit_transform(x[column].values.reshape(-1, 1))
                new_columns = []
                categories = ohe.categories_[0]
                # Attempt removing trailing zero from floats if present
                try:
                    categories = categories.astype("int")
                except:
                    pass
                # Save new columns and add them to the dataframe
                for i, category in enumerate(categories):
                    new_columns.append(column + "_" + str(category))
                    x[new_columns[-1]] = encoded[:, i]
                x = x.drop(columns=[column])
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "ohe",
                        "weight": pickle.dumps(ohe),
                        "new_columns": new_columns,
                        "dataset": "x",
                    }
                )

    else:
        for index, column in enumerate(vf):
            if (
                column in excluded_columns + excluded_encoding_columns
                or index in excluded_columns + excluded_encoding_columns
            ):
                continue
            if (
                vf[column].dtype == "object"
                and len(vf[column].unique()) > 1
                and len(vf[column].unique()) <= le_thresh
            ):
                # Binary column
                le = LabelEncoder()
                vf[column] = le.fit_transform(vf[column])
                # vf[column] = vf[column].astype(float)
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "Le",
                        "weight": pickle.dumps(le),
                        "dataset": "any",
                    }
                )

            elif len(vf[column].unique()) <= ohe_thresh:  # vf[column].dtype == "object"
                # Multiple categories column
                ohe = OneHotEncoder(sparse=False)
                encoded = ohe.fit_transform(vf[column].values.reshape(-1, 1))
                new_columns = []
                categories = ohe.categories_[0]
                # Attempt removing trailing zero from floats if present
                try:
                    categories = categories.astype("int")
                except:
                    pass
                # Save new columns and add them to the dataframe
                for i, category in enumerate(categories):
                    new_columns.append(column + "_" + str(category))
                    vf[new_columns[-1]] = encoded[:, i]
                vf = vf.drop(columns=[column])
                labelencoding_list.append(
                    {
                        "column_index": index,
                        "encoding_type": "ohe",
                        "weight": pickle.dumps(ohe),
                        "new_columns": new_columns,
                        "dataset": "any",
                    }
                )

    # Step 6: Split dataset into training and testing sets
    if has_x == True and has_y == True:
        if test_size_value > 0:
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=test_size_value, random_state=0
            )
        else:
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.1, random_state=0
            )
            x_train = x.copy()
            y_train = y.copy()

    else:
        if test_size_value > 0:
            v_train, v_test = train_test_split(
                vf, test_size=test_size_value, random_state=0
            )
        else:
            v_train, v_test = train_test_split(vf, test_size=0.1, random_state=0)
            v_train = vf.copy()

    # Step 7: Scale numerical features using StandardScaler
    if standard_scaler == True and (has_x and has_y) == True:
        # Scale x
        scaler = StandardScaler()
        numerical_columns = x_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            x
            for x in numerical_columns
            if x not in excluded_columns + excluded_scaling_columns
        ]
        x_train[numerical_columns] = scaler.fit_transform(x_train[numerical_columns])
        x_test[numerical_columns] = scaler.transform(x_test[numerical_columns])
        standard_scaler_weight = scaler

        # Scale y
        scaler = StandardScaler()
        numerical_columns = y_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            y
            for y in numerical_columns
            if y not in excluded_columns + excluded_scaling_columns
        ]
        y_train[numerical_columns] = scaler.fit_transform(y_train[numerical_columns])
        y_test[numerical_columns] = scaler.transform(y_test[numerical_columns])
        standard_scaler_weight = scaler

    elif standard_scaler == True and (has_x and has_y) == False:
        scaler = StandardScaler()
        numerical_columns = v_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            x
            for x in numerical_columns
            if x not in excluded_columns + excluded_scaling_columns
        ]
        v_train[numerical_columns] = scaler.fit_transform(v_train[numerical_columns])
        v_test[numerical_columns] = scaler.transform(v_test[numerical_columns])
        standard_scaler_weight = scaler

    if normal_scaler == True and (has_x and has_y) == True:
        # Scale x
        scaler = MinMaxScaler()
        numerical_columns = x_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            x
            for x in numerical_columns
            if x not in excluded_columns + excluded_scaling_columns
        ]
        x_train[numerical_columns] = scaler.fit_transform(x_train[numerical_columns])
        x_test[numerical_columns] = scaler.transform(x_test[numerical_columns])
        normalize_scaler_weight = scaler
        # Scale y
        scaler = MinMaxScaler()
        numerical_columns = y_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            y
            for y in numerical_columns
            if y not in excluded_columns + excluded_scaling_columns
        ]
        y_train[numerical_columns] = scaler.fit_transform(y_train[numerical_columns])
        y_test[numerical_columns] = scaler.transform(y_test[numerical_columns])
        normalize_scaler_weight = scaler

    elif normal_scaler == True and (has_x and has_y) == False:
        scaler = MinMaxScaler()
        numerical_columns = v_train.select_dtypes(include=np.number).columns.tolist()
        numerical_columns = [
            x
            for x in numerical_columns
            if x not in excluded_columns + excluded_scaling_columns
        ]
        v_train[numerical_columns] = scaler.fit_transform(v_train[numerical_columns])
        v_test[numerical_columns] = scaler.transform(v_test[numerical_columns])
        normalize_scaler_weight = scaler

    # Step 8 Extract the object to be saved and save it
    # Create a dictionary object to hold the variables
    obj = {
        "labelencoding_list": labelencoding_list,
        "standard_scaler_weight": {
            "status": standard_scaler,
            "object": pickle.dumps(standard_scaler_weight),
            "columns": numerical_columns,
        },
        "normalize_scaler_weight": {
            "status": normal_scaler,
            "object": pickle.dumps(normalize_scaler_weight),
            "columns": numerical_columns,
        },
        "missingvalues_list": missingvalues_list,
        "outlier_handlers": outlier_handlers,
        "excluded_columns": excluded_columns,
    }

    # file_uuid = uuid.uuid4()
    # weight_file_name = str(file_uuid) + ".weights"
    # with open(
    #     weight_file_name, "wb"
    # ) as f:  # After saving, zip folder content and save to s3
    #     pickle.dump(obj, f)

    # Step 9: Return the preprocessed DataFrame and split datasets and pkl file
    if (has_x and has_y) == True:
        return (
            clean_df(x_train, data_type_detection="none", report=False),
            clean_df(x_test, data_type_detection="none", report=False),
            clean_df(y_train, data_type_detection="none", report=False),
            clean_df(y_test, data_type_detection="none", report=False),
            clean_df(x, data_type_detection="none", report=False),
            clean_df(y, data_type_detection="none", report=False),
            obj,
            report,
        )

    else:
        return (
            clean_df(v_train, data_type_detection="none", report=False),
            clean_df(v_test, data_type_detection="none", report=False),
            [],
            [],
            clean_df(vf, data_type_detection="none", report=False),
            [],
            obj,
            report,
        )


def data_transform(array, obj, dataset_type="x", clean=False):
    """
    Step 1: load the saved weight
    Step 2: Handle date variable
    Step 3: Handle all encoded columns using the encoded weights [fix items for LE saving diff from OHE saving]
    Step 4: Handle numerical missing data using SimpleImputer value
    Step 5: Scale numerical features using loaded scaler
    """

    # Step 1: load the saved weight
    # with open(weight_file_name, "rb") as f:
    # obj = pickle.load(f)

    # print(obj)
    # dtypes, array = clean_df(array, report=False)

    labelencoding_list = obj["labelencoding_list"]
    standard_scaler_weight = obj["standard_scaler_weight"]
    normalize_scaler_weight = obj["normalize_scaler_weight"]
    missingvalues_list = obj["missingvalues_list"]
    excluded_columns = obj["excluded_columns"]
    # outlier_handlers = obj["outlier_handlers"]

    inferred_dtypes, array = clean_df(array, report=False)

    # Step 2: Handle date variable
    for column in array.columns:
        if (
            column in excluded_columns
            or array.columns.tolist().index(column) in excluded_columns
        ):
            continue
        if array[column].dtype == "datetime64[ns]":
            array[column + "_second"] = array[column].dt.second
            array[column + "_minute"] = array[column].dt.minute
            array[column + "_hour"] = array[column].dt.hour
            array[column + "_dayofweek"] = array[column].dt.dayofweek
            array[column + "_month"] = array[column].dt.month
            array[column + "_year"] = array[column].dt.year
            array = array.drop(columns=[column])
        elif array[column].dtype == "timedelta64[ns]":
            array[column + "_seconds"] = array[column].dt.seconds
            array = array.drop(columns=[column])
    # print(array)

    # Step 3: Drop duplicates if cleaning
    if clean:
        array = array.drop_duplicates()
        for column in array.select_dtypes(include=["object"]):
            if (
                column in excluded_columns
                or array.columns.tolist().index(column) in excluded_columns
            ):
                continue
            array = array.dropna(subset=[column])

    # Step 4: Handle numerical missing data using SimpleImputer value
    for imputer in missingvalues_list:
        column_index = imputer["column_index"]
        missing_strategy = imputer["strategy_type"]
        weight = pickle.loads(imputer["weight"])
        dataset = imputer["dataset"]
        if dataset in [dataset_type, "any"]:
            # with open(weight_link, "rb") as f:
            #     weight = pickle.load(f)

            imputer_obj = SimpleImputer(strategy="constant", fill_value=weight)
            temp = array.iloc[:, column_index]

            temp = imputer_obj.fit_transform(temp.values.reshape(-1, 1))
            columns = array.columns
            array = np.array(array)
            array[:, column_index] = temp.ravel()
            array = pd.DataFrame(array, columns=columns)

    # Step 3: Handle all encoded columns using the encoded weights [fix items for LE saving diff from OHE saving]
    # drops = []
    for index, column in enumerate(array):
        for labelencoder in labelencoding_list:
            column_index = labelencoder["column_index"]
            dataset = labelencoder["dataset"]
            weight = pickle.loads(labelencoder["weight"])
            new_columns = labelencoder.get("new_columns")

            if index == column_index:  # map generated column to current column
                printout = dict(labelencoder).copy()
                printout.pop("weight")
                # print(index, column, printout, "*" * 50)
                if dataset in [dataset_type, "any"]:
                    # print("************* I got here **********")
                    # print(labelencoder["encoding_type"])
                    # with open(weightfile, "rb") as f:
                    #     weight = pickle.load(f)

                    temp = array.iloc[:, index]

                    temp_array = temp.values.reshape(-1, 1)
                    temp = weight.transform(temp_array)

                    if new_columns:
                        array.rename(columns={column: "drop"}, inplace=True)
                        array = pd.concat(
                            [array, pd.DataFrame(temp, columns=new_columns)], axis=1
                        )
                    else:
                        if temp.ndim == 1:
                            array[column] = temp
                        else:
                            array.rename(columns={column: "drop"}, inplace=True)
                            array = pd.concat([array, pd.DataFrame(temp)], axis=1)
                    # drops.append(column_index)

                # elif dataset == "y":
                #     array = weight.transform(array[column])
    if "drop" in array.columns:
        array = array.drop(["drop"], axis=1)

    # Step 5: Scale numerical features using loaded scaler
    # 'normalize_scaler_weight': {'status': False, 'object': 'fede509d-0bfd-4929-91ae-7e6ed988a631.pkl'}
    # 'standard_scaler_weight': {'status': True, 'object': '6776afa2-2031-4ffe-92b9-ff3bb9416c90.pkl'}

    if normalize_scaler_weight["status"] == True:
        columns = normalize_scaler_weight["columns"]
        # with open(normalize_scaler_weight["object"], "rb") as f:
        #     weight = pickle.load(f)
        weight = pickle.loads(normalize_scaler_weight["object"])

        # columns = array.columns
        array[columns] = weight.transform(array[columns])
        # array = pd.DataFrame(array, columns=columns)

    if standard_scaler_weight["status"] == True:
        columns = standard_scaler_weight["columns"]
        # with open(standard_scaler_weight["object"], "rb") as f:
        #     scaler = pickle.load(f)
        scaler = pickle.loads(standard_scaler_weight["object"])

        # columns = array.columns
        array[columns] = scaler.transform(array[columns])
        # array = pd.DataFrame(array, columns=columns)

    return clean_df(array, data_type_detection="none", report=False)
