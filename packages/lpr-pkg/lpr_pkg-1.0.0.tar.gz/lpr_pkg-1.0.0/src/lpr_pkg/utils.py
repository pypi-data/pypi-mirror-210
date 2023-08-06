from itertools import groupby
from typing import Tuple

import Levenshtein as Lev
import numpy as np
import tensorflow as tf


def ctcBestPath(mat: np.ndarray, characters_dict: list) -> Tuple:
    """implements best path decoding as shown by Graves (Dissertation, p63)

    Args:
        mat (2D array):
        characters_dict (dict): dictionary of characters
    Returns:
        res (str): text string
    """

    # get char indices along best path
    best_path = np.argmax(mat, axis=-1)
    confidence = np.mean(np.max(mat, axis=-1))

    # collapse best path (using itertools.groupby),
    # map to chars, join char list to string
    blank_idx = len(characters_dict) - 1
    best_chars_collapsed = [
        (characters_dict)[k] for k, _ in groupby(best_path) if k != blank_idx
    ]
    decoded_string = "".join(best_chars_collapsed)

    return decoded_string, confidence


def tfBeamSearch(
    mat: np.ndarray,
    characters_dict: list,
    n_best: int = 2,
    beam_width: int = 3,
) -> Tuple:
    """Computes best path from model output softmax probabilities using tensorflow.

    Using softmax probabilities, compute n best paths and decodes from a characters dictionary, and ratio OCR confidence.

    Args:
        mat (np.ndarray):
            Probabilities matrix (softmax output), time-major -> (time, classes)
        characters_dict (list):
            Python list containing ordered characters
        n_best (int):
            Top-n paths to be considered
        beam_width (int):
            Beam width of ctc beam search decoder

    Returns:
        textt (string):
            Top scorer decoded text strings
        confidences (float):
            Computed confidence score (not probability)


    """
    paths, scores = tf.nn.ctc_beam_search_decoder(
        np.log(np.transpose(mat[np.newaxis], [1, 0, 2]) + 1e-8),
        [mat.shape[0]],
        beam_width=beam_width,
        top_paths=n_best,
    )
    scores = np.exp(scores.numpy())

    decoded_string = "".join(
        [characters_dict[char_idx] for char_idx in paths[0].values.numpy()]
    ).replace(characters_dict[-2], " ")

    # Ratio OCR confidence formula, https://www.cs.tau.ac.il/~wolf/papers/confidenceinocr.pdf
    confidence = 1 - scores[0, 1] / scores[0, 0]

    return decoded_string, confidence


def platesRecognitionConfForumla(
    plateTextConf: float, plateRegionConf: float, plateColorConf: float
) -> float:
    return (
        plateTextConf**0.8 * plateRegionConf**0.1 * plateColorConf**0.1
    )


def sigmoid(x: float) -> float:
    """calculate sigmoid value of a number

    Args:
        x (float): number

    Returns:
        float: sigmiod value
    """
    return 1.0 / (np.exp(-x) + 1.0)


def softmax(x: np.array, axis: int = -1) -> np.array:
    """calculate softmax of array

    Args:
        x (array): array like

    Returns:
        (array): softmax
    """
    x = np.exp(x) / np.sum(np.exp(x), axis=axis)[..., np.newaxis]
    return x


def batch_calculate_cer_v0(pred_texts, orig_texts):
    def calculate_cer(s1, s2):
        """
        Computes the Character Error Rate, defined as the edit distance.
        Arguments:
                        s1 (string): space-separated sentence (actual)
                        s2 (string): space-separated sentence (predicted)
        """
        return Lev.distance(s1, s2) / len(s1)

    cer = []
    correct_plates = 0
    nearly_correct_plates = 0

    for pred_text, orig_text in zip(pred_texts, orig_texts):
        pred_text = pred_text.strip()
        orig_text = orig_text.strip()

        try:
            plate_cer = calculate_cer(pred_text, orig_text)
        except:
            continue
        cer.append(plate_cer)

        if plate_cer * len(orig_text) <= 1.0:
            nearly_correct_plates += 1
        if pred_text == orig_text:
            correct_plates += 1

    CER = np.mean(cer) * 100
    PER = (1 - correct_plates / len(pred_texts)) * 100
    SPER = (1 - nearly_correct_plates / len(pred_texts)) * 100
    return CER, PER, SPER
