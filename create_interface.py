
from typing import List
from ai_manager import AIManager
import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment
api_key = os.getenv("OPENAI_API_KEY")

def create_interface():
    ai_manager = AIManager()
    
    def respond(message: str, history: List):
        
        
        # Update API key if changed
        ai_manager.set_api_key(api_key.strip())
        
        # Get AI response
        reply = ai_manager.chat(message, history)
        
        # Update history
        new_history = history + [(message, reply)]
        
        return new_history, new_history, ""
    
    # Create Gradio interface
    with gr.Blocks(
        title="PulseBoard AskManager",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1000px; margin: auto; }
        .header { text-align: center; margin-bottom: 2rem; }
        .chat-container { min-height: 400px; }
        """
    ) as demo:
        gr.Markdown(
            """
            # 🤖 AskManager — PulseBoard Chat
            
            Your AI assistant for sprint management and team health monitoring.
            Ask questions about team workload, sprint progress, or get recommendations.
            """,
            elem_classes=["header"]
        )
            
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(
                    label="Chat with AskManager",
                    elem_classes=["chat-container"],
                    height=500
                )
                
                with gr.Row():
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask about team health, sprint progress, or get recommendations...",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Example questions
        gr.Markdown("""
        **Example Questions:**
        - "Who needs help with their workload?"
        - "What's our sprint progress looking like?"
        - "Any team members at risk of burnout?"
        - "What should I prioritize this week?"
        """)
        
        # State management
        chat_history = gr.State([])
        
        # Event handlers
        def submit_message(msg, history):
            if not msg.strip():
                return history, history, msg
            return respond(msg, history)
        
        send_btn.click(
            submit_message,
            inputs=[question_input, chat_history],
            outputs=[chatbot, chat_history, question_input]
        )
        
        question_input.submit(
            submit_message,
            inputs=[question_input, chat_history],
            outputs=[chatbot, chat_history, question_input]
        )
    
    return demo
