import onnxruntime
import cv2
import numpy as np
from .helpers import ModelHelpers
import tritonclient.grpc as grpcclient
import glob
import os
from easydict import EasyDict
import json


class Model:
    def __init__(
        self,
        output_path: str,
        ip: str = None,
        port: str = None,
        onnx_path: str = None,
        triton_model_name: str = None,
        config_file: str = None,
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

        self.config = EasyDict(json.load(open(config_file)))

    def predict(self, images_directory: str):
        os.system("rm -dr {}".format(self.output_path))
        os.system("mkdir -p {}".format(self.output_path))

        image_names = sorted(glob.glob("{}/*.*g".format(images_directory)))

        helpers = ModelHelpers(self.config)
        for image_name in image_names:
            image = cv2.cvtColor(cv2.imread(image_name), cv2.COLOR_BGR2RGB)

            if image.shape[0] * image.shape[1] < 64 * 64:
                continue

            processed_image = helpers.preprocess(image)
            predictions = self.infer(processed_image)
            plate_number, plate_region, plate_color, _ = helpers.postprocess(
                predictions
            )

            print(plate_number, plate_region, plate_color)
            pred_file = open(
                "{}/{}.txt".format(self.output_path, image_name.split("/")[-1][:-4]),
                "w",
            )
            pred_file.write(
                "{}\n{}\n{}".format(
                    plate_number.replace("_", " ").strip(), plate_region, plate_color
                )
            )
            pred_file.close()

    def __prepare_session(self):
        if self.mode == "local":
            print(f"Loading LPR using ONNX backend")
            so = onnxruntime.SessionOptions()
            so.graph_optimization_level = (
                onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
            )
            so.intra_op_num_threads = 1
            so.inter_op_num_threads = 1
            so.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL

            if self.config.backend == "openvino":
                providers = ["OpenVINOExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]
            return onnxruntime.InferenceSession(
                self.onnx_path, sess_options=so, providers=providers
            )
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
                return triton_client
            except Exception as e:
                raise Exception("Triton connection failed: " + str(e))

    def infer(self, input):
        session = self.__prepare_session()
        if self.mode == "local":
            ort_inputs = {session.get_inputs()[0].name: input}
            return session.run(None, ort_inputs)
        else:
            inputs = []
            outputs = []
            print(input.shape)
            inputs.append(grpcclient.InferInput("image", [1,96, 144, 3], "FP32"))
            inputs[0].set_data_from_numpy(input)
            print(input.shape)

            outputs.append(grpcclient.InferRequestedOutput("OCR_Output"))
            outputs.append(grpcclient.InferRequestedOutput("Region_Output"))
            outputs.append(grpcclient.InferRequestedOutput("Color_Output"))
            results = session.infer(
                model_name=self.triton_model_name,
                inputs=inputs,
                outputs=outputs,
                headers={},
            )
            ocr_pred = results.as_numpy("OCR_Output")
            region_pred = results.as_numpy("Region_Output")
            color_pred = results.as_numpy("Color_Output")
            output = (ocr_pred, region_pred, color_pred)
            print(output)
            # ocr_pred, region_pred, color_pred
            return output
