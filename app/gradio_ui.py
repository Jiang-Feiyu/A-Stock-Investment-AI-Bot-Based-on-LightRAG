import json
import time
import gradio as gr
import os, sys
sys.path.append("..")
from LightRAG.lightrag import QueryParam

class Gradio_UI:
    def __init__(self, rag):
        # predefined prompts, can provide different kind of advice
        self.pre_defined_prompts = None

        # components
        self.roles_drop = None
        self.prompt_box = None
        self.custom_btn = None
        self.temperature_slider = None
        self.top_p_slider = None
        self.freq_penalty_slider = None
        self.presence_penalty_slider = None
        self.max_token_slider = None
        self.chat_box = None
        self.chat_revoke_btn = None
        self.input_message = None
        self.option_bar = None
        self.advance_option_btn = None

        self.option_bar_state = False

        self.rag = rag

        with open("./app/pre_defined_prompts.json", "r", encoding="utf-8") as f:
            self.pre_defined_prompts = json.load(f)


    def forbid_prompt_submit(self):
        return {
            self.roles_drop: gr.update(interactive = False),
            self.prompt_box: gr.update(interactive = False),
            self.custom_btn: gr.update(interactive = False)
        }

    def custom_setting(self):
        return {
            self.prompt_box: gr.update(placeholder = "Please input the Prompt", value = None, interactive = True, visible = True),
            self.roles_drop: gr.update(value = "Custom", allow_custom_value = True),
        }

    def pre_defined(self, a):
        return {
            self.prompt_box: gr.update(value = self.pre_defined_prompts[a], interactive = False, visible = False),
            self.roles_drop: gr.update(allow_custom_value = False),
        }

    def option_bar_switch(self):
        self.option_bar_state = not self.option_bar_state
        if self.option_bar_state:
            title = "Hide"
        else:
            title = "Show Advance Options"

        return {
            self.option_bar: gr.update(visible = self.option_bar_state),
            self.advance_option_btn: gr.update(value = title),
        }

    # TODO: Communicate with Model
    def respond(self, query, chat_history):
        res = self.rag.query(query = query, param = QueryParam(mode = "hybrid"))
        chat_history.append((query, res))

        yield {
            self.input_message: "",
            self.chat_box: chat_history
        }
    """
    def respond(query, chat_history, prompt, temperature, top_p,
                freq_penalty, presence_penalty, max_tokens):
        history = []
        for user_msg, ai_msg in chat_history:
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": ai_msg})

        res = ""
        chat_history.append((query, res))
        for r in model.ChatGPT(prompt).stream_with_history(query, history,
                                                           temperature=temperature,
                                                           top_p=top_p,
                                                           presence_penalty=presence_penalty,
                                                           frequency_penalty=freq_penalty,
                                                           max_tokens=max_tokens):
            res += r
            chat_history[-1] = (query, res)
            time.sleep(0.01)
            yield {input_message: "", chat_box: chat_history}
        yield {input_message: "", chat_box: chat_history}
    """

    def helper_layout(self):
        with gr.Blocks() as b:
            with gr.Row():
                with gr.Column(scale = 4):
                    gr.Markdown("<h4>Chat</h4>")

                    self.chat_box = gr.Chatbot(
                        elem_id="chat-box", show_label=False, height=600)

                    with gr.Row():
                        self.input_message = gr.Textbox(
                            placeholder = "Input your query, and press SHIFT + ENTER to send",
                            show_label = False, lines = 4, max_lines = 4,
                            elem_id = "chat-input", container = False)
                        with gr.Column():
                            self.chat_revoke_btn = gr.Button("Clear", elem_id="chat_revoke")
                            self.advance_option_btn = gr.Button("Show Advance Options")

                with gr.Column(scale = 6):
                    with gr.Column(visible = self.option_bar_state) as option_bar:
                        self.option_bar = option_bar
                        gr.Markdown("<h4>Prompt Settings</h4>")
                        with gr.Row():
                            with gr.Column():
                                with gr.Row():
                                    # Several preferences provided for user to choose
                                    self.roles_drop = gr.Dropdown(
                                        choices = self.pre_defined_prompts.keys(),
                                        value="default", label="PREDEFINED ROLES",
                                        interactive=True)

                                with gr.Row():
                                    self.prompt_box = gr.Textbox(
                                        label = "PROMPT",
                                        value = self.pre_defined_prompts[self.roles_drop.value],
                                        lines = 8, max_lines = 8,
                                        interactive = False,
                                        visible = False
                                    )

                                with gr.Row():
                                    self.custom_btn = gr.Button(
                                        "Create Your Own Prompt")

                        # Model settings
                        gr.Markdown("<h4>Parameters</h4>")
                        with gr.Row():
                            with gr.Column(variant="panel"):
                                with gr.Row():
                                    self.temperature_slider = gr.Slider(
                                        minimum=0.0, maximum=1.0,
                                        step=0.1, label="TEMPERATURE",
                                        interactive=True, value=0.1,
                                        info="Info Test: This is Temperature.")
                                    self.top_p_slider = gr.Slider(
                                        minimum=0.0, maximum=1.0,
                                        step=0.1, label="TOP-P",
                                        interactive=True, value=1.0)
                                with gr.Row():
                                    self.freq_penalty_slider = gr.Slider(
                                        minimum=-2.0, maximum=2.0,
                                        step=0.1, label="FREQUENCY PENALTY",
                                        interactive=True, value=0.0)
                                    self.presence_penalty_slider = gr.Slider(
                                        minimum=-2.0, maximum=2.0,
                                        step=0.1, label="PRESENCE PENALTY",
                                        interactive=True, value=0.0)
                                with gr.Row():
                                    self.max_token_slider = gr.Slider(
                                        minimum=20, maximum=4096,
                                        step=1, label="MAX TOKEN",
                                        interactive=True, value=800)


            self.bind_callback()

        return {"block": b, "label": "HELPER"}

    def bind_callback(self):
        self.roles_drop.input(self.pre_defined, inputs = [self.roles_drop], outputs = [self.prompt_box, self.roles_drop])
        self.custom_btn.click(self.custom_setting, inputs = [], outputs = [self.prompt_box, self.roles_drop])
        self.input_message.submit(self.forbid_prompt_submit, inputs = [],
                             outputs = [self.roles_drop, self.prompt_box, self.custom_btn])
        self.chat_revoke_btn.click(lambda p: "", inputs = [self.chat_box], outputs = [self.chat_box])
        self.advance_option_btn.click(self.option_bar_switch, inputs = [], outputs = [self.option_bar, self.advance_option_btn])

        self.input_message.submit(self.respond,
                             inputs = [self.input_message, self.chat_box],
                             outputs = [self.input_message, self.chat_box])

    def create_ui(self):
        tabs = [self.helper_layout()]
        with gr.Blocks(title = "prompt") as ui:
            with gr.Tabs(elem_id = "tabs"):
                for t in tabs:
                    with gr.TabItem(label = t["label"], id = t["label"], elem_id = "tab_" + t["label"]):
                        t["block"].render()
        return ui