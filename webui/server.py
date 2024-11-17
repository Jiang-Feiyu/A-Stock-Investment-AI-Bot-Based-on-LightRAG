import gradio_ui
import uvicorn
import fastapi
import gradio as gr
from fastapi.templating import Jinja2Templates

app = fastapi.FastAPI()
templates = Jinja2Templates(directory = "templates")

gui = gradio_ui.Gradio_UI()
app = gr.mount_gradio_app(app = app, path = "/",
                          blocks = gui.create_ui().queue(default_concurrency_limit = 5, max_size = 64))

if __name__ == '__main__':
    uvicorn.run(app)