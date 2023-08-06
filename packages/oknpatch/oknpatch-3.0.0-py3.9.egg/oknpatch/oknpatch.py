import json
import csv
import commentjson
import numpy as np
import math
import os
import time
import argparse
from scipy.signal import medfilt
import sys
import pkg_resources


# This function is to get the positions in given array
def get_index(search_input, array_in):
    idx_found = False
    return_idx = None
    for idx, val in enumerate(array_in):
        if val == search_input:
            idx_found = True
            return_idx = idx
            break

    if not idx_found:
        print(f"{search_input} can not be found!")

    return return_idx


# This function is update the csv file according to the config input
def run_updater(config, inputfile, outputfile, varargin=None):
    start_time = time.time()
    if varargin is not None:
        print("varargin is not none.")
    data_table = None
    row_count = None

    if isinstance(config, str):
        config = load_commented_json(config)

    if isinstance(inputfile, str):
        data_table = read_table(inputfile)

    # extra information
    extra = {"inputfile": inputfile, "outputfile": outputfile, "config": config}

    config_filter_info_array = config["filters"]

    for filter_info in config_filter_info_array:
        if filter_info["Enabled"]:
            data_table = dispatch_function(filter_info, data_table, extra)
        else:
            pass

    header_array = []
    for key in data_table:
        header_array.append(key)

    print("Start updating the csv!")
    with open(outputfile, mode='w', newline="") as destination_file:
        csv_writer = csv.DictWriter(destination_file, fieldnames=header_array)
        csv_writer.writeheader()

        row_count = len(data_table[header_array[0]])

        for i in range(row_count):
            temp_dict = {}
            for header in header_array:
                temp_dict[header] = data_table[header][i]
            csv_writer.writerow(temp_dict)
    print(f"csv is updated and it took {time.time() - start_time} sec")
    print("--------------------------------------------------------------------------------------")
    return outputfile


###########################################################
# FILTER DISPATCHER
###########################################################

# dispatch function

def dispatch_function(this_filter, y, extra):
    match_item = this_filter["function"]
    print(f"Dispatched function name: {match_item}")
    if match_item == 'cdp_direction':

        t = y[this_filter["input"]]
        # need to be fixed ********
        keyname = "need to be fixed"
        f = cdp_direction(extra.log, keyname, t)
        y[this_filter["output"]] = f

    elif match_item == 'reduce':

        print('reduce')

    elif match_item == 'dwnsample':

        t = y[this_filter["input"]]
        n = this_filter["target_samplerate"]
        dT = np.nanmean(np.diff(t))
        T = 1 / dT
        try:
            r = math.log(math.floor(T / n), 2)
        except ValueError:
            r = 0

        print('Target samplerate       = ', n)
        print('Estiametd samplerate    = ', T)
        print('Approximated reductions = ', r)

        if r == 0:
            return y

        p = dwnsample(y, r)
        y = p
        return y

    elif match_item == 'detectblinkV':

        x1 = y[this_filter["input"][0]]
        x2 = y[this_filter["input"][1]]
        x1 = medfilt(x1, 3)
        x2 = medfilt(x2, 3)

        # need to be continued
        print(x1)
        print(x2)

    elif match_item == 'deblinker2':

        x0 = y[this_filter["input"][0]]
        y0 = y[this_filter["input"][1]]
        th = this_filter["threshold"]

        i = deblinker2(x0, y0, th)
        y[this_filter["output"]] = i

    elif match_item == 'passthrough':

        f = y[this_filter["input"]]
        output_column = this_filter["output"]
        y[output_column] = f
        print(f"{output_column} column has been added to csv data.")

    elif match_item == 'dshift':

        f = y[this_filter["input"][0]]
        y[this_filter["output"]] = dshift(f)

    elif match_item == 'tidy':

        f = y[this_filter["input"][0]]
        n = this_filter["value"]
        thicken = this_filter["thicken"]

        is_tracking = y[this_filter["input"][1]]
        y[this_filter["output"]] = tidy(f, n, thicken, np.logical_not(is_tracking))

    elif match_item == 'wavelet':

        f = y[this_filter["input"][0]]
        if are_all_elements_nan(f):
            y[this_filter["output"]] = f
            return

        # need to check cell2mat equal numpy.array or not
        levelForReconstruction = np.array(this_filter["levelForReconstruction"])
        waveletType = this_filter["type"]
        level = this_filter["Level"]
        y[this_filter["output"]] = waveleter(f, levelForReconstruction, waveletType, level)

    elif match_item == 'spikeRemover':
        print(match_item)
    elif match_item == 'deblinker':
        print(match_item)
    elif match_item == 'shiftSignal':
        print(match_item)
    elif match_item == 'medianFilter':

        input_column = this_filter["input"][0]
        f = y[input_column]
        n = this_filter["npoint"]
        y[this_filter["output"]] = medfilt(f, n)
        print(f"{input_column} column has been median filtered with n point {n}.")

    elif match_item == 'replaceNanBy':

        input_column = this_filter["input"][0]
        input_array = y[input_column]
        pointer = this_filter["pointer"]
        y[this_filter["output"]] = replace_nan_by(y, input_array, pointer)

    elif match_item == 'applymask':
        print(match_item)
    elif match_item == 'detrender':
        print(match_item)
    elif match_item == 'detectblinkV':
        print(match_item)
    elif match_item == 'gradient':

        related_column_name_array = this_filter["input"]
        f = y[related_column_name_array[1]]
        t = y[related_column_name_array[0]]
        output_column = this_filter["output"]
        y[output_column] = grad(f, t)
        print(f"{output_column} column is added to the csv data by using gradient.")

    else:
        print('Function is not found')
    return y


def spike_remover(f):
    pass


def xdetectblink(x1, V, fps, varargin):
    pass


def detectblinkV(t, V, fps, varargin):
    pass


def dwnsample(M, N):
    F = len(M[next(iter(M))])
    N = int(N)
    if isinstance(N, int):
        loop_count = 0
        while loop_count < N:
            loop_count += 1
            for key in M:
                temp_array = M[key]
                temp_array = temp_array[0:F:2]
                M[key] = temp_array
    else:
        print("The number of loop input must be number!")

    return M


def replace_nan_by(y, input_array, pointer):
    if "<=" in pointer:
        try:
            column_name, value = str(pointer).split("<=")
            pointer_column__array = y[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) <= float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    elif "==" in pointer:
        try:
            column_name, value = str(pointer).split("==")
            pointer_column__array = y[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) == float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    elif ">=" in pointer:
        try:
            column_name, value = str(pointer).split(">=")
            pointer_column__array = y[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) >= float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    else:
        if ">" in pointer:
            try:
                column_name, value = str(pointer).split(">")
                pointer_column__array = y[column_name]
                array_length = len(input_array)
                for ind in range(array_length):
                    if float(pointer_column__array[ind]) > float(value):
                        input_array[ind] = np.nan
            except KeyError:
                pass
        elif "<" in pointer:
            try:
                column_name, value = str(pointer).split("<")
                pointer_column__array = y[column_name]
                array_length = len(input_array)
                for ind in range(array_length):
                    if float(pointer_column__array[ind]) < float(value):
                        input_array[ind] = np.nan
            except KeyError:
                pass
        else:
            pass

    return input_array


def waveleter(x, levelForReconstruction, waveletType, level):
    [x1, i] = fillmissing(x)
    x11 = x1

    return x11


def deblinker2(x, y, th):
    s = x * y
    i = (s > th)
    return i


def applymask(f, is_mask):
    pass


def deblinker(f, is_blinking):
    pass


def medianfilter(f, npoiint):
    pass


def tidy(f, npoint, n_thicken, is_deleted):
    # need  to be fixed
    return f


def dshift(f):
    y = np.nanmean(f)
    f1 = f - y
    return f1


def grad(f, t):
    df = np.gradient(f)
    dt = np.gradient(t)
    dfdt = df / dt
    return dfdt


def cdp_direction(logs, fname, t):
    return t


def load_commented_json(config_input):
    with open(config_input, 'r') as handle:
        protocol = commentjson.load(handle)
    return protocol


def read_table(input_file_dir):
    file = open(input_file_dir)
    csv_reader = csv.reader(file)
    header_array = []
    rows = []
    data_table_dict = {}
    count = 0

    for row in csv_reader:
        if count <= 0:
            header_array = row
            count += 1
        else:
            rows.append(row)

    # Take out 1 row for header
    row_count = len(rows) - 1

    for header in header_array:
        header_position = get_index(header, header_array)
        value_array = []
        for row in rows:
            # print(header)
            try:
                input_value = float(row[header_position])
            except ValueError:
                input_value = float("NaN")
            value_array.append(input_value)
        data_table_dict[header] = value_array

    return data_table_dict


def read_signal_csv(input_file_dir1):
    file1 = open(input_file_dir1)
    csv_reader = csv.reader(file1)
    header_array = []
    rows = []
    data_table_dict = {}
    count_one = 0

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    for header in header_array:
        header_position = get_index(header, header_array)
        value_array = []
        for row in rows:
            value_array.append(row[header_position])
        data_table_dict[header] = value_array

    return data_table_dict


# # This function is to get the positions in given array
# def get_index(search_input, array_in):
#     idx_found = False
#     return_idx = None
#     for idx, val in enumerate(array_in):
#         if val == search_input:
#             idx_found = True
#             return_idx = idx
#             break
#
#     if not idx_found:
#         print(f"{search_input} can not be found!")
#
#     return return_idx


# def medfilt1(x, k):
#     # Apply a length-k median filter to a 1D array x.
#     # Boundaries are extended by repeating endpoints.
#     assert k % 2 == 1, "Median filter length must be odd."
#     assert x.ndim == 1, "Input must be one-dimensional."
#     k2 = (k - 1) // 2
#     y = np.zeros((len(x), k), dtype=x.dtype)
#     y[:, k2] = x
#     for i in range(k2):
#         j = k2 - i
#         y[j:, i] = x[:-j]
#         y[:j, i] = x[0]
#         y[:-j, -(i + 1)] = x[j:]
#         y[-j:, -(i + 1)] = x[-1]
#     return np.median(y, axis=1)


def are_all_elements_nan(input_array):
    for ele in input_array:
        if not np.isnan(ele):
            return False
    return True


def fillmissing(input_array):
    # input_array = ma.masked_array(input_array, input_array == np.nan)
    # for shift in (-1, 1):
    #     for axis in (0, 1):
    #         shifted_array = np.roll(input_array, shift=shift, axis=axis)
    #         idx = ~shifted_array.mask * input_array.mask
    #         input_array[idx] = shifted_array[idx]
    return input_array


# This function is to detect okn from the given preprocessed csv and produce result folder which includes signal.csv
def detect_with_okn_detector(csv_to_b_detected, okn_detector_config_location, okn_detector_location):
    start_time = time.time()
    print(f"Sending the following directory to okn detector: {csv_to_b_detected}!")
    updated_filename = os.path.basename(csv_to_b_detected)
    out_put_dir = csv_to_b_detected.replace(updated_filename, "result")
    commandline = f"okndetector -c \"{okn_detector_config_location}\" -i \"{csv_to_b_detected}\" -o \"{out_put_dir}\""
    print(commandline)
    os.chdir(okn_detector_location)
    os.system(commandline)
    print(f"The result has been produced in the directory {out_put_dir}.")
    print(f"The process took {time.time() - start_time} sec.")
    print("--------------------------------------------------------------------------------------")

    return out_put_dir


# This function is to check whether file location and necessary file exist or not
# return array of element which contains file directory, exist or not, excepted file name
def get_file_dir_exist_array(file_name_array_input):
    file_dir_exist_array = []
    for expected_string, name in file_name_array_input:
        file_exist = os.path.isfile(name)
        if file_exist:
            if expected_string in str(name):
                file_exist = True
            else:
                file_exist = False
        file_dir_exist_array.append([name, file_exist, expected_string])
    return file_dir_exist_array


# This function is to get the positions in given array
def get_position(search_input, array_in):
    idx_found = False
    return_idx = None
    for idx, val in enumerate(array_in):
        if val == search_input:
            idx_found = True
            return_idx = idx
            break

    if not idx_found:
        print(f"{search_input} can not be found!")

    return return_idx


# This function is to read given csv and return first data of given column
def get_timestamp_from_csv(csv_dir_input, column_name_input):
    with open(csv_dir_input, "r") as csv_file:
        csv_data_array = csv.reader(csv_file, delimiter=',')
        header_array = next(csv_data_array)
        first_row = next(csv_data_array)
        data_position = get_position(column_name_input, header_array)

        return float(first_row[data_position])


# This function is to start and end index of given trial in given gaze.csv file
def get_start_end_info(csv_input, trial_id_input):
    start_index = None
    end_index = None
    with open(csv_input, "r") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        header_array = next(csv_data)
        rows = []
        for data in csv_data:
            rows.append(data)

        event_string_position = get_position("event_string", header_array)

        start_marker_found = False
        for index, row in enumerate(rows):
            event_string = row[event_string_position]
            if not start_marker_found:
                if "start_marker" in event_string and trial_id_input in event_string:
                    start_index = index
                    start_marker_found = True
            else:
                if "end_marker" in event_string:
                    end_index = index
                    break

        csv_file.close()
        return {"start_index": start_index, "end_index": end_index}


# This function is replace incorrect data rows with correct data rows
def replace_with_correct_data(trial_dir_input, gaze_dir_input, gaze_start_end_input):
    gaze_start_index = gaze_start_end_input["start_index"]
    gaze_end_index = gaze_start_end_input["end_index"]

    # get is_event, event_id and direction value from the input csv
    # because gaze.csv does not have these values
    with open(trial_dir_input, "r") as trial_csv_file:
        trial_csv_data = csv.reader(trial_csv_file, delimiter=',')
        trial_header_array = next(trial_csv_data)
        is_event_position = get_position("is_event", trial_header_array)
        event_id_position = get_position("event_id", trial_header_array)
        direction_position = get_position("direction", trial_header_array)
        trial_rows = []
        for data in trial_csv_data:
            trial_rows.append(data)
        is_event_value = trial_rows[0][is_event_position]
        event_id_value = trial_rows[0][event_id_position]
        direction_value = trial_rows[0][direction_position]
        trial_csv_file.close()

    # get the trial data from gaze.csv by using start index and end index
    with open(gaze_dir_input, "r") as gaze_csv_file:
        gaze_csv_data = csv.reader(gaze_csv_file, delimiter=',')
        header_array = next(gaze_csv_data)

        # sts = sensor timestamp, g = gaze, rts = record timestamp
        # get the header positions which rows need to be modified and used
        g_is_event_position = get_position("is_event", header_array)
        g_event_string_position = get_position("event_string", header_array)
        g_sts_position = get_position("sensor_timestamp", header_array)
        g_rts_position = get_position("record_timestamp", header_array)

        rows = []
        for data in gaze_csv_data:
            rows.append(data)
        correct_data_array = rows[gaze_start_index: gaze_end_index + 1]

        output_data_array = []

        first_sts = 0
        got_first_sts = False
        for data in correct_data_array:
            output_data = data
            # record first sensor timestamp to be used to calculate record timestamp
            if not got_first_sts:
                first_sts = float(data[g_sts_position])
                got_first_sts = True
            record_ts = float(data[g_sts_position]) - first_sts
            # noinspection PyTypeChecker
            # modify and add columns from gaze data to trial data
            output_data[g_rts_position] = record_ts
            output_data[g_is_event_position] = is_event_value
            output_data[g_event_string_position] = event_id_value
            output_data.append(direction_value)
            output_data_array.append(output_data)

        gaze_csv_file.close()

    # rewrite and replace incorrect data with correct data
    with open(trial_dir_input, mode='w', newline="") as new_destination_file:
        csv_writer = csv.DictWriter(new_destination_file, fieldnames=trial_header_array)
        csv_writer.writeheader()
        for data in output_data_array:
            data_to_write = {}
            for ind, name in enumerate(trial_header_array):
                data_to_write[name] = data[ind]
            csv_writer.writerow(data_to_write)

        new_destination_file.close()


# This function is the main function to correct trial data lost issue
# by calling get_start_end_info and replace_with_correct_data
# It also has error handling in case of error
def fix_trial_data_lost(trial_dir_input, gaze_dir_input):
    success = True
    error_string = None
    try:
        trial_csv_file_name = os.path.basename(trial_dir_input)
        output_dir = str(trial_dir_input).replace(trial_csv_file_name, "")
        trial_id, extra_string = str(trial_csv_file_name).split("_", 1)
        gaze_start_end_info = get_start_end_info(gaze_dir_input, trial_id)

        replace_with_correct_data(trial_dir_input, gaze_dir_input, gaze_start_end_info)
    except Exception as error:
        success = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_string = f"Error occurred:error type:{type(error).__name__} in line number:{exc_tb.tb_lineno}."
        trial_csv_file_name = None
        output_dir = None

    return trial_csv_file_name, output_dir, success, error_string


# This function is to get the build-in directory of config file by package name and config file name
def get_config_location(package_name, config_file_name):
    config_dir = pkg_resources.resource_filename(package_name, config_file_name)

    return config_dir


# This function is to update the trial csv file by calling run_updater function
# It has error handling in case of error
def update_csv(input_csv_file_dir, extra_string_for_updated_csv, updater_config):
    success = True
    error_string = None
    try:
        csv_file_name = os.path.basename(input_csv_file_dir)
        updated_file_name = extra_string_for_updated_csv + csv_file_name
        output_dir = input_csv_file_dir.replace(csv_file_name, updated_file_name)
        output_csv_dir = run_updater(updater_config, input_csv_file_dir, output_dir)
        trial_csv_file_name = os.path.basename(output_csv_dir)
        output_dir_without_folder = output_csv_dir.replace(trial_csv_file_name, "")
    except Exception as error:
        success = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_string = f"Error occurred:error type:{type(error).__name__} in line number:{exc_tb.tb_lineno}."
        trial_csv_file_name = None
        output_dir_without_folder = None

    return trial_csv_file_name, output_dir_without_folder, success, error_string


def replace_with_new_direction(csv_file_input, direction_input):
    with open(csv_file_input, "r") as trial_csv_file:
        trial_csv_data = csv.reader(trial_csv_file, delimiter=',')
        trial_header_array = next(trial_csv_data)
        direction_position = get_position("direction", trial_header_array)
        trial_rows = []
        for data in trial_csv_data:
            trial_rows.append(data)
        trial_csv_file.close()

    for row in trial_rows:
        row[direction_position] = direction_input

    # rewrite and replace incorrect data with correct data
    with open(csv_file_input, mode='w', newline="") as new_destination_file:
        csv_writer = csv.DictWriter(new_destination_file, fieldnames=trial_header_array)
        csv_writer.writeheader()
        for data in trial_rows:
            data_to_write = {}
            for ind, name in enumerate(trial_header_array):
                data_to_write[name] = data[ind]
            csv_writer.writerow(data_to_write)

        new_destination_file.close()


def change_direction_and_rerun(csv_file_input, direction_input, extra_string_input, updater_config_input,
                               detector_config_input, detector_location_input):
    success = True
    error_string = None
    try:
        replace_with_new_direction(csv_file_input, direction_input)
        updated_file, output_file_location, success, error = update_csv(csv_file_input,
                                                                        extra_string_input,
                                                                        updater_config_input)
        updated_file_dir = os.path.join(output_file_location, updated_file)
        result_folder_dir = detect_with_okn_detector(updated_file_dir, detector_config_input, detector_location_input)
    except Exception as error:
        success = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_string = f"Error occurred:error type:{type(error).__name__} in line number:{exc_tb.tb_lineno}."
        result_folder_dir = None

    return result_folder_dir, success, error_string


def main():
    parser = argparse.ArgumentParser(prog='oknpatch',
                                     description='OKNPATCH package.')
    # parser.add_argument("oknpatch -t trial_data_lost -i csv_to_be_fixed -gi gaze_csv_to_be_referenced")
    # parser.add_argument("oknpatch -t update -i csv_to_be_updated [-es extra_string] [-uc updater_config]")
    # parser.add_argument("oknpatch -t change_direction_and_rerun -i csv_to_be_fixed -di direction_input [-es "
    #                     "extra_string] [-uc updater_config] [-okndc okn_detector_config] -okndl okn_detector_location")
    parser.add_argument('--version', action='version', version='3.0.0'),
    parser.add_argument("-t", dest="type_input", required=True, default=sys.stdin,
                        help="issue type to fix", metavar="issue type")
    parser.add_argument("-i", dest="input_file", required=False, default=sys.stdin,
                        metavar="input file to be fixed or updated")
    parser.add_argument("-gi", dest="gaze_input", required=False, default=sys.stdin,
                        metavar="gaze file to be referenced")
    parser.add_argument("-es", dest="extra_string", required=False, default=sys.stdin,
                        metavar="extra string to be used to named update csv")
    parser.add_argument("-uc", dest="updater_config", required=False, default=sys.stdin,
                        metavar="config to be used to update input csv")
    parser.add_argument("-di", dest="direction_input", required=False, default=sys.stdin,
                        metavar="direction input to rerun")
    parser.add_argument("-okndc", dest="okn_detector_config", required=False, default=sys.stdin,
                        metavar="config to be used to in okn detector")
    parser.add_argument("-okndl", dest="okn_detector_location", required=False, default=sys.stdin,
                        metavar="okn detector location")

    args = parser.parse_args()
    type_input = args.type_input
    input_file = args.input_file
    input_file_exist = True if "io.TextIOWrapper" not in str(input_file) else False

    if str(type_input) == "trial_data_lost":
        gaze_input = args.gaze_input
        gaze_input_exist = True if "io.TextIOWrapper" not in str(gaze_input) else False
        # If first input and second input are provided or not "None"
        if input_file_exist and gaze_input_exist:
            # Check whether any of those files is missing or not and the file name is correct or not
            file_name_array = [["trial", input_file], ["gaze", gaze_input]]
            dir_exist_array = get_file_dir_exist_array(file_name_array)
            all_file_found = True

            # Display if any of file is missing
            for exist_array in dir_exist_array:
                if not exist_array[1]:
                    print("")
                    print(f"Error! {exist_array[2]} file is missing in {exist_array[0]}.")
                    print("")
                    all_file_found = False

            # No file is missing
            if all_file_found:
                print("")
                print("All necessary csv files are found.")
                print("")
                output_file, output_file_location, success, error = fix_trial_data_lost(input_file, gaze_input)
                if success:
                    print(f"{output_file} is created in {output_file_location}")
                else:
                    print(error)
        else:
            if not input_file_exist and not input_file_exist:
                print("")
                print(f"Necessary arguments are missing to run oknpatch:{type_input}.")
                print("Example Usage:")
                print("oknpatch -t trial_data_lost -i csv_to_be_fixed -gi gaze_csv_to_be_referenced")
                print("")
            elif not input_file_exist:
                print("")
                print(f"File to be fixed or updated is missing in the argument to fix {type_input} issue.")
                print("Example Usage:")
                print("oknpatch -t trial_data_lost -i csv_to_be_fixed -gi gaze_csv_to_be_referenced")
                print("")
            elif not gaze_input_exist:
                print("")
                print(f"Gase file input is missing to fix {type_input} issue.")
                print("Example Usage:")
                print("oknpatch -t trial_data_lost -i csv_to_be_fixed -gi gaze_csv_to_be_referenced")
                print("")
    elif str(type_input) == "update":
        extra_string = args.extra_string
        updater_config = args.updater_config
        extra_string_exist = True if "io.TextIOWrapper" not in str(extra_string) else False
        updater_config_exist = True if "io.TextIOWrapper" not in str(updater_config) else False
        # If first input is provided or not "None"
        if input_file_exist:
            # Check whether input file exists or not
            file_exist = os.path.isfile(input_file)
            if file_exist:
                print("")
                print("Input file is found.")
                print("")
                # Determine whether default extra_string or custom input needs to be used
                if extra_string_exist:
                    extra_string = str(extra_string)
                else:
                    print("There is no extra string input to name updated_csv.")
                    extra_string = "updated_"
                    print(f"Therefore using default extra string:{extra_string}")

                # Determine whether build-in config or input config needs to be used
                if updater_config_exist:
                    config_dir_exist = os.path.isfile(updater_config)
                    if config_dir_exist:
                        updater_config_location = updater_config
                    else:
                        print("Input updater config does not exist.")
                        updater_config_location = get_config_location("oknpatch", "gazefilters.json")
                        print(f"Therefore using default updater config from package.")
                else:
                    print("There is no update config location input.")
                    updater_config_location = get_config_location("oknpatch", "gazefilters.json")
                    print(f"Therefore using default updater config from package.")
                output_file, output_file_location, success, error = update_csv(input_file,
                                                                               extra_string,
                                                                               updater_config_location)
                if success:
                    print(f"{output_file} is created in {output_file_location}")
                else:
                    print(error)
            else:
                print(f"Input file:{input_file} does not exist.")
        else:
            print("")
            print(f"Input file to be fixed is missing to fix {type_input} issue.")
            print("oknpatch -t update -i csv_to_be_updated [-es extra_string] [-uc updater_config]")
            print("")
    elif str(type_input) == "change_direction_and_rerun":
        extra_string = args.extra_string
        updater_config = args.updater_config
        direction_input = args.direction_input
        okn_detector_config = args.okn_detector_config
        okn_detector_location = args.okn_detector_location
        extra_string_exist = True if "io.TextIOWrapper" not in str(extra_string) else False
        updater_config_exist = True if "io.TextIOWrapper" not in str(updater_config) else False
        direction_input_exist = True if "io.TextIOWrapper" not in str(direction_input) else False
        okn_detector_config_exist = True if "io.TextIOWrapper" not in str(okn_detector_config) else False
        okn_detector_location_exist = True if "io.TextIOWrapper" not in str(okn_detector_location) else False
        if input_file_exist and direction_input_exist and okn_detector_location_exist:
            # Determine whether default extra_string or custom input needs to be used
            if extra_string_exist:
                extra_string = str(extra_string)
                print("Extra string input is found.")
            else:
                extra_string = "updated_"
                print(f"There is no extra string input. Therefore using default extra string:{extra_string}")
            # Determine whether build-in updater config or input updater config needs to be used
            if updater_config_exist:
                config_dir_exist = os.path.isfile(updater_config)
                if config_dir_exist:
                    print("Input updater config location is found.")
                    updater_config_location = updater_config
                else:
                    print("Input updater config does not exist.")
                    updater_config_location = get_config_location("oknpatch", "gazefilters.json")
                    print(f"Therefore using default updater config from package.")
            else:
                print("There is no update config location input.")
                updater_config_location = get_config_location("oknpatch", "gazefilters.json")
                print(f"Therefore using default updater config from package.")
            if okn_detector_config_exist:
                okn_detector_config_dir_exist = os.path.isfile(okn_detector_config)
                if okn_detector_config_dir_exist:
                    print("Input updater config location is found.")
                    okn_detector_config_location = updater_config
                else:
                    print("Input updater config does not exist.")
                    okn_detector_config_location = get_config_location("oknpatch", "okndetector.gaze.config")
                    print(f"Therefore using default updater config from package.")
            else:
                print("There is no update config location input.")
                okn_detector_config_location = get_config_location("oknpatch", "okndetector.gaze.config")
                print(f"Therefore using default updater config from package.")
            result_folder_dir, success, error = change_direction_and_rerun(input_file, direction_input,
                                                                           extra_string, updater_config_location,
                                                                           okn_detector_config_location,
                                                                           okn_detector_location)
            if success:
                print(f"Rerunning is successful and result folder is created in {result_folder_dir}.")
            else:
                print(error)
        else:
            if not input_file_exist and not direction_input_exist:
                print("")
                print(f"Necessary arguments are missing to run oknpatch:{type_input}.")
                print("Example Usage:")
                print("oknpatch -t change_direction_and_rerun -i csv_to_be_fixed -di direction_input [-es "
                      "extra_string] [-uc updater_config] [-okndc okn_config] -okndl okn_location")
                print("")
                print("")
            else:
                if not input_file_exist:
                    print("")
                    print("The csv file to be fixed is missing.")
                    print("oknpatch -t change_direction_and_rerun -i csv_to_be_fixed -di direction_input -okndl "
                          "okn_location")
                    print("")
                if not direction_input_exist:
                    print("")
                    print("The direction input is missing.")
                    print("oknpatch -t change_direction_and_rerun -i csv_to_be_fixed -di direction_input -okndl "
                          "okn_location")
                    print("")
                if not okn_detector_location_exist:
                    print("")
                    print("The okn detector location input is missing.")
                    print("oknpatch -t change_direction_and_rerun -i csv_to_be_fixed -di direction_input -okndl "
                          "okn_location")
                    print("")

    else:
        print(f"Invalid issue type: {type_input}")
