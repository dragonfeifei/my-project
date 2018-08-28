import argparse
import pandas as pd
import numpy as np

def rollBy(what, basis, window, func):
    indexed_what = pd.Series(what.values,index=basis.values)
    def applyToWindow(val):
        indexer = indexed_what.index.slice_indexer(val,val+window-1,1)
        chunk = indexed_what.iloc[indexer]
        return func(chunk)
    rolled = basis.apply(applyToWindow)
    return rolled

def main(actual_price_file, predicted_price_file, window_size_file, output_file):
    window_size = None
    with open(window_size_file, 'r') as file:
        window_size = int(file.read())

    actual_df = pd.read_csv(
        actual_price_file,
        sep='|',
        header=None,
        names=['time', 'stock', 'price'])
    predicted_df = pd.read_csv(
        predicted_price_file,
        sep='|',
        header=None,
        names=['time', 'stock', 'price'])

    actual_df.set_index(['time', 'stock'], inplace=True)
    predicted_df.set_index(['time', 'stock'], inplace=True)

    joined_df = actual_df.join(
        predicted_df, how='left', lsuffix='_actual',rsuffix='_predicted')

    joined_df['error'] = np.abs(
        joined_df['price_actual'] - joined_df['price_predicted'])

    joined_df.reset_index(inplace=True)

    joined_df['avg_error'] = rollBy(
        joined_df['error'], joined_df['time'], window_size, np.mean)

    output_df = joined_df[['time', 'avg_error']]\
        .drop_duplicates().set_index('time')

    output_df = output_df\
        .reindex(range(
            output_df.index.min(), output_df.index.max() - window_size + 2))\
        .reset_index()

    output_df['end_time'] = output_df['time'] + window_size - 1

    output_df[['time', 'end_time', 'avg_error']]\
        .to_csv(
            output_file,
            sep='|',
            header=None,
            index=False,
            na_rep='NA',
            float_format='%.2f')


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
