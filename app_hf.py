"""
Gradio interface for HuggingFace Spaces deployment
Runs on: https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system
"""
import gradio as gr
import requests
import json
from typing import Optional

# Start the FastAPI app in background
import subprocess
import time
import threading

def start_fastapi():
    """Start FastAPI server in background"""
    subprocess.Popen(
        ["python", "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "7860"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)  # Wait for server to start

# Start FastAPI in background thread
threading.Thread(target=start_fastapi, daemon=True).start()

def analyze_architecture(description: str, provider: str = "openrouter", model_id: str = "google/gemini-2.0-flash-exp:free") -> dict:
    """
    Analyze AWS architecture for failures and provide recommendations
    
    Args:
        description: Describe your AWS architecture
        provider: LLM provider (openrouter, local, etc.)
        model_id: Model to use
        
    Returns:
        Analysis results with failures and recommendations
    """
    try:
        payload = {
            "description": description,
            "provider": provider,
            "model_id": model_id
        }
        
        response = requests.post(
            "http://127.0.0.1:7860/api/analyze",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "✅ Analysis Complete",
                "result": json.dumps(result, indent=2)
            }
        else:
            return {
                "status": "❌ Error",
                "result": f"Error {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "❌ Error",
            "result": f"Connection error: {str(e)}\n\nMake sure the description is at least 10 characters long."
        }

# Build Gradio interface
with gr.Blocks(title="AWS Architecture Failure Detection", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏗️ AWS Architecture Failure Detection System
    
    Analyze your AWS architecture for potential failures and get AI-driven recommendations.
    
    **How to use:**
    1. Describe your AWS architecture (e.g., "EC2 with RDS master-slave, API Gateway with Lambda")
    2. Select your LLM provider
    3. Click "Analyze" to get failure predictions and recommendations
    """)
    
    with gr.Row():
        with gr.Column():
            # Input
            architecture_desc = gr.Textbox(
                label="AWS Architecture Description",
                placeholder="Describe your architecture: EC2 instances with RDS master-slave, API Gateway, Lambda...",
                lines=5,
                info="Minimum 10 characters"
            )
            
            with gr.Row():
                provider = gr.Dropdown(
                    choices=["openrouter", "simulation"],
                    value="openrouter",
                    label="LLM Provider"
                )
                model_id = gr.Textbox(
                    value="google/gemini-2.0-flash-exp:free",
                    label="Model ID",
                    info="Leave default or customize"
                )
            
            analyze_btn = gr.Button("🔍 Analyze Architecture", variant="primary", size="lg")
        
        with gr.Column():
            # Output
            status_output = gr.Textbox(label="Status", interactive=False)
            result_output = gr.Textbox(
                label="Analysis Results",
                lines=15,
                interactive=False,
                show_copy_button=True
            )
    
    # Connect button
    analyze_btn.click(
        fn=analyze_architecture,
        inputs=[architecture_desc, provider, model_id],
        outputs=[status_output, result_output]
    )
    
    # Examples
    gr.Examples(
        examples=[
            [
                "I have 3 EC2 instances behind an ALB with a single RDS database and ElastiCache. Auto-scaling is disabled.",
                "openrouter",
                "google/gemini-2.0-flash-exp:free"
            ],
            [
                "API Gateway → Lambda → DynamoDB with no read replicas. Single AZ deployment.",
                "openrouter",
                "google/gemini-2.0-flash-exp:free"
            ],
            [
                "On-premise database synced to S3 daily. No backup strategy. Manual deployments via SSH.",
                "simulation",
                "google/gemini-2.0-flash-exp:free"
            ],
        ],
        inputs=[architecture_desc, provider, model_id],
        outputs=[status_output, result_output],
        fn=analyze_architecture,
        run_on_load=False
    )
    
    gr.Markdown("""
    ---
    
    ## 📚 About
    This tool uses AI agents to:
    - 🔍 **Detect** common AWS architecture failures
    - 📊 **Analyze** failure patterns and dependencies
    - 💡 **Recommend** architectural improvements
    - 🛡️ **Predict** potential outages
    
    **GitHub**: https://github.com/karthikc1125/aws-architecture-failure-detection-system
    """)

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
