
import torch

def init_generator(seed, device):
    g_cuda = torch.Generator(device=device)
    seed = seed % 100
    g_cuda.manual_seed(seed)
    return g_cuda
