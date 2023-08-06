import numpy as np
import cv2
import joblib

from .utils import (
    ctcBestPath,
    platesRecognitionConfForumla,
    softmax,
    tfBeamSearch,
)


class ModelHelpers:
    def __init__(self, config) -> None:
        print(f"\nLPR Initializer Starting")

        self.config = config
        self.model_name = self.config.model_name
        self.input_size = self.config.input_size
        self.backend = self.config.backend

        try:
            self.characters_dict = joblib.load(self.config.characters_dict)
        except:
            self.characters_dict = (
                open(self.config.characters_dict).read().strip().split("\n")
            )

        try:
            self.regions_dict = joblib.load(self.config.regions_dict)
        except:
            self.regions_dict = (
                open(self.config.regions_dict).read().strip().split("\n")
            )

        try:
            self.colors_dict = joblib.load(self.config.colors_dict)
        except:
            self.colors_dict = open(self.config.colors_dict).read().strip().split("\n")

        if "decode_type" in self.config.keys():
            if self.config.decode_type == "greedy":
                self.ocr_decode = ctcBestPath
            elif self.config.decode_type == "beam_search":
                self.ocr_decode = tfBeamSearch
            else:
                self.ocr_decode = ctcBestPath
        else:
            self.ocr_decode = ctcBestPath

        if "ocr_activation" in self.config.keys():
            self.ocr_activation = self.config.ocr_activation
        else:
            self.ocr_activation = "softmax"

        if "region_activation" in self.config.keys():
            self.region_activation = self.config.region_activation
        else:
            self.region_activation = "softmax"

        if "color_activation" in self.config.keys():
            self.color_activation = self.config.color_activation
        else:
            self.color_activation = "softmax"

        try:
            self.mean = joblib.load(self.config.mean)
        except:
            self.mean = self.config.mean

        try:
            self.var = joblib.load(self.config.var)
        except:
            self.var = self.config.var

        self.max_length = self.config.max_length

        print("\nLPR Successfully Initialized")

    def preprocess(self, image):
        assert len(image.shape) == 3, "Wrong input dimensions"
        if image.shape[-1] > 3:
            image = image[:, :, :-1]

        return (
            cv2.resize(image, (self.input_size.width, self.input_size.height)).astype(
                np.float32
            )[np.newaxis]
            - self.mean
        ) / self.var

    # A utility function to decode the output of the network

    def postprocess(self, pred):
        if len(pred) == 3:
            ocr_pred, region_pred, color_pred = pred
        else:
            raise AssertionError("Number of outputs mismatch any of possible options")

        output_text = []
        output_region = []
        output_color = []

        if self.ocr_activation == "softmax":
            pass
        else:
            raise NotImplementedError

        if self.region_activation == "softmax":
            pass
        elif self.region_activation == "linear":
            region_pred = softmax(region_pred)
        else:
            raise NotImplementedError

        if self.color_activation == "softmax":
            pass
        elif self.color_activation == "linear":
            color_pred = softmax(color_pred)
        else:
            raise NotImplementedError

        plate_text, plate_text_confidence = self.ocr_decode(
            ocr_pred[0], self.characters_dict
        )

        plate_text = plate_text.strip().replace("[UNK]", "")

        plate_region = self.regions_dict[np.argmax(region_pred[0])]
        plate_region_confidence = max(
            0, (1 - sum(sorted(region_pred[0])[:-1]) / region_pred[0].max())
        )

        plate_color = self.colors_dict[np.argmax(color_pred[0])]
        plate_color_confidence = max(
            0, (1 - sum(sorted(color_pred[0])[:-1]) / color_pred[0].max())
        )

        output_text = plate_text
        output_region = plate_region
        output_color = plate_color

        overall_conf = platesRecognitionConfForumla(
            plateTextConf=plate_text_confidence,
            plateRegionConf=plate_region_confidence,
            plateColorConf=plate_color_confidence,
        )

        return (
            output_text,
            output_region,
            output_color,
            overall_conf,
        )

    def run(self, image):
        processed_image = self.preprocess(image)
        predictions = self.infer(processed_image)
        output = self.postprocess(predictions)
        return output
