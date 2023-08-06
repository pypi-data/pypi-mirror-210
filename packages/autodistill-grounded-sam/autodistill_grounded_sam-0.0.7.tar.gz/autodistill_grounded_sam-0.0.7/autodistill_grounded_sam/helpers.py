import os
import random
import shutil
import urllib.request

import numpy as np
import torch
import yaml
from groundingdino.util.inference import Model
from PIL import Image
from segment_anything import SamPredictor, sam_model_registry
from supervision import Detections

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if not torch.cuda.is_available():
    print("WARNING: CUDA not available. GroundingDINO will run very slowly.")


def combine_detections(detections_list, overwrite_class_ids):
    if len(detections_list) == 0:
        return Detections.empty()

    if overwrite_class_ids is not None and len(overwrite_class_ids) != len(
        detections_list
    ):
        raise ValueError(
            "Length of overwrite_class_ids must match the length of detections_list."
        )

    xyxy = []
    mask = []
    confidence = []
    class_id = []
    tracker_id = []

    for idx, detection in enumerate(detections_list):
        xyxy.append(detection.xyxy)

        if detection.mask is not None:
            mask.append(detection.mask)

        if detection.confidence is not None:
            confidence.append(detection.confidence)

        if detection.class_id is not None:
            if overwrite_class_ids is not None:
                # Overwrite the class IDs for the current Detections object
                class_id.append(
                    np.full_like(
                        detection.class_id, overwrite_class_ids[idx], dtype=np.int64
                    )
                )
            else:
                class_id.append(detection.class_id)

        if detection.tracker_id is not None:
            tracker_id.append(detection.tracker_id)

    xyxy = np.vstack(xyxy)
    mask = np.vstack(mask) if mask else None
    confidence = np.hstack(confidence) if confidence else None
    class_id = np.hstack(class_id) if class_id else None
    tracker_id = np.hstack(tracker_id) if tracker_id else None

    return Detections(
        xyxy=xyxy,
        mask=mask,
        confidence=confidence,
        class_id=class_id,
        tracker_id=tracker_id,
    )


def load_grounding_dino():
    AUTODISTILL_CACHE_DIR = os.path.expanduser("~/.cache/autodistill")

    GROUDNING_DINO_CACHE_DIR = os.path.join(AUTODISTILL_CACHE_DIR, "groundingdino")

    GROUNDING_DINO_CONFIG_PATH = os.path.join(
        GROUDNING_DINO_CACHE_DIR, "GroundingDINO_SwinT_OGC.py"
    )
    GROUNDING_DINO_CHECKPOINT_PATH = os.path.join(
        GROUDNING_DINO_CACHE_DIR, "groundingdino_swint_ogc.pth"
    )

    try:
        print("trying to load grounding dino directly")
        grounding_dino_model = Model(
            model_config_path=GROUNDING_DINO_CONFIG_PATH,
            model_checkpoint_path=GROUNDING_DINO_CHECKPOINT_PATH,
            device=DEVICE,
        )
        return grounding_dino_model
    except Exception:
        print("downloading dino model weights")
        if not os.path.exists(GROUDNING_DINO_CACHE_DIR):
            os.makedirs(GROUDNING_DINO_CACHE_DIR)

        if not os.path.exists(GROUNDING_DINO_CHECKPOINT_PATH):
            url = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
            urllib.request.urlretrieve(url, GROUNDING_DINO_CHECKPOINT_PATH)

        if not os.path.exists(GROUNDING_DINO_CONFIG_PATH):
            url = "https://raw.githubusercontent.com/roboflow/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py"
            urllib.request.urlretrieve(url, GROUNDING_DINO_CONFIG_PATH)

        grounding_dino_model = Model(
            model_config_path=GROUNDING_DINO_CONFIG_PATH,
            model_checkpoint_path=GROUNDING_DINO_CHECKPOINT_PATH,
            device=DEVICE,
        )

        # grounding_dino_model.to(DEVICE)

        return grounding_dino_model


def load_SAM():
    # Check if segment-anything library is already installed

    AUTODISTILL_CACHE_DIR = os.path.expanduser("~/.cache/autodistill")
    SAM_CACHE_DIR = os.path.join(AUTODISTILL_CACHE_DIR, "segment_anything")
    SAM_CHECKPOINT_PATH = os.path.join(SAM_CACHE_DIR, "sam_vit_h_4b8939.pth")

    url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"

    # Create the destination directory if it doesn't exist
    os.makedirs(os.path.dirname(SAM_CHECKPOINT_PATH), exist_ok=True)

    # Download the file if it doesn't exist
    if not os.path.isfile(SAM_CHECKPOINT_PATH):
        urllib.request.urlretrieve(url, SAM_CHECKPOINT_PATH)

    SAM_ENCODER_VERSION = "vit_h"

    sam = sam_model_registry[SAM_ENCODER_VERSION](checkpoint=SAM_CHECKPOINT_PATH).to(
        device=DEVICE
    )
    sam_predictor = SamPredictor(sam)

    return sam_predictor


def split_data(base_dir, split_ratio=0.8):
    images_dir = os.path.join(base_dir, "images")
    annotations_dir = os.path.join(base_dir, "annotations")

    # Correct the image file names if they have an extra dot before the extension
    for file in os.listdir(images_dir):
        if file.count(".") > 1:
            new_file_name = file.replace("..", ".")
            os.rename(
                os.path.join(images_dir, file), os.path.join(images_dir, new_file_name)
            )

    # Convert .png and .jpeg images to .jpg
    for file in os.listdir(images_dir):
        if file.endswith(".png"):
            img = Image.open(os.path.join(images_dir, file))
            rgb_img = img.convert("RGB")
            rgb_img.save(os.path.join(images_dir, file.replace(".png", ".jpg")))
            os.remove(os.path.join(images_dir, file))
        if file.endswith(".jpeg"):
            img = Image.open(os.path.join(images_dir, file))
            rgb_img = img.convert("RGB")
            rgb_img.save(os.path.join(images_dir, file.replace(".jpeg", ".jpg")))
            os.remove(os.path.join(images_dir, file))

    # Get list of all files (removing the image file extension)
    all_files = os.listdir(images_dir)
    all_files = [os.path.splitext(f)[0] for f in all_files if f.endswith(".jpg")]

    # Shuffle the files
    random.shuffle(all_files)

    # Compute the splitting index
    split_idx = int(len(all_files) * split_ratio)

    # Split the files
    train_files = all_files[:split_idx]
    valid_files = all_files[split_idx:]

    # Make directories for train and valid
    train_dir = os.path.join(base_dir, "train")
    valid_dir = os.path.join(base_dir, "valid")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(valid_dir, exist_ok=True)

    # Make images and labels subdirectories
    train_images_dir = os.path.join(train_dir, "images")
    train_labels_dir = os.path.join(train_dir, "labels")
    valid_images_dir = os.path.join(valid_dir, "images")
    valid_labels_dir = os.path.join(valid_dir, "labels")
    os.makedirs(train_images_dir, exist_ok=True)
    os.makedirs(train_labels_dir, exist_ok=True)
    os.makedirs(valid_images_dir, exist_ok=True)
    os.makedirs(valid_labels_dir, exist_ok=True)

    # Move the files
    for file in train_files:
        shutil.move(os.path.join(images_dir, file + ".jpg"), train_images_dir)
        shutil.move(os.path.join(annotations_dir, file + ".txt"), train_labels_dir)

    for file in valid_files:
        shutil.move(os.path.join(images_dir, file + ".jpg"), valid_images_dir)
        shutil.move(os.path.join(annotations_dir, file + ".txt"), valid_labels_dir)

    # Load the existing YAML file to get the names
    with open(os.path.join(base_dir, "data.yaml"), "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        names = data["names"]

    # Rewrite the YAML file
    with open(os.path.join(base_dir, "data.yaml"), "w") as file:
        data = {
            "train": os.path.abspath(base_dir) + "/train/images",
            "val": os.path.abspath(base_dir) + "/valid/images",
            "nc": len(names),
            "names": names,
        }
        yaml.dump(data, file)
