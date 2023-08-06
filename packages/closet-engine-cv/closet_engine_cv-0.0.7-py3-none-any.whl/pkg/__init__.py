import argparse
import cv2
import os
from os.path import join, getsize, basename, splitext
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='Generate diff images')
    parser.add_argument('-x', nargs=1, type=str, required=True)
    parser.add_argument('-y', nargs=1, type=str, required=True)
    parser.add_argument('--diff', nargs=1, type=str, required=True)
    parser.add_argument('--highlight', nargs=1, type=str, required=True)
    parser.add_argument('--combined', nargs=1, type=str, required=True)

    args = parser.parse_args()
    x_path:str = args.x[0]
    y_path:str = args.y[0]
    diff_path:str = args.diff[0]
    highlight_path:str = args.highlight[0]
    combined_path:str = args.combined[0]

    # print(x_path, y_path, diff_path, highlight_path, combined_path)


    x = cv2.imread(x_path)
    y = cv2.imread(y_path)
    diff = cv2.absdiff(x, y)
    res, thres_diff = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY)
    combined = np.concatenate((x, y, diff, thres_diff,), axis=1)

    # x_base = splitext(basename(x_path))[0]
    # y_base = splitext(basename(y_path))[0]
    # y_to_x = y_base + '-' + x_base
    cv2.imwrite(diff_path, diff)
    cv2.imwrite(highlight_path, thres_diff)
    cv2.imwrite(combined_path, combined)
