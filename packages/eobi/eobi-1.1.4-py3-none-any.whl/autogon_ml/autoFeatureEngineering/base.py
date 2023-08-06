import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import uuid
import os
import pickle
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import autosklearn.classification

def saveOBjtoFile(obj, folder_uuid):
    # Save the object to a pickle file
    weight_file_name = str(uuid.uuid4()) + ".pkl"

    file_path = os.path.join(folder_uuid, weight_file_name)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)
    return file_path



def auto_preprocess_data_fit(df, data_slice_x=None, data_slice_y=None, strategy_value='mean', standard_scalar=False,
                             normal_scalar=False, test_size_value=0.25):
    '''
    The goal of this function is to auto-feature engineer an tabular dataset applied to it and save the weight for transforrming new data
    Improvements:
    0. Clean code properly and add error handling
    1. Add more rules like remove columns with special character
    2. Handle outliers
    3. Convert data types or Fix datatypes issues
    4. Remove unnecessary columns
    5. Check for inconsistencies: Check for inconsistencies in the data, such as inconsistent date formats or inconsistent spelling of names.
    6. Handling text data: Text data can be cleaned by removing stop words, stemming, lemmatizing, and performing other techniques to remove noise and irrelevant information.
    '''

    # Define the variables
    has_x = False  # check if x is defined
    has_y = False  # check if y is defined
    labelencoding_list = []  # define the labelencoding list object
    standard_scalar_weight = None  # Variable to hold standard scalar weight
    normalize_scalar_weight = None  # Variable to hold normalize scalar weight
    missingvalues_list = []  # define the missing value list object

    # Save the object to a pickle file
    folder_uuid = str(uuid.uuid4())
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_uuid):
        os.makedirs(folder_uuid)

    # Step 0: Feature Sampling
    if data_slice_x is not None:
        has_x = True
        X = df.iloc[data_slice_x]  # Replace 'target_variable' with the name of your target column
    if data_slice_y is not None:
        has_y = True
        y = df.iloc[data_slice_y]  # Replace 'target_variable' with the name of your target column

    # Step 1: Extract day of the week, month, or year as separate features from date columns
    if (has_x and has_y) == True:

        for column in X.columns:
            if X[column].dtype == 'datetime64[ns]':
                X[column + '_dayofweek'] = X[column].dt.dayofweek
                X[column + '_month'] = X[column].dt.month
                X[column + '_year'] = X[column].dt.year
                X = X.drop(columns=[column])

    if (has_x and has_y) == False:
        vf = X if has_x == True else y
        for column in vf.columns:
            if vf[column].dtype == 'datetime64[ns]':
                vf[column + '_dayofweek'] = vf[column].dt.dayofweek
                vf[column + '_month'] = vf[column].dt.month
                vf[column + '_year'] = vf[column].dt.year
                vf = vf.drop(columns=[column])

    # Step 2: Apply label encoding to binary categorical columns and one-hot encoding to multiple categorical columns

    if (has_x and has_y) == True:

        if y.dtype == 'object' and len(y.unique()) > 1:
            # Binary column
            le = LabelEncoder()
            y = pd.Series(le.fit_transform(y))
            labelencoding_list.append({
                "column_index": 0,
                "encoding_type": "Le",
                "weight": saveOBjtoFile(le,folder_uuid),
                "dataset": "y"
            })

        for index, column in enumerate(X.select_dtypes(include=['object'])):
            if len(X[column].unique()) == 2:
                # Binary column
                le = LabelEncoder()
                X[column] = le.fit_transform(X[column])
                labelencoding_list.append({
                    "column_index": index,
                    "encoding_type": "Le",
                    "weight": saveOBjtoFile(le,folder_uuid),
                    "dataset": "X"
                })

            else:
                # Multiple categories column
                ohe = OneHotEncoder(sparse=False)
                encoded = ohe.fit_transform(X[column].values.reshape(-1, 1))
                for i, category in enumerate(ohe.categories_[0]):
                    X[column + '_' + category] = encoded[:, i]
                X = X.drop(columns=[column])
                labelencoding_list.append({
                    "column_index": index,
                    "encoding_type": "ohe",
                    "weight": saveOBjtoFile(ohe,folder_uuid),
                    "dataset": "X"
                })

    if (has_x and has_y) == False:
        for index, column in enumerate(vf.select_dtypes(include=['object'])):
            if len(vf[column].unique()) == 2:
                # Binary column
                le = LabelEncoder()
                vf[column] = le.fit_transform(vf[column])
                labelencoding_list.append({
                    "column_index": index,
                    "encoding_type": "Le",
                    "weight": saveOBjtoFile(ohe,folder_uuid),
                    "dataset": "any"
                })

            else:
                # Multiple categories column
                ohe = OneHotEncoder(sparse=False)
                encoded = ohe.fit_transform(vf[column].values.reshape(-1, 1))
                for i, category in enumerate(ohe.categories_[0]):
                    vf[column + '_' + category] = encoded[:, i]
                vf = vf.drop(columns=[column])
                labelencoding_list.append({
                    "column_index": index,
                    "encoding_type": "ohe",
                    "weight": saveOBjtoFile(ohe,folder_uuid),
                    "dataset": "any"
                })

    # Step 3: Drop duplicate records
    if (has_x and has_y) == True:
        # drop duplicates in X and remove corresponding rows in Y
        duplicated_indices = X.duplicated()  # extract indices of duplicated rows
        X = X.drop_duplicates()  # drop duplicated rows in X
        y = y.drop(y.index[duplicated_indices], axis=0)  # drop corresponding rows in Y

    if (has_x and has_y) == False:
        vf = vf.drop_duplicates()  # does not aply

    # Step 4: Remove missing data where datatype is text if available
    if (has_x and has_y) == True:
        for column in X.select_dtypes(include=['object']):
            duplicated_indices = X.dropna(subset=[column]).duplicated()
            X = X.dropna(subset=[column])
            y = y.drop(y.index[duplicated_indices], axis=0)

    if (has_x and has_y) == False:
        for column in X.select_dtypes(include=['object']):
            vf = vf.dropna(subset=[column])

    # Step 5: Handle numerical missing data using SimpleImputer with specified strategy
    if (has_x and has_y) == True:
        for index, column in enumerate(X.select_dtypes(include=['float64'])):
            missing_data_exists = X[column].isna().any()
            if missing_data_exists:
                imputer = SimpleImputer(strategy=strategy_value)
                X[column] = imputer.fit_transform(X[[column]])
                missingvalues_list.append({
                    "column_index": index,
                    "column_name": column,
                    "strategy_tyoe": strategy_value,
                    "weight": saveOBjtoFile(imputer,folder_uuid),
                    "dataset": "X"
                })
            else:
                pass
                # print("No missing data in column 'A'")

    if (has_x and has_y) == False:
        for index, column in enumerate(vf.select_dtypes(include=['float64'])):
            missing_data_exists = vf[column].isna().any()
            if missing_data_exists:
                imputer = SimpleImputer(strategy=strategy_value)
                vf[column] = imputer.fit_transform(vf[[column]])
                missingvalues_list.append({
                    "column_index": index,
                    "strategy_tyoe": strategy_value,
                    "weight": saveOBjtoFile(imputer,folder_uuid),
                    "dataset": "V"
                })
            else:
                pass

    # Step 6: Split dataset into training and testing sets
    if has_x == True and has_y == True:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_value, random_state=0)

    elif (has_x and has_y) == False:
        v_train, v_test = train_test_split(vf, test_size=test_size_value, random_state=0)

    else:
        pass  # nothing to do here

    # Step 7: Scale numerical features using StandardScaler

    if standard_scalar == True and (has_x and has_y) == True:
        scaler = StandardScaler()
        numerical_columns = X_train.select_dtypes(include=['float64', 'int']).columns.tolist()
        X_train[numerical_columns] = scaler.fit_transform(X_train[numerical_columns])
        X_test[numerical_columns] = scaler.transform(X_test[numerical_columns])
        standard_scalar_weight = scaler

    if standard_scalar == True and (has_x and has_y) == False:
        scaler = StandardScaler()
        numerical_columns = v_train.select_dtypes(include=['float64', 'int']).columns.tolist()
        v_train[numerical_columns] = scaler.fit_transform(v_train[numerical_columns])
        v_test[numerical_columns] = scaler.transform(v_test[numerical_columns])
        standard_scalar_weight = scaler

    if normal_scalar == True and (has_x and has_y) == True:
        scaler = MinMaxScaler()
        numerical_columns = X_train.select_dtypes(include=['float64', 'int']).columns.tolist()
        X_train[numerical_columns] = scaler.fit_transform(X_train[numerical_columns])
        X_test[numerical_columns] = scaler.transform(X_test[numerical_columns])
        standard_scalar_weight = scaler

    if normal_scalar == True and (has_x and has_y) == False:
        scaler = MinMaxScaler()
        numerical_columns = v_train.select_dtypes(include=['float64', 'int']).columns.tolist()
        v_train[numerical_columns] = scaler.fit_transform(v_train[numerical_columns])
        v_test[numerical_columns] = scaler.transform(v_test[numerical_columns])
        standard_scalar_weight = scaler

    # Step 8 Extract the object to be saved and save it
    # Create a dictionary object to hold the variables
    obj = {
        "labelencoding_list": labelencoding_list,
        "standard_scalar_weight": {"status": standard_scalar, "object": saveOBjtoFile(standard_scalar_weight,folder_uuid)},
        "normalize_scalar_weight": {"status": normal_scalar, "object": saveOBjtoFile(normalize_scalar_weight,folder_uuid)},
        "missingvalues_list": missingvalues_list,
    }

    file_uuid = uuid.uuid4()
    weight_file_name = str(file_uuid) + ".pkl"

    file_path = os.path.join(folder_uuid, weight_file_name)

    with open(file_path, "wb") as f: # After saving, zip folder content and save to s3
        pickle.dump(obj, f)


    # Step 9: Return the preprocessed DataFrame and split datasets and pkl file
    if (has_x and has_y) == True:
        return X_train, X_test, y_train, y_test, df, X, y, file_path

    if (has_x and has_y) == False:
        return v_train, v_test, [], [], df, vf, [], file_path



def auto_preprocess_data_transform(array, weight_file_name):
    '''
    Step 1: load the saved weight
    Step 2: Handle date variable
    Step 3: Handle all encoded columns using the encoded weights [fix items for LE saving diff from OHE saving]
    Step 4: Handle numerical missing data using SimpleImputer value
    Step 5: Scale numerical features using loaded scaler
    '''

    # Step 1: load the saved weight
    with open(weight_file_name, "rb") as f:
        obj = pickle.load(f)

    # print(obj)

    labelencoding_list = obj["labelencoding_list"]
    standard_scalar_weight = obj["standard_scalar_weight"]
    normalize_scalar_weight = obj["normalize_scalar_weight"]
    missingvalues_list = obj["missingvalues_list"]

    # Step 2: Handle date variable
    for column in array.columns:
        if array[column].dtype == 'datetime64[ns]':
            array[column + '_dayofweek'] = array[column].dt.dayofweek
            array[column + '_month'] = array[column].dt.month
            array[column + '_year'] = array[column].dt.year
            array = array.drop(columns=[column])
    # print(array)

    # Step 3: Handle all encoded columns using the encoded weights [fix items for LE saving diff from OHE saving]
    for index, column in enumerate(array.select_dtypes(include=['object'])):
        for labelencoder in labelencoding_list:
            column_index = labelencoder["column_index"]
            dataset = labelencoder["dataset"]
            weightfile = labelencoder["weight"]

            if index == column_index:  # map generated column to current column
                if (dataset == "any") or (dataset == "X"):
                    # print("************* I got here **********")
                    # print(labelencoder["encoding_type"])
                    with open(weightfile, 'rb') as f:
                        weight = pickle.load(f)

                    temp = array.iloc[:, index]
                    temp = weight.transform(temp.values.reshape(-1, 1))
                    array = array.drop(array.columns[column_index], axis=1)
                    array = pd.concat([array, pd.DataFrame(temp)], axis=1)

                # elif dataset == "y":
                #   array = weight.transform(array)

    # Step 4: Handle numerical missing data using SimpleImputer value
    for imputer in missingvalues_list:
        column_index = imputer["column_index"]
        missing_strategy = imputer["strategy_tyoe"]
        weight_link = imputer["weight"]
        dataset = imputer["dataset"]
        if dataset == "X":
            with open(weight_link, 'rb') as f:
                weight = pickle.load(f)

            imputer_obj = SimpleImputer(strategy=missing_strategy, fill_value=weight)
            temp = array.iloc[:, column_index]

            temp = imputer_obj.fit_transform(temp.values.reshape(-1, 1))
            array = np.array(array)
            array[:, column_index] = temp.ravel()
            array = pd.DataFrame(array)

    # Step 5: Scale numerical features using loaded scaler
    # 'normalize_scalar_weight': {'status': False, 'object': 'fede509d-0bfd-4929-91ae-7e6ed988a631.pkl'}
    # 'standard_scalar_weight': {'status': True, 'object': '6776afa2-2031-4ffe-92b9-ff3bb9416c90.pkl'}

    # standard_scalar_weight = obj["standard_scalar_weight"]
    # normalize_scalar_weight = obj["normalize_scalar_weight"]

    if normalize_scalar_weight["status"] == True:
        with open(normalize_scalar_weight["object"], 'rb') as f:
            weight = pickle.load(f)

        array = weight.transform(array)

    if standard_scalar_weight["status"] == True:
        with open(standard_scalar_weight["object"], 'rb') as f:
            scaler = pickle.load(f)

        array = scaler.transform(array)

    return array


def tuplelize(boundary_list: str):
    # Here, the boundary string is processed into a list of boundaries of different dimensionalities without any whitespaces
    boundaries = boundary_list.replace(" ", "").split(",")
    # The list of different dimensionality slices is predefined here
    slices = []

    for boundary in boundaries:
        # Since ':' returns everything, slice(None) is used meaning that nothing is filtered out
        if boundary == ":":
            slices.append(slice(None))
        elif ":" in boundary:
            # If the boundary contains ':' and any other value(s) (type integer hopefully else an exception is raised),
            # then those extra values are accounted for
            sub_items = boundary.split(":")
            slice_items = []

            # Here, each value around the colon is processed and added to the slices
            for sub in sub_items:
                try:
                    slice_items.append(int(sub))
                except ValueError:
                    # All non integer values are handled here. Empty spaces are equivalent to None values for the slice function
                    if sub == "":
                        slice_items.append(None)
                    # Error values are caught here
                    else:
                        pass

            # The slice function is autofilled here, thereby allowing for both double and triple values to be parsed
            for i in range(3 - len(slice_items)):
                slice_items.append(None)
            slices.append(slice(slice_items[0], slice_items[1], slice_items[2]))
        else:
            # Single integers are processed and appended here
            try:
                slices.append(int(boundary))
            # Error values are caught here
            except:
                pass

    # Convertion of the list of slices to a tuple occurs below
    if len(slices) > 1:
        return tuple(slices)
    else:
        return slices[0]