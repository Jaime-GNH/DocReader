import os
import sys
import torch


# GLOBAL
LANGUAGE = 'es'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
RESOURCES_DIR = r"../../resources" if getattr(sys, "frozen", False) else ""

# TEXT PROCESSING
TEXT_CONVERSIONS_PATH = os.path.join(RESOURCES_DIR, r"text_conversions.json")

# TEXT TO SPEECH
MODEL_NAMES = ['tts_models/es/css10/vits', 'tts_models/es/mai/tacotron2-DDC']
SPEAKER_DIR = os.path.join(RESOURCES_DIR, r"speakers")
SPEAKERS = ["Default"] + [s.split('.')[0] for s in os.listdir(SPEAKER_DIR)]
MODEL_SAMPLE_RATE_OUT = 24000
