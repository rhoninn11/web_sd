import time

DEVICE = "cuda"
def callback_testing_txt2img(request_data, out_queue, step_callback=None, device=DEVICE):
    print(f"+++ callback_testing_txt2img")
    steps = 50
    step_now = 0
    while step_now < steps:
        timestep = step_now/steps*1000.0
        if(step_callback):
            step_callback(step_now, timestep, None)
        time.sleep(0.05)
        print(f"+++ callback_testing_txt2img step: {step_now}")
        step_now += 1