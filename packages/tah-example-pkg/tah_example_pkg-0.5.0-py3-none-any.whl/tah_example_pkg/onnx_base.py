import onnxruntime 
import cv2
import numpy as np

class PPSEG_ONNX:
    def __init__(self, model_weights_path):
        self.session = onnxruntime.InferenceSession(model_weights_path, None)
        self.input_name = self.session.get_inputs()[0].name
        
    def normalize(self,img, mean, std):
        img = img.astype(np.float32, copy=False) / 255.0
        img -= mean
        img /= std
        return img

    def preprocess(self,img,input_shape):
    
        mean=(0.5, 0.5, 0.5)
        std=(0.5, 0.5, 0.5)
        mean = np.array(mean)[np.newaxis, np.newaxis, :]
        std = np.array(std)[np.newaxis, np.newaxis, :]    
        #image normaliztion
        norm_img = self.normalize(img, mean, std)
        #image resize
        resized_img = cv2.resize(norm_img,input_shape, interpolation = cv2.INTER_AREA)
        #convert bgr to rgb:
        rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        #transpose image: nchw
        trs_img = np.transpose(rgb_img, (2, 0, 1))  
        #expand dimension
        preprocessed_img = trs_img[np.newaxis, ...]  
        return preprocessed_img

    def postprocess(self, preds, input_dim, min_bbox, num_classes, class_id):

        dets = []
        #get the logits of the selected class and the background class
        selected_cls_scores = preds[0,class_id,:,:]
        bg_cls_scores = preds[0,0,:,:]

        #get the segmentation values across the 3 logits channels [0:bg, 1:asphalt, 2:sand]
        segments = np.argmax(preds, axis=1)
        segments = np.array(segments[0])
        segments = segments.astype('int32')
        print('1')

        #get the total number of pixels per each class and assign the missed classes to zero
        pixels_per_cls = np.unique(segments,return_counts=True)
        pixels_per_cls_dict = dict(zip(pixels_per_cls[0],pixels_per_cls[1]))
        classes = np.array([*range(num_classes)]).astype('int32')
        print('2')
        missed_classes = list( set(classes) - set(list(pixels_per_cls_dict.keys())) )
        for missed_class in missed_classes:
            pixels_per_cls_dict[missed_class] = 0
        
        #get the total number of pixels per the region of interest [sand pixels and asphalt pixels],required for the selected class ratio
        roi_classes = list(set(list(pixels_per_cls_dict.keys())) - set([0]))
        roi_values = sum(value for key,value in pixels_per_cls_dict.items() if key in roi_classes)

        #build a binary image with the pixels of the only selected class to find its contours
        fg_pixels = np.where(segments != class_id, 0, segments)*56
        contour_image = np.stack((fg_pixels,fg_pixels,fg_pixels),-1)
        contour_image = contour_image.astype('uint8')
        print('3')
        contour_image_ = cv2.cvtColor(contour_image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(contour_image_, 50, 250, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        #convert the contours to bounding boxes if they are larger than certain size and find the ratio and confidence of the contour
        for contour in contours:
            contour_score = 0
            
            x_2 = np.min([np.max(contour[:,:,0]),input_dim[0]])
            y_2 = np.min([np.max(contour[:,:,1]),input_dim[1]])
            x_1 = np.max([np.min(contour[:,:,0]),0])
            y_1 = np.max([np.min(contour[:,:,1]),0])
            print('4')
            rect_area = np.abs(x_2-x_1) * np.abs(y_2-y_1)
            if rect_area >= min_bbox:
                for i in range(len(contour)):
                    y,x = contour[i][0]
                    score = selected_cls_scores[x,y]+bg_cls_scores[x,y]
                    contour_score += score   

                contour_score = round(contour_score/len(contour),2)
                contour_area = cv2.contourArea(contour)
                contour_ratio = round(contour_area/roi_values,2)
                #det = [x_1,y_1,x_2,y_2,contour_score,contour_ratio,class_id]
                dets.append(contour_score)
            print('done')
        return dets

    def predict(self, image_path):

        dim = (1024,512)
        min_bbox = 2050
        num_classes = 3
        selected_class = 2

        image = cv2.imread(image_path)
        img = self.preprocess(image,dim)
        ort_inputs = {self.input_name : img}
        output = self.session.run(None, ort_inputs)
        cls_conf = np.array(output[0])
        model_output = self.postprocess(cls_conf,dim,min_bbox,num_classes,selected_class)
        print(model_output)
        return model_output
        