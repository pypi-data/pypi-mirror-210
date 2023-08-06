import pandas as pd
import numpy as np

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


def boundaries_to_indices(boundaries, column_indices, format="int", obj="pd"):
    # print(
    #     "Boundaries to indices, Boundaries:",
    #     boundaries,
    #     "Column Indices:",
    #     column_indices,
    # )
    if boundaries == None:
        return None

    if type(boundaries) == list:
        columns = (
            list([str(x) for x in boundaries])
            if format == "str"
            else list([int(x) for x in boundaries])
        )

    else:
        if type(boundaries) == str and boundaries.find(",") > -1:
            # print("Found , in boundaries")
            blist = boundaries.split(",")
            return (
                tuplelize(blist[0]),
                boundaries_to_indices(blist[1], column_indices),
            )

        elif type(column_indices) == pd.DataFrame:
            column_indices = column_indices.columns.values.tolist()
            column_indices = list(range(len(column_indices)))
            column_indices = (
                np.array(list([str(x) for x in column_indices]))
                if format == "str"
                else np.array(list([int(x) for x in column_indices]))
            )

        elif type(column_indices) == type(np.array([2, 3])):
            columns_len = column_indices.shape[1]
            column_indices = np.array(list(range(columns_len)))
            # print("Processed numpy column indices:", column_indices)
        tuplelized = tuplelize(boundaries)
        print("Tuplelized", tuplelized)
        columns = column_indices[tuplelized]
        if type(columns) == np.int_:
            # print("Detected int column")
            columns = [
                int(columns),
            ]
            # print(columns)
        columns = list(columns)

    if obj == "np":
        print("Processing np boundary")
        if not "," in boundaries:
            print("Appending slice")
            return slice(None), columns
    return columns