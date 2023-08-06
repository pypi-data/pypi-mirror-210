import os

os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch

torch.use_deterministic_algorithms(False)

import glob
import subprocess

import cv2
import numpy as np
import torch
from autodistill.base_models import BaseModel
from autodistill.ontology import ClassDescriptionOntology
from supervision import DetectionDataset
from tqdm import tqdm

from autodistill_grounded_sam.helpers import (
    combine_detections,
    load_grounding_dino,
    load_SAM,
    split_data,
)

HOME = os.path.expanduser("~")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class GroundedSAM(BaseModel):
    def __init__(self, ontology, box_threshold=0.35, text_threshold=0.25):
        super().__init__(ontology=ontology)

        self.grounding_dino_model = load_grounding_dino()
        self.sam_predictor = load_SAM()
        self.box_threshold = box_threshold
        self.text_threshold = text_threshold

    def create_ontology(self, ontology):
        return ClassDescriptionOntology(ontology)

    def predict(self, img_path):
        # image: cv2 image

        image = cv2.imread(img_path)

        # GroundingDINO predictions
        detections_list = []

        for i, description in enumerate(self.ontology.descriptions):
            # detect objects
            detections = self.grounding_dino_model.predict_with_classes(
                image=image,
                classes=[description],
                box_threshold=self.box_threshold,
                text_threshold=self.text_threshold,
            )

            detections_list.append(detections)

        detections = combine_detections(
            detections_list, overwrite_class_ids=range(len(detections_list))
        )

        # SAM Predictions
        xyxy = detections.xyxy

        self.sam_predictor.set_image(image)
        result_masks = []
        for box in xyxy:
            masks, scores, logits = self.sam_predictor.predict(
                box=box, multimask_output=False
            )
            index = np.argmax(scores)
            result_masks.append(masks[index])

        detections.mask = np.array(result_masks)

        # separate in supervison to combine detections and override class_ids
        return detections

    def label(self, context_folder, extension=".jpg", output_folder=None):
        if output_folder is None:
            output_folder = context_folder + "_labeled"
        os.makedirs(output_folder, exist_ok=True)

        images_map = {}
        detections_map = {}

        files = glob.glob(context_folder + "/*" + extension)
        progress_bar = tqdm(files, desc="Labeling images")
        # iterate through images in context_folder
        for f_path in progress_bar:
            progress_bar.set_description(desc=f"Labeling {f_path}", refresh=True)
            image = cv2.imread(f_path)

            f_path_short = os.path.basename(f_path)
            images_map[f_path_short] = image.copy()
            detections = self.predict(f_path)
            detections_map[f_path_short] = detections

        dataset = DetectionDataset(
            self.ontology.class_names, images_map, detections_map
        )

        dataset.as_yolo(
            output_folder + "/images",
            output_folder + "/annotations",
            min_image_area_percentage=0.01,
            data_yaml_path=output_folder + "/data.yaml",
        )

        split_data(output_folder)

        print("Labeled dataset created - ready for distillation.")
