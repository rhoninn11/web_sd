
import torch, time
from diffusers import StableDiffusionXLPipeline

def load_base_pipeline(model_id, device):
    print("base pipeline initialization")
    base_pipeline = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    base_pipeline = base_pipeline.to(device)
    return base_pipeline