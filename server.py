import app.gradio_ui as g_ui
import uvicorn
import fastapi
import gradio as gr
from fastapi.templating import Jinja2Templates
from LightRAG.lightrag import LightRAG
from LightRAG.lightrag.llm import gpt_4o_mini_complete
import os

app = fastapi.FastAPI()
templates = Jinja2Templates(directory = "templates")

WORKING_DIR = "./LightRAG/fina"
knowledge_dir = os.path.join(WORKING_DIR, "knowledge.txt")

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(working_dir = WORKING_DIR,
               llm_model_func = gpt_4o_mini_complete)

with open(knowledge_dir, "r", encoding="utf-8") as f:
    rag.insert(f.read())

gui = g_ui.Gradio_UI(rag = rag)
app = gr.mount_gradio_app(app = app, path = "/",
                          blocks = gui.create_ui().queue(default_concurrency_limit = 5, max_size = 64))

if __name__ == '__main__':
    uvicorn.run(app)