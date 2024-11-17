import model
import gradio_ui
import uvicorn
import fastapi
import gradio as gr
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

app = fastapi.FastAPI()
templates = Jinja2Templates(directory = "templates")

