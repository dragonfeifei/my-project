import argparse
import csv
from collections import defaultdict

def main(actual_price_file, predicted_price_file, window_size_file, output_file):
    # get window size from file
    window_size = None
    with open(window_size_file, 'r') as file:
        window_size = int(file.read())

    ''' Data structure for holding actual stock prices

    Nested dictionary is used for fast accessing of any stock
    price at any hour.
    The outer dict uses 'time' as key. Value is another dict
    which contains all the stocks and prices within that hour.
    e.g. 
    {
        1: { 'STOCK1': 9.9, 'STOCK2': 99.8 },
        2: { 'STOCK1': 10.0, 'STOCK2': 101.2 }
    }
    '''
    actual = defaultdict(dict)

    # populate the data structure from actual file
    with open(actual_price_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            # ignore invalid lines
            if len(row) >= 3:
                time = int(row[0])
                stock = row[1]
                price = float(row[2])
                actual[time][stock] = price

    # earliest hour of actual prices
    start_time = min(actual.keys())
    # latest hour of actual prices
    end_time = max(actual.keys())


    ''' Data structure for holding stats of 'errors' between
        actual and predicted prices
    
    The outer dict uses 'time' as key. Value is a tuple contains
    the sum of all errors at this hour and the number of all 
    errors at this hour. time -> (sum, num)

    e.g. 
    {
        1: (0.10, 4)
        2: (0.20, 2)
    }
    '''
    stats = defaultdict(lambda: (0.0, 0))

    # scan through predicted file to:
    # 1. find 'matched' stock
    # 2. calculate errors
    # 3. update stats
    with open(predicted_price_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            # ignore invalid lines
            if len(row) >= 3:
                time = int(row[0])
                stock = row[1]
                price = float(row[2])
                # check whether we have a match
                if time in actual and stock in actual[time]:
                    error = abs(price - actual[time][stock]) 
                    s, n = stats[time]
                    stats[time] = (s + error, n + 1)

    ''' Sliding a window for avg_error calculation
    
    Window is from window_start to window_end. By adding 1 to
    window_start and window_end, we are 'sliding' the window.

    total: sum of errors within window
    count: num of errors within window
    first: flag for identifying first window

    In order to calculate 'total' more efficiently, except the
    first window, we will only update the CHANGES to it. Thus 
    we don't need to calculate the sum for middle part of the
    window again.

    e.g.
    ----------------------------------------------------------
    sum(hour_1), sum(hour_2), ... , sum(hour_n), sum(hour_n+1)
         ^                               ^
         |                               |
    window_start                    window_end


    total_for_window_1 = sum(hour_1) + ... + sum(hour_n)

    ----------------------------------------------------------

    sum(hour_1), sum(hour_2), ... , sum(hour_n), sum(hour_n+1)
                      ^                               ^
                      |                               |
                 window_start                    window_end


    total_for_window_2 = sum(hour_2) + ... + sum(hour_n+1)

                       = total_for_window_1
                           + sum(hour_n+1) - sum(hour_1)
    ----------------------------------------------------------
    
    The calculation of 'count' is similar to 'total'.

    Finally avg_error of each window can be calculated by
     total / count.
    '''
    window_start = start_time
    window_end = window_start + window_size - 1
    total = 0
    count = 0
    first = True
    with open(output_file, 'w') as file:
        while window_end <= end_time:
            if first:
                # for first window, we have to add them up one by one
                for time in range(window_start, window_end+1):
                    total += stats[time][0]
                    count += stats[time][1]
                first = False
            else:
                # for following windows, we only need to add the diff
                total += stats[window_end][0] - stats[window_start-1][0]
                count += stats[window_end][1] - stats[window_start-1][1]
            
            if count > 0:
                # if at least we have one value in this window
                file.write(str(window_start) + '|' \
                    + str(window_end) + '|' + '%.2f' % (total/count) + '\n')
            else:
                # if no value in this window, we output 'NA'
                file.write(str(window_start) + '|' \
                    + str(window_end) + '|NA\n')

            # moving the window    
            window_start += 1
            window_end += 1

if __name__ == "__main__":

    # parse external arguments for input/output file names
    parser = argparse.ArgumentParser()

    parser.add_argument('--actual', '-a',
        metavar='ACTUAL_PRICE_FILE', help='actual price file', required=True)

    parser.add_argument('--predicted', '-p',
        metavar='PREDICITED_PRICE_FILE', help='predicted price file', required=True)

    parser.add_argument('--window', '-w',
        metavar='WINDOW_SIZE_FILE', help='window size file', required=True)

    parser.add_argument('--output', '-o',
        metavar='OUTPUT_FILE', help='comparison result file', default='.')

    args = parser.parse_args()

    # invoke main function
    main(args.actual, args.predicted, args.window, args.output)