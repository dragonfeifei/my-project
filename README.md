# My Solution to Prediction Validation Problem

## Idea:
The key is finding all the matched errors, organizing intermediate stats by time. Then use a sliding window to calculate the final result.

## Aproach:
1. Store all actual prices into a nested dictionary for fast looking up
1. Read predicted prices line by line and match with actual prices
1. If a match is finded, error will be calculated and accumulated in another data structure
1. Maintain a sliding window and calculate the average of errors, write to output file at the same time

## Optimizations:
1. Nested dictionary is used for quickly finding specific stock price at specific hour
1. Specical data structure is used for storing sum of errors and num of errors for specific hour
1. Average errors for one window is calculated based on previous window's results (see comments in source file for details)

## Dependencies:
### Python (following Python Standard Libs are used):
1. argparse: parsing external arguments
1. csv: reading input files
1. defaultdict: data structure

## Run Instructions:
```
./run.sh
```

## Alternative Aproaches:
1. Use Pandas for data joining and windowing (solution can be found in commit history)
1. Maintain two coordinated sliding windows for input files (so we only need to load small portion of data into memory)
