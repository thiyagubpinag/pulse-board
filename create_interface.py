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
    
    # Create Gradio interface with custom styling
    with gr.Blocks(
        title="PulseBoard AskManager - AI Sprint Assistant",
        theme=gr.themes.Soft(),
        css="""
        .container { 
            max-width: 1200px; 
            margin: auto; 
            padding: 20px;
        }
        .header { 
            text-align: center; 
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #87CEEB 0%, #00BFFF 100%); /* Sky blue gradient */
            color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .feature-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .chat-container { 
            min-height: 450px;
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }
        .input-section {
            background: #ffffff;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-top: 1rem;
        }
        .example-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        .example-item {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .example-item:hover {
            background: #bbdefb;
            transform: translateY(-2px);
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #4caf50;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        """
    ) as demo:
        
        # Header Section
        with gr.Column(elem_classes=["header"]):
            gr.HTML("""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <div>
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: bold;">PulseBoard AskManager</h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Your Intelligent Sprint Management Assistant</p>
                </div>
            </div>
            """)
        
        # What is PulseBoard Section
        with gr.Column(elem_classes=["feature-card"]):
            gr.Markdown("""
            ## 🎯 What is PulseBoard AskManager?
            
            **PulseBoard AskManager** is your AI-powered assistant designed to help you monitor and optimize your team's sprint performance. Think of it as your personal sprint coach that understands your team's workload, progress, and well-being.
            
            ### Key Features:
            - **📊 Real-time Sprint Monitoring** - Track progress and identify bottlenecks instantly
            - **👥 Team Health Analysis** - Monitor workload distribution and prevent burnout
            - **🎯 Smart Recommendations** - Get actionable insights to improve team performance
            - **📈 Progress Tracking** - Understand where your sprint stands and what needs attention
            """)
        
        # Main Chat Interface
        with gr.Row():
            with gr.Column(scale=2):
                # Status indicator
                gr.HTML("""
                <div style="display: flex; align-items: center; margin-bottom: 1rem; padding: 0.5rem; background: #f0f8f0; border-radius: 8px;">
                    <span class="status-indicator"></span>
                    <span style="color: #2e7d32; font-weight: 500;">AskManager is ready to help you!</span>
                </div>
                """)
                
                chatbot = gr.Chatbot(
                    label="💬 Chat with AskManager",
                    elem_classes=["chat-container"],
                    height=400,
                    placeholder="Start a conversation with AskManager! Ask about your team's sprint progress, workload distribution, or get recommendations for improvement.",
                    show_label=True
                )
                
                with gr.Column(elem_classes=["input-section"]):
                    with gr.Row():
                        question_input = gr.Textbox(
                            label="💭 Ask AskManager anything about your sprint",
                            placeholder="e.g., 'How is my team's workload distributed?' or 'What should I focus on this week?'",
                            scale=4,
                            lines=2
                        )
                        send_btn = gr.Button(
                            "Send 🚀", 
                            variant="primary", 
                            scale=1,
                            size="lg"
                        )
        
        # Example Questions Section
        with gr.Column():
            gr.Markdown("## 💡 Try These Sample Questions")
            
            # Create clickable example buttons
            example_questions = [
                ("👥 Team Workload", "Who needs help with their workload? Show me the current distribution."),
                ("📊 Sprint Progress", "What's our sprint progress looking like? Are we on track?"),
                ("⚠️ Burnout Risk", "Are any team members at risk of burnout? What are the warning signs?"),
                ("🎯 Priority Focus", "What should I prioritize this week to improve our sprint outcome?"),
                ("🔄 Blockers & Issues", "What are the current blockers affecting our team's productivity?"),
                ("📈 Performance Metrics", "How is our team performing compared to previous sprints?"),
                ("🎨 Resource Allocation", "How can we better allocate resources for maximum efficiency?"),
                ("🚦 Risk Assessment", "What risks should I be aware of for this sprint?")
            ]
            
            with gr.Column():
                example_buttons = []
                for title, question in example_questions:
                    btn = gr.Button(
                        title,
                        variant="secondary",
                        size="sm",
                        elem_classes=["example-item"]
                    )
                    example_buttons.append((btn, question))
        
        # How to Use Section
        with gr.Column(elem_classes=["feature-card"]):
            gr.Markdown("""
            ## 🔧 How to Use AskManager
            
            1. **Ask Natural Questions** - Simply type your questions in plain English about your sprint, team, or project
            2. **Get Instant Insights** - AskManager analyzes your data and provides immediate, actionable responses
            3. **Follow Recommendations** - Implement the suggested actions to improve your team's performance
            4. **Monitor Continuously** - Regular check-ins help maintain optimal team health and productivity
            
            ### 📋 Best Practices:
            - **Be Specific**: Instead of "How are we doing?", try "What's our completion rate for this sprint?"
            - **Ask for Details**: Request specific metrics, team member insights, or actionable recommendations
            - **Regular Check-ins**: Use AskManager daily for the best sprint management experience
            """)
        
        # State management
        chat_history = gr.State([])
        
        # Event handlers
        def submit_message(msg, history):
            if not msg.strip():
                return history, history, msg
            return respond(msg, history)
        
        def set_example_question(question):
            return question
        
        # Wire up the example buttons
        for btn, question in example_buttons:
            btn.click(
                lambda q=question: q,
                outputs=[question_input]
            )
        
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