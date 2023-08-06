import argparse
import os 

def ArgParser():
    parser = argparse.ArgumentParser(description='Evaluate predictions using converted .ONNX model.')
    # Add the arguments
    parser.add_argument('--model_preds', type=str, action='store', required='true', help='the path to model predictions')
    parser.add_argument('--gt', type=str, action='store', required='true', help='the path to output predections')
    parser.add_argument('--output_metrics', type=str, action='store', required='true', help='the path to output metrics location')

    # Execute the parse_args() method
    return parser.parse_args()

def Evaluate(model_preds_path, gt_path, output_metrics_path):

    os.makedirs(output_metrics_path, exist_ok=True)  
    f = open(output_metrics_path+"/accuracy.txt" , "w")

    gt_score = 0
    print('0')
    gt_labels_file = open(gt_path)
    print('1')
    gt_labels = gt_labels_file.read()
    gt_labels = ((gt_labels.strip().split('[')[-1]).split(']')[0]).split(',')
    for gt_label in gt_labels:
        gt_score += float(gt_label)
    gt_score /= len(gt_labels)

    pred_score = 0
    pred_labels_file = open(model_preds_path)
    pred_labels = pred_labels_file.read()
    pred_labels = ((pred_labels.strip().split('[')[-1]).split(']')[0]).split(',')
    for pred_label in pred_labels:
        pred_score += float(pred_label)
    pred_score /= len(pred_labels)

    acc = 100 - abs(pred_score-gt_score)
    f.write(str(acc))

def main():
    args = ArgParser()
    model_preds_path, gt_path, output_metrics_path = args.model_preds, args.gt, args.output_metrics
    
    try:
        Evaluate(model_preds_path, gt_path, output_metrics_path)
        print("Evaluation is done successfully!")
    except Exception as e:
        print("An exception occurred during Evaluation!")
        print(e)


if __name__ == '__main__':
    main()
    