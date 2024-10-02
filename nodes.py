import base64
from PIL import Image
import torch
import numpy as np
import io


class Base64ImageInput:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_image": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "process_input"

    CATEGORY = "MM"

    def process_input(self, base64_image):
        if base64_image:
            try:
                image_bytes = base64.b64decode(base64_image)
                # Open the image from bytes
                image = Image.open(io.BytesIO(image_bytes))
                image = image.convert("RGB")
                image = np.array(image).astype(np.float32) / 255.0
                image = torch.from_numpy(image)[None,]
                return (image,)
            except Exception as e:
                # Handle error or log the exception
                print(f"Error decoding base64 image: {e}")
                return None
        else:
            return None



class Base64ImageOutput:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "quality": ("INT", {"min": 0, "max": 100, "default": 70}),
            },
        }

    RETURN_TYPES = ("STRING",)

    FUNCTION = "process_output"

    OUTPUT_NODE = True

    CATEGORY = "MM"

    def process_image(self, image, quality):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        buffered = io.BytesIO()
        # Save the image as WebP with lossy compression at the given quality
        img.save(buffered, format="webp", quality=quality)

        base64_image = base64.b64encode(buffered.getvalue()).decode()
        return base64_image

    def process_output(self, images: list[torch.Tensor], quality: int):
        return {"ui": {"images": [self.process_image(image, quality) for image in images]}}




# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Base64ImageInput": Base64ImageInput,
    "Base64ImageOutput": Base64ImageOutput,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64ImageInput": "Base64Image Input Node",
    "Base64ImageOutput": "Base64Image Output Node",
}