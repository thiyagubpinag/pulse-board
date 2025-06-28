from typing import List, Tuple
from openai import OpenAI
from correlation_engine import CorrelationEngine
from data_stores import DataStore
from goal_analyzer import GoalAnalyzer
from sprint_status_analyzer import SprintStatusAnalyzer
from system_generator import SystemContextGenerator
from wellbeing_analyzer import WellbeingAnalyzer
from workload_analyzer import WorkloadAnalyzer


class AIManager:
    def __init__(self, api_key: str = None):
        self.client = None
        self.data_store = DataStore()
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key: str):
        """Set the OpenAI API key"""
        self.client = OpenAI(api_key=api_key)
    
    def chat(self, message: str, history: List[Tuple[str, str]]) -> str:
        """Process a chat message and return AI response"""
        if not self.client:
            return "❌ Please provide a valid OpenAI API key first."
        
        try:
            # Build conversation history
            messages = [{"role": "system", "content": SystemContextGenerator.generate_context(
                sprint=self.data_store.sprint_status,
                daily_updates=self.data_store.daily_updates,
                analysis_results=
                WorkloadAnalyzer.analyze(self.data_store.workload_data)+
                GoalAnalyzer.analyze(self.data_store.goal_data) +
                WellbeingAnalyzer.analyze(self.data_store.daily_updates) +
                SprintStatusAnalyzer.analyze(self.data_store.sprint_status),
                correlation=CorrelationEngine.correlate(
                    WorkloadAnalyzer.analyze(self.data_store.workload_data)+
                    GoalAnalyzer.analyze(self.data_store.goal_data) +
                    WellbeingAnalyzer.analyze(self.data_store.daily_updates) +
                    SprintStatusAnalyzer.analyze(self.data_store.sprint_status)
                ),
                workload_data=self.data_store.workload_data
            )}]
            
            for user_msg, assistant_msg in history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})
            
            messages.append({"role": "user", "content": message})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error: {str(e)}"

# ==== Gradio Interface ====

