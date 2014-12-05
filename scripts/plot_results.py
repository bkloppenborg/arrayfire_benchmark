#!/usr/bin/python

# general functionality
import glob
import numpy as np
import argparse
# plotting
import matplotlib.pyplot as plt  
import math
import matplotlib.cm as cm

class read_state():
    """A class representing an enumerated state of the Celero file reader
    """
    start = 0
    header = 1
    result_row = 2
    finished = 3

def list_recordTable_groups(results):
    """Returns a unique sorted list of all groups of benchmarks
    """
    all_groups = list()
    for result in results:
        all_groups.append(result['group'])
        
    unique_groups = set(all_groups)
    unique_groups = sorted(unique_groups)
    return unique_groups

def list_recordTable_attribute(results, attribute):

    entries = list()
    for result in results:
        entries.append(result['extra_data'][attribute])
        
    unique_entries = set(entries)
    unique_entries = sorted(unique_entries)
    return unique_entries

def parse_celero_recordTable_header(header_row):
    """
    Parses a Celero recordTable header row separating the row into the 
    data size and other field sections. Returns a list of the following
    structures:
    
        data_sizes - np.ndarray containing the sizes of the data
        other_fields - extra fields
        split_start - where the data_sizes split begins
        split_end - where the data_sizes split ends
    
    """
   
    data_sizes = filter(lambda x: x.isdigit(), header_row)
    other_fields = filter(lambda x: not x.isdigit(), header_row)
    other_fields = filter(lambda x: x != "", other_fields)
    
    split_start = len(other_fields) + 1
    split_end = split_start + len(data_sizes)
    
    data_sizes = map(int, data_sizes)
    data_sizes = np.array(data_sizes)
    
    return [data_sizes, other_fields, split_start, split_end]


def plot_time_vs_size(results, show_backend=False):
    """ Creates a plot of execution time vs. data size
    """
    
    colors = cm.rainbow(np.linspace(0, 1, len(results)))

    # plot execution time vs. data size
    color_id = 0
    for result in results:
        x = np.sqrt(result['data_sizes'])
        y = result['times']
        
        # construct the label
        label = result['extra_data']['AF_DEVICE']
        if show_backend:
            label += " " + result['extra_data']['AF_PLATFORM'] 
         
        plt.scatter(x, y, color=colors[color_id], label=label)
        plt.plot(x,y, color=colors[color_id], label=None)
        color_id += 1

    # set specific plot options
    plt.xlim(0,plt.xlim()[1])
    plt.ylim(0,plt.ylim()[1])
    plt.title(results[0]['group'])
    plt.ylabel("Execution time (micro-seconds)")
    plt.xlabel("Image width")
    plt.legend(loc='upper left', numpoints=1)
    plt.show()
    
def plot_throughput_vs_size(results, show_backend=False):

    colors = cm.rainbow(np.linspace(0, 1, len(results)))

    # plot for throughput vs. data size
    color_id = 0
    for result in results:
        x = np.sqrt(result['data_sizes'])
        y = result['data_sizes'] / result['times']
        
        # construct the label
        label = result['extra_data']['AF_DEVICE']
        if show_backend:
            label += " " + result['extra_data']['AF_PLATFORM'] 
         
        plt.scatter(x, y, color=colors[color_id], label=label)
        plt.plot(x,y, color=colors[color_id], label=None)
        color_id += 1
        
    # set specific plot options
    plt.xlim(0,plt.xlim()[1])
    plt.ylim(0,plt.ylim()[1])
    plt.title(results[0]['group'])
    plt.ylabel(r"Throughput ($10^9$ elements / second)")
    plt.xlabel("Image width")
    plt.legend(loc='upper left', numpoints=1)
    plt.show()

def plot_image_rate_vs_size(results, show_backend=False):

    colors = cm.rainbow(np.linspace(0, 1, len(results)))

    # plot images/second vs. data size
    color_id = 0
    for result in results:
        x = np.sqrt(result['data_sizes'])
        y = 1.0/(result['times'] * 1E-9) / 1E6
       
        # construct the label
        label = result['extra_data']['AF_DEVICE']
        if show_backend:
            label += " " + result['extra_data']['AF_PLATFORM'] 
         
        plt.scatter(x, y, color=colors[color_id], label=result['extra_data']['AF_DEVICE'])
        plt.plot(x,y, color=colors[color_id], label=None)
        color_id += 1

    # set specific plot options
    plt.xlim(0,2048)
    plt.ylim(0,plt.ylim()[1])
    plt.title(results[0]['group'])
    plt.ylabel(r"Throughput ($10^6$ images / second)")
    plt.xlabel("Image width")
    plt.legend(loc='upper right', numpoints=1)
    plt.show()

def read_celero_recordTable(filename):
    """
    Splits a group of Celero test results into individual results which can
    be plotted.
    """
    
    infile = open(filename, 'r')
    
    # The results are structured as follows
    #  group_name0,...
    #  '',extra_0,...,extraN,size0,...,sizeN
    #  benchmark0,extra0,...,extraN,time0,...,timeN
    #  ...
    #  benchmarkM,extra0,...,extraN,time0,...,timeN
    #  '',... (or otherwise blank)
    #  group_name1,...
    
    # output variables
    output = list()
    # state and data variables
    state = read_state.start
    group = ""
    data_sizes = list()
    other_fields = list()
    split_start = 0
    split_end = 0
    
    for line in infile:
    
        # End of a group, clear variables
        if state == read_state.finished:
            group = ""
            data_sizes = list()
            other_fields = list()
            split_start = 0
            split_end = 0
            # reset the read state
            state = read_state.start
            
        # strip off newline, split the line, remove empty fields
        line = line.strip("\n")
        line = line.split(',')
        line = filter(lambda x: x != "", line)      
        
        # check for the end of the group
        if len(line) == 0:
            state = read_state.finished
            continue
            
        # group ID row
        if state == read_state.start:
            group_name = line[0]
            state = read_state.header
            continue
            
        # header row
        if state == read_state.header:
            [data_sizes, other_fields, split_start, split_end] = parse_celero_recordTable_header(line)
            state = read_state.result_row
            continue
            
        # result row
        if state == read_state.result_row:
            benchmark_name = line[0]
            
            other_data = line[1:split_start]
            t_times = line[split_start:split_end]
            t_times = map(float, t_times)
            t_times = np.array(t_times)
            
            extra_data = dict(zip(other_fields, other_data))
            
            result = {'group': group_name, 'benchmark_name': benchmark_name, 
                'data_sizes': data_sizes, 'times': t_times,
                'extra_data': extra_data}
            
            output.append(result)
        
    return output
    
def import_directory(directory):
    """
    Creates a list of all .csv files in a directory, imports them using
    read_celero_recordTable, and returns the result.
    """

    csv_files = glob.glob(directory + "/*.csv")
    
    results = list()        
    
    for filename in csv_files:
        results.extend(read_celero_recordTable(filename))
        
    return results

def main():
    
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    # general arguments / functionality for any recordTable result
    parser.add_argument("-d", "--directory", 
        help="Parse all files in the specified directory")
    parser.add_argument("-f", "--file", 
        help="Parse the specified file")
    parser.add_argument("-lg", "--list-groups", 
        help="List all test groups found in the file/directory",  action="store_true")
     
    # arguments specific to the ArrayFire's benchmarking
    parser.add_argument("-t", "--data-type", 
        help="Show results only for a specific data type [f32, f64]")
    parser.add_argument("-g", "--groups", action='append',
        help="Show results for specific groups (may be combined with -t)")
    parser.add_argument("-lb", "--list-backends", action="store_true",
        help="Lists the backends found in the tests")    
    parser.add_argument("-b", "--backend", action='append',
        help="Show plots for specific backends")  
        
    args = parser.parse_args()
  
    results = list()
    if args.directory:
        results = import_directory(args.directory)
    else:
        results = read_celero_recordTable(filename)
        
    # list groups of benchmarks then exit
    if args.list_groups:
        groups = list_recordTable_groups(results)
        for entry in groups:
            print(entry)
        quit()
    
    # list backends found in the data, then exit            
    if args.list_backends:
        backends = list_recordTable_attribute(results, 'AF_PLATFORM')
        print backends
        quit()
    
    # Limit what will be plotted by explicitly including the arguments
    # specified on the command line
    include_groups = list()
    all_groups = list_recordTable_groups(results)
    # include specific data types
    if args.data_type:
        include_groups = filter(lambda x: x[-3:] == args.data_type, all_groups)
        
    # include specific tests
    if args.groups:         
        include_groups.extend(args.groups)
    
    # If no specific options have been set, include all groups by default
    if len(include_groups) == 0:
        include_groups = all_groups
    
    # Apply filtering
    # limit by groups
    results = filter(lambda x: x['group'] in include_groups, results)
    # limit by backend
    if args.backend:
        results = filter(lambda x: x['extra_data']['AF_PLATFORM'] in args.backend, results)
            
    # make the plots
    groups = list_recordTable_groups(results)
    for group in groups:
        # extract only the results which match this group
        temp = filter(lambda x: x['group'] == group, results)
        # remove the baseline measurements from the plots
        temp = filter(lambda x: x['benchmark_name'] != "Baseline", temp)
        
        show_backend = False
        if len(args.backend) > 1:
            show_backend = True
        
        plot_time_vs_size(temp, show_backend=show_backend)
        plot_throughput_vs_size(temp, show_backend=show_backend)
        plot_image_rate_vs_size(temp, show_backend=show_backend)
         
    
# Run the main function if this is a top-level script:
if __name__ == "__main__":
    main()
