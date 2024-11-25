import app.gradio_ui as g_ui
import uvicorn
import fastapi
import gradio as gr
from fastapi.templating import Jinja2Templates
from LightRAG.lightrag import LightRAG
from LightRAG.lightrag.llm import gpt_4o_mini_complete
import os

# File paths
knowledge_file = './LightRAG/fina/dynamic_knowledge.txt'
static_knowledge_file = './LightRAG/fina/static_knowledge.txt'
output_file = './LightRAG/fina/knowledge.txt'

def merge_knowledge_files(dynamic_file, static_file, output_file):
    try:
        # Read content from both files
        with open(dynamic_file, 'r', encoding='utf-8') as f1:
            dynamic_content = f1.read()
            
        with open(static_file, 'r', encoding='utf-8') as f2:
            static_content = f2.read()
            
        # Combine the content
        merged_content = dynamic_content + "\n" + static_content
        
        # Write merged content to output file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(merged_content)
            
        print(f"Successfully merged files into {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# 合并知识库
merge_knowledge_files(knowledge_file, static_knowledge_file, output_file)

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
    uvicorn.run(app, host="0.0.0.0", port=7860) 