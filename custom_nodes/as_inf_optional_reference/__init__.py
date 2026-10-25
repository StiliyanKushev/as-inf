"""Optional reference inputs used by the AS-INF workflows."""

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


class OptionalReferenceCrop3x4(OptionalReferenceImage):
    """Optional image loader with a visually selected, fixed 3:4 crop.

    The browser extension stores the rectangle as normalized coordinates. The
    backend enforces 3:4 once more so API calls and hand-edited workflows cannot
    accidentally stretch or pad the reference.
    """

    @classmethod
    def INPUT_TYPES(cls):
        image_input = super().INPUT_TYPES()["required"]["image"]
        hidden_crop = {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.0001}
        hidden_size = {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.0001}
        return {
            "required": {
                "image": image_input,
                "crop_x": ("FLOAT", hidden_crop),
                "crop_y": ("FLOAT", hidden_crop),
                "crop_w": ("FLOAT", hidden_size),
                "crop_h": ("FLOAT", hidden_size),
            }
        }

    FUNCTION = "load_optional_crop"
    DESCRIPTION = (
        "Select None for prompt-only generation, or choose an image and move "
        "or zoom the fixed 3:4 crop rectangle. Crop coordinates stay hidden."
    )

    @staticmethod
    def _crop_box(width, height, crop_x, crop_y, crop_w, crop_h):
        x0 = max(0, min(width - 1, round(float(crop_x) * width)))
        y0 = max(0, min(height - 1, round(float(crop_y) * height)))
        x1 = max(x0 + 1, min(width, round((float(crop_x) + float(crop_w)) * width)))
        y1 = max(y0 + 1, min(height, round((float(crop_y) + float(crop_h)) * height)))

        # Select the largest exact 3:4 integer rectangle inside the requested
        # area and keep it centered. This is crop-only: no padding or stretch.
        units = min((x1 - x0) // 3, (y1 - y0) // 4)
        if units < 1:
            units = min(width // 3, height // 4)
            x0, y0, x1, y1 = 0, 0, width, height
        crop_width, crop_height = 3 * units, 4 * units
        left = x0 + ((x1 - x0) - crop_width) // 2
        top = y0 + ((y1 - y0) - crop_height) // 2
        return left, top, left + crop_width, top + crop_height

    @staticmethod
    def _crop_mask(mask, image_width, image_height, box):
        _, mask_height, mask_width = mask.shape
        left, top, right, bottom = box
        mx0 = max(0, min(mask_width - 1, round(left * mask_width / image_width)))
        my0 = max(0, min(mask_height - 1, round(top * mask_height / image_height)))
        mx1 = max(mx0 + 1, min(mask_width, round(right * mask_width / image_width)))
        my1 = max(my0 + 1, min(mask_height, round(bottom * mask_height / image_height)))
        return mask[:, my0:my1, mx0:mx1]

    def load_optional_crop(self, image, crop_x, crop_y, crop_w, crop_h):
        if image == NONE:
            dtype = comfy.model_management.intermediate_dtype()
            device = comfy.model_management.intermediate_device()
            neutral = torch.full(
                (1, 64, 48, 3), 96.0 / 255.0, dtype=dtype, device=device
            )
            mask = torch.zeros((1, 64, 48), dtype=dtype, device=device)
            return neutral, mask, False

        loaded, mask = nodes.LoadImage.load_image(self, image)
        _, height, width, _ = loaded.shape
        box = self._crop_box(width, height, crop_x, crop_y, crop_w, crop_h)
        left, top, right, bottom = box
        loaded = loaded[:, top:bottom, left:right, :]
        mask = self._crop_mask(mask, width, height, box)
        return loaded, mask, True

    @classmethod
    def VALIDATE_INPUTS(
        cls, image, crop_x=None, crop_y=None, crop_w=None, crop_h=None
    ):
        return super().VALIDATE_INPUTS(image)

    @classmethod
    def IS_CHANGED(cls, image, crop_x, crop_y, crop_w, crop_h):
        base = super().IS_CHANGED(image)
        return f"{base}|{crop_x!r},{crop_y!r},{crop_w!r},{crop_h!r}"


class LoraLoaderModelOnlyWithTrigger(nodes.LoraLoaderModelOnly):
    """Load a model-only LoRA and emit its activation text when enabled.

    Keeping the trigger output on the same node as the strength prevents the
    prompt and model state from drifting apart: strength zero produces an empty
    string, while any non-zero strength prefixes the configured activation text.
    """

    @classmethod
    def INPUT_TYPES(cls):
        inputs = nodes.LoraLoaderModelOnly.INPUT_TYPES()
        inputs["required"]["trigger_words"] = (
            "STRING",
            {
                "default": "",
                "multiline": True,
                "tooltip": (
                    "Prompt activation text emitted only while this LoRA has "
                    "a non-zero model strength."
                ),
            },
        )
        return inputs

    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "active_trigger_words")
    FUNCTION = "load_lora_model_only_with_trigger"
    CATEGORY = "AS-INF/model"
    DESCRIPTION = (
        "Loads a model-only LoRA and emits its configured trigger words only "
        "when the LoRA strength is non-zero."
    )

    def load_lora_model_only_with_trigger(
        self, model, lora_name, strength_model, trigger_words
    ):
        loaded_model = super().load_lora_model_only(
            model, lora_name, strength_model
        )[0]
        active_trigger_words = (
            str(trigger_words).strip() if abs(float(strength_model)) > 1e-8 else ""
        )
        return loaded_model, active_trigger_words


class PrependLoraTriggers:
    """Prepend enabled LoRA activation text to a compiled image prompt."""

    @classmethod
    def INPUT_TYPES(cls):
        text = ("STRING", {"default": "", "multiline": True})
        return {
            "required": {
                "trigger_1": text,
                "trigger_2": text,
                "trigger_3": text,
                "prompt": text,
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "prepend"
    CATEGORY = "AS-INF/text"
    DESCRIPTION = (
        "Prepends all non-empty conditional LoRA trigger strings to the final "
        "compiled prompt."
    )

    @staticmethod
    def prepend(trigger_1, trigger_2, trigger_3, prompt):
        parts = [
            str(value).strip()
            for value in (trigger_1, trigger_2, trigger_3, prompt)
            if str(value).strip()
        ]
        return ("\n\n".join(parts),)


NODE_CLASS_MAPPINGS = {
    "ASInfOptionalReferenceImage": OptionalReferenceImage,
    "ASInfOptionalReferenceCrop3x4": OptionalReferenceCrop3x4,
    "ASInfLoraLoaderModelOnlyWithTrigger": LoraLoaderModelOnlyWithTrigger,
    "ASInfPrependLoraTriggers": PrependLoraTriggers,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ASInfOptionalReferenceImage": "Optional Reference Image",
    "ASInfOptionalReferenceCrop3x4": "Optional Reference + Fixed 3:4 Crop",
    "ASInfLoraLoaderModelOnlyWithTrigger": "LoRA Loader + Conditional Trigger",
    "ASInfPrependLoraTriggers": "Prepend Active LoRA Triggers",
}

WEB_DIRECTORY = "./web"
