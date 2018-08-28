import argparse
import csv
from collections import defaultdict

def main(actual_price_file, predicted_price_file, window_size_file, output_file):
    window_size = None
    with open(window_size_file, 'r') as file:
        window_size = int(file.read())

    actual = defaultdict(dict)
    with open(actual_price_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            if len(row) >= 3:
                time = int(row[0])
                stock = row[1]
                price = float(row[2])
                actual[time][stock] = price

    start_time = min(actual.keys())
    end_time = max(actual.keys())

    errors = defaultdict(list)
    with open(predicted_price_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            if len(row) >= 3:
                time = int(row[0])
                stock = row[1]
                price = float(row[2])
                if time in actual and stock in actual[time]:
                    error = abs(price - actual[time][stock])
                    errors[time].append(error)

    window_start = start_time
    window_end = window_start + window_size - 1
    total = 0
    count = 0
    first = True
    with open(output_file, 'w') as file:
        while window_end <= end_time:
            if first:
                for time in range(window_start, window_end+1):
                    total+=sum(errors[time])
                    count+=len(errors[time])
                first = False
            else:
                total += sum(errors[window_end]) - sum(errors[window_start-1])
                count += len(errors[window_end]) - len(errors[window_start-1])
            if count > 0:
                file.write(str(window_start) + '|' \
                    + str(window_end) + '|' + '%.2f' % (total/count) + '\n')
            else:
                file.write(str(window_start) + '|' \
                    + str(window_end) + '|NA\n')
            window_start+=1
            window_end+=1

if __name__ == "__main__":
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
    main(args.actual, args.predicted, args.window, args.output)