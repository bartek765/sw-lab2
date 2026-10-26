import os
import gradio as gr
from agent.agent import respond

app = gr.ChatInterface(fn=respond, title="ESP32 AI Agent — GPIO",
    description="Sterowanie wyjściami ESP32 przez MQTT.",
    examples=["ustaw GPIO 25 na wysoki przez 10 sekund", "ustaw GPIO 26 na niski"])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))
