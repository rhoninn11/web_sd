
import torch, time
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline

def extract_cuda_number(device):
    dev_name_split = device.split(":")
    if len(dev_name_split) == 1:
        return 0
    cuda_number = int(dev_name_split[1])
    return cuda_number

def load_base_pipeline(model_id, refiner_id, device):
    gpu_id = extract_cuda_number(device)
    print("base pipeline initialization")
    base_pipeline = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    base_pipeline.enable_vae_tiling()
    base_pipeline.enable_model_cpu_offload(gpu_id=gpu_id)

    refiner_pipeline = StableDiffusionXLImg2ImgPipeline.from_pretrained(refiner_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16",
        text_encoder_2=base_pipeline.text_encoder_2,
        vae=base_pipeline.vae,
    )
    refiner_pipeline.enable_vae_tiling()
    refiner_pipeline.enable_model_cpu_offload(gpu_id=gpu_id)
    return (base_pipeline, refiner_pipeline)