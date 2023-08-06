import filetype
import onnxruntime
import cv2
import numpy as np
from .helpers import ModelHelpers


class Model:
    def __init__(
        self, output_path: str, ip: str = None, port: str = None, onnx_path: str = None
    ) -> None:
        self.output_path = output_path
        if ip is not None and port is not None and onnx_path is None:
            self.mode = "remote"
            self.ip = ip
            self.port = port
        elif onnx_path is not None:
            self.mode = "local"
            self.onnx_path = onnx_path
        else:
            raise Exception("You need to provide either IP & port, or onnx path.")

    def predict(self, image_path: str):
        if filetype.is_image(image_path):
            session = self.__prepare_session()
            helpers = ModelHelpers()

            dim = (1024, 512)
            min_bbox = 2050
            num_classes = 3
            selected_class = 2
            image = cv2.imread(image_path)

            img = helpers.preprocess(image, dim)
            print(img.shape)
            ort_inputs = {session.get_inputs()[0].name: img}
            output = session.run(None, ort_inputs)
            cls_conf = np.array(output[0])
            model_output = helpers.postprocess(
                cls_conf, dim, min_bbox, num_classes, selected_class
            )
            
            print(model_output)
        else:
            raise Exception("Image path is not a supported image format.")

    def __prepare_session(self):
        if self.mode == "local":
            return onnxruntime.InferenceSession(self.onnx_path, None)
        else:
            pass
