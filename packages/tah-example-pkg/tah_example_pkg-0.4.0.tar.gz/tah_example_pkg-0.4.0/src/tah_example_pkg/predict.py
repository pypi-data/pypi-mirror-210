import argparse
import os
import cv2
from onnx_base import PPSEG_ONNX
import filetype


def ArgParser():
    parser = argparse.ArgumentParser(
        description="Make prediction using converted .ONNX model."
    )

    # Add the arguments
    parser.add_argument(
        "--input_onnx_model",
        type=str,
        action="store",
        required="true",
        help="the path to onnx model",
    )
    parser.add_argument(
        "--output_preds",
        type=str,
        action="store",
        required="true",
        help="the path to output predections",
    )

    # Execute the parse_args() method
    return parser.parse_args()


def Predict(input_onnx_path, output_preds_path):
    # defined by operations
    directory = "./data/verify_data/"

    ppseg = PPSEG_ONNX(input_onnx_path)

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file

        if os.path.isfile(f):
            if not filetype.is_image(f):
                continue
            f_name, file_extension = os.path.splitext
            output_file = open(f"{output_preds_path}/{f_name}.txt", "w")
            test_img_path = f

            output = ppseg.predict(test_img_path)
            output_line = str(output) + "\n"
            output_file.write(output_line)
            output_file.close()


def main():
    args = ArgParser()
    input_onnx_path, output_preds_path = args.input_onnx_model, args.output_preds
    try:
        Predict(input_onnx_path, output_preds_path)
        print("Prediction is done successfully!")
    except Exception as e:
        print("An exception occurred during prediction!")
        print(e)


if __name__ == "__main__":
    main()
