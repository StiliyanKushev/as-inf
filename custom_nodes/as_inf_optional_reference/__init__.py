"""A single ComfyUI image input that can explicitly select no reference."""

from __future__ import annotations

import os

import comfy.model_management
import folder_paths
import nodes
import torch


NONE = "[None — prompt-only mode]"


class OptionalReferenceImage(nodes.LoadImage):
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [
            name
            for name in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, name))
        ]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {
            "required": {
                "image": ([NONE, *sorted(files)], {"image_upload": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("image", "mask", "has_reference")
    FUNCTION = "load_optional_image"
    CATEGORY = "AS-INF/inputs"
    DESCRIPTION = (
        "Select None for prompt-only generation, or select/upload an image to "
        "enable all reference-conditioned branches automatically."
    )

    def load_optional_image(self, image):
        if image == NONE:
            dtype = comfy.model_management.intermediate_dtype()
            device = comfy.model_management.intermediate_device()
            neutral = torch.full(
                (1, 64, 64, 3), 96.0 / 255.0, dtype=dtype, device=device
            )
            mask = torch.zeros((1, 64, 64), dtype=dtype, device=device)
            return neutral, mask, False

        loaded, mask = super().load_image(image)
        return loaded, mask, True

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if image == NONE:
            return True
        return super().VALIDATE_INPUTS(image)

    @classmethod
    def IS_CHANGED(cls, image):
        if image == NONE:
            return "prompt-only"
        return super().IS_CHANGED(image)


NODE_CLASS_MAPPINGS = {"ASInfOptionalReferenceImage": OptionalReferenceImage}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ASInfOptionalReferenceImage": "Optional Reference Image"
}

