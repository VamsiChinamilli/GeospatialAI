# WeatherB/core_next/utils/model_loader.py

"""
Model Loader
============

Centralised loader for trained AI models used by the
Urban Climate Analysis backend.

Current Architecture
--------------------

1. Land Cover
   -> U-Net
   -> PyTorch checkpoint hosted on Hugging Face Hub

2. Land Surface Temperature (LST)
   -> Expert System
   -> No LST neural-network checkpoint

Responsibilities
----------------

1. Download/load the Land Cover U-Net checkpoint from
   Hugging Face Hub.
2. Keep the model cached in memory.
3. Ensure the model is loaded in evaluation mode.
4. Keep model-loading logic separate from inference logic.

Important
---------

The LST neural model has been removed from the active
architecture and must NOT be loaded here.
"""


import torch

from huggingface_hub import hf_hub_download

from core_next.utils.unet.model import UNet


# =======================================================
# HUGGING FACE MODEL CONFIGURATION
# =======================================================

HF_REPO_ID = "naga-vamsi/weatherb-landcover-unet"

HF_MODEL_FILENAME = "best_model.pth"


# =======================================================
# MODEL LOADER
# =======================================================

class ModelLoader:

    """
    Central model registry.

    The Land Cover U-Net is downloaded from Hugging Face
    only when it is not already available in the local
    Hugging Face cache.

    Once loaded, the PyTorch model is kept in memory so
    it is NOT loaded again for every API request.
    """

    _unet = None

    # ===================================================
    # DEVICE
    # ===================================================

    @staticmethod
    def get_device():

        return torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    # ===================================================
    # DOWNLOAD / RESOLVE CHECKPOINT
    # ===================================================

    @staticmethod
    def _get_checkpoint_path():

        """
        Get the Land Cover U-Net checkpoint from
        Hugging Face Hub.

        hf_hub_download() handles local caching.

        If the model is already cached on this machine,
        Hugging Face reuses the cached file instead of
        downloading the 295 MB checkpoint again.

        Returns
        -------
        str
            Local path to the cached checkpoint.
        """

        print(
            "\nResolving Land Cover U-Net checkpoint..."
        )

        print(
            "Hugging Face repository:",
            HF_REPO_ID
        )

        print(
            "Model file:",
            HF_MODEL_FILENAME
        )

        checkpoint_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_MODEL_FILENAME,
        )

        print(
            "Checkpoint available at:",
            checkpoint_path
        )

        return checkpoint_path

    # ===================================================
    # EXTRACT STATE DICT
    # ===================================================

    @staticmethod
    def _extract_state_dict(checkpoint):

        """
        Supports both:

        1. Full training checkpoint

           {
               "epoch": ...,
               "model": ...,
               "optimizer": ...,
               "metrics": ...
           }

        2. Raw model state_dict
        """

        if isinstance(checkpoint, dict):

            if "model" in checkpoint:

                return checkpoint["model"]

            if all(
                isinstance(key, str)
                for key in checkpoint.keys()
            ):

                return checkpoint

        raise RuntimeError(
            "Unsupported model checkpoint format."
        )

    # ===================================================
    # LAND COVER U-NET
    # ===================================================

    @classmethod
    def load_unet(cls):

        """
        Load the Land Cover segmentation U-Net.

        Input:
            5 channels
            256 x 256

        Output:
            11 classes
            256 x 256

        Returns:
            UNet
        """

        # ------------------------------------------------
        # Already loaded?
        # ------------------------------------------------

        if cls._unet is not None:

            return cls._unet

        # ------------------------------------------------
        # Device
        # ------------------------------------------------

        device = cls.get_device()

        print(
            "\n=============================================="
        )

        print(
            "Loading Land Cover U-Net"
        )

        print(
            "=============================================="
        )

        print(
            "Device:",
            device
        )

        # ------------------------------------------------
        # Resolve checkpoint from Hugging Face
        # ------------------------------------------------

        checkpoint_path = cls._get_checkpoint_path()

        # ------------------------------------------------
        # Architecture must exactly match training
        # ------------------------------------------------

        model = UNet(
            in_channels=5,
            num_classes=11,
            pretrained=False
        )

        # ------------------------------------------------
        # Load checkpoint
        # ------------------------------------------------

        checkpoint = torch.load(
            checkpoint_path,
            map_location=device
        )

        state_dict = cls._extract_state_dict(
            checkpoint
        )

        # ------------------------------------------------
        # Load trained weights
        # ------------------------------------------------

        model.load_state_dict(
            state_dict
        )

        # ------------------------------------------------
        # Move model to device
        # ------------------------------------------------

        model = model.to(device)

        # ------------------------------------------------
        # Evaluation mode
        # ------------------------------------------------

        model.eval()

        # ------------------------------------------------
        # Cache model in memory
        # ------------------------------------------------

        cls._unet = model

        print(
            "✓ Land Cover U-Net loaded successfully."
        )

        print(
            "=============================================="
        )

        return cls._unet

    # ===================================================
    # LOAD ALL ACTIVE AI MODELS
    # ===================================================

    @classmethod
    def load_all(cls):

        """
        Load every neural model required by the
        current climate-analysis pipeline.

        Current active neural model:

            {
                "unet": Land Cover U-Net
            }

        LST is handled by the Expert System and therefore
        is intentionally NOT loaded here.
        """

        return {
            "unet": cls.load_unet()
        }

    # ===================================================
    # CLEAR CACHE
    # ===================================================

    @classmethod
    def clear(cls):

        """
        Remove cached models from memory.

        Useful during development/testing or when
        reloading updated checkpoints.
        """

        cls._unet = None

        if torch.cuda.is_available():

            torch.cuda.empty_cache()