"""
Module containing functions to read in data from ngspice output
"""
from typing import Dict, List, TextIO, Tuple, Union


def parse_ngspice_sim_output(file: TextIO) -> Tuple[str, str, str, List[Dict[str, Union[str, float]]]]:
    """
    Parse the file created by the ngspice write command
    and return the data and metadata
    """
    # Parse header including plot type
    line_1 = file.readline()
    line_2 = file.readline()
    line_3 = file.readline()
    # if this is an AC analysis we need to tell the rest of the parser this
    ac_analysis = True if line_3 == "Plotname: AC Analysis\n" else False
    if ac_analysis:
        print("Detected data of ac sweep")
        plot_type = "ac"
    else:
        print("Detected data of transient analysis")
        plot_type = "tran"
    title = " ".join(line_3.split(" ")[1:] + ["of"] + line_1.split(" ")[1:])
    date = " ".join(line_2.split(" ")[1:])
    del line_1
    del line_2
    del line_3
    file.readline()

    # parse variables
    number_of_variables = int(file.readline().split(" ")[-1])
    number_of_points = int(file.readline().split(" ")[-1])
    simvars = []
    file.readline()
    vars_left = number_of_variables
    if ac_analysis:
        var_name_line = file.readline().split("\t")
        var_name = var_name_line[-3].strip()
        var_type = var_name_line[-2].strip()
        var_unit = "[Hz]"
        simvars.append({'name': var_name, 'type': var_type,
                       'unit': var_unit, 'data': []})
        vars_left -= 1
    for _ in range(vars_left):
        var_name_line = file.readline().split("\t")
        var_name = var_name_line[-2].strip()
        var_type = var_name_line[-1].strip()
        if var_type == "time":
            var_unit = "[s]"
        elif var_type.lower() == "voltage":
            var_unit = "[V]"
        elif var_type.lower() == "current":
            var_unit = "[I]"
        elif var_type.lower() == "frequency":
            var_unit = "[Hz]"
        elif var_type.lower() == "decibel":
            var_unit = "dB"
            var_type = "relative Amplitude"
        else:
            var_unit = "unknown unit"
        simvars.append({'name': var_name, 'type': var_type,
                       'unit': var_unit, 'data': []})
    file.readline()
    for _ in range(number_of_points):
        match plot_type:
            case "ac":
                for i in range(number_of_variables):
                    tokens = file.readline().split("\t")
                    string_val = tokens[-1]
                    amp_and_phase = string_val.split(',')
                    amplitude = amp_and_phase[0].strip()
                    phase = amp_and_phase[1].strip()
                    simvars[i]['data'].append(
                        (float(amplitude), float(phase)))
            case "tran":
                for i in range(number_of_variables):
                    tokens = file.readline().split("\t")
                    simvars[i]['data'].append(
                        float(tokens[-1][:-1]))
        file.readline()
    return plot_type, title, date, simvars
