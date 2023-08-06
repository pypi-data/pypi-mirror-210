import filetype
import onnxruntime
import cv2
import numpy as np
from .helpers import ModelHelpers
import tritonclient.grpc as grpcclient


class Model:
    def __init__(
        self,
        output_path: str,
        ip: str = None,
        port: str = None,
        onnx_path: str = None,
        triton_model_name: str = None,
    ) -> None:
        self.output_path = output_path
        if (
            ip is not None
            and port is not None
            and triton_model_name is not None
            and onnx_path is None
        ):
            self.mode = "remote"
            self.ip = ip
            self.port = port
            self.triton_model_name = triton_model_name
        elif onnx_path is not None:
            self.mode = "local"
            self.onnx_path = onnx_path
        else:
            raise Exception("You need to provide either IP & port, or onnx path.")

    def predict(self, image_paths:list):
        imgs=[]
        for path in image_paths:
            if filetype.is_image(path):
                imgs.append(cv2.imread(path))
            else:
                raise Exception(f"Image path is not a supported image format.{path}")
        
        helpers = ModelHelpers()
        dim = (1024, 512)
        min_bbox = 2050
        num_classes = 3
        selected_class = 2
        img = helpers.preprocess(imgs, dim)
        print(img.shape)
        
        output = self.__infer(img)
        cls_conf = np.array(output[0])
        model_output = helpers.postprocess(
            cls_conf, dim, min_bbox, num_classes, selected_class
        )
        print(model_output)
        

    def __prepare_session(self):
        if self.mode == "local":
            return onnxruntime.InferenceSession(self.onnx_path, None)
        else:
            try:
                keepalive_options = grpcclient.KeepAliveOptions(
                    keepalive_time_ms=2**31 - 1,
                    keepalive_timeout_ms=20000,
                    keepalive_permit_without_calls=False,
                    http2_max_pings_without_data=2,
                )
                triton_client = grpcclient.InferenceServerClient(
                    url=f"{self.ip}:{self.port}",
                    verbose=False,
                    keepalive_options=keepalive_options,
                )
                # self.model = triton_client
                return triton_client
            except Exception as e:
                raise Exception("Triton connection failed: " + str(e))

    def __infer(self, input):
        session = self.__prepare_session()
        if self.mode == "local":
            ort_inputs = {session.get_inputs()[0].name: input}
            return session.run(None, ort_inputs)
        else:
            inputs = []
            outputs = []

            inputs.append(grpcclient.InferInput("x", [1, 3, 512, 1024], "FP32"))
            inputs[0].set_data_from_numpy(input)

            outputs.append(grpcclient.InferRequestedOutput("softmax_0.tmp_0"))
            results = session.infer(
                model_name=self.triton_model_name,
                inputs=inputs,
                outputs=outputs,
                headers={},
            )
            output = results.as_numpy('softmax_0.tmp_0')
            print(output)
            return output
