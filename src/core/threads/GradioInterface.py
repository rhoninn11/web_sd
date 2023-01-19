
from core.utils.utils_thread import ThreadWrap
import gradio as gr

# has thread interface but it have to run in main tread
class GradioInterface():
    def __init__(self):
        ThreadWrap.__init__(self)
        self.config_reciver = None
        self.run_cond = False
        self.history = []

    def bind_config_reciver(self, reciver):
        self.config_reciver = reciver

    def config_messegify(self, config):
        message = []
        for key in config:
            if len(message):
                message.append("; ")
            message.append(f"{key.upper()}: {config[key]}")
        
        return "".join(message)

    def prompt_config_chat(self, prompt, prompt_negative, power, history):
        new_config = {
            "prompt": prompt,
            "prompt_negative": prompt_negative,
            "power": power
        }
        
        history = self.history
        message = self.config_messegify(new_config)
        if self.config_reciver:
            self.config_reciver.new_config(new_config)
        response = f"New config applied"

        history.append((message, response))
        return history, history

    # thread inteface functions
    def start(self):
        config_chat_history = gr.Chatbot().style(color_map=("blue", "grean"))
        config_interface = gr.Interface(fn=self.prompt_config_chat,
            inputs=[
                    gr.Textbox(
                        label="Prompt",
                        lines=3,
                    ),       
                    gr.Textbox(
                        label="Prompt negative",
                        lines=3,
                    ),
                    gr.Slider(0.0, 1.0, value=0.8, label="power"),
                    "state"
                ],
            outputs=[config_chat_history, "state"],
            allow_flagging="never",
        )
        config_interface.launch()     
    
    def is_blocking(self):
        return True

    def ask_to_stop(self):
        pass
    
    def join(self):
        pass
