"""
Psychology Service
Integrates the PsychologyTest module with the FastAPI backend.
"""

import os
import sys
import asyncio
from typing import List, Optional, Tuple, Any
from pathlib import Path
from io import BytesIO

# Add the psychology test module to the path
psychology_path = Path(__file__).parent.parent / "hugg" / "1.PsychologyTest"
sys.path.append(str(psychology_path))

# Import psychology test modules
from settings import (
    respond,
    generate_interview_report as generate_interview_report_original,
    generate_report_from_file as generate_report_from_file_original,
    reset_interview,
    interview_history,
    question_count
)
from ai_config import convert_text_to_speech, n_of_questions, load_model, openai_api_key
from prompt_instructions import get_interview_initial_message_sarah, get_interview_initial_message_aaron
from knowledge_retrieval import setup_knowledge_retrieval
from services.ai_service import ai_service

from models.schemas import TherapyMessage


class PsychologyService:
    """Service for psychology interview functionality"""
    
    def __init__(self):
        self.llm = None
        self.interview_retrieval_chain = None
        self.report_retrieval_chain = None
        self.combined_retriever = None
        self.knowledge_base_connected = False
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base and retrieval chains"""
        try:
            if not openai_api_key:
                print("OpenAI API key not available. Using fallback mode.")
                self.knowledge_base_connected = False
                return
                
            # Try to initialize the knowledge base
            try:
                self.llm = load_model(openai_api_key)
                self.interview_retrieval_chain, self.report_retrieval_chain, self.combined_retriever = setup_knowledge_retrieval(self.llm)
                self.knowledge_base_connected = True
                print("Successfully connected to psychology knowledge base.")
            except Exception as kb_error:
                print(f"Knowledge base initialization failed: {str(kb_error)}")
                self.knowledge_base_connected = False
                print("Psychology service will use fallback mode.")
                
        except Exception as e:
            print(f"Error initializing psychology service: {str(e)}")
            self.knowledge_base_connected = False
            print("Psychology service will use fallback mode.")
    
    async def start_interview(
        self, 
        interviewer: str = "Sarah", 
        language: str = "english"
    ) -> Tuple[str, Optional[BytesIO]]:
        """Start a new psychology interview"""
        try:
            # Reset interview state
            reset_interview()
            
            # Get initial message based on interviewer
            if interviewer.lower() == "sarah":
                initial_message = get_interview_initial_message_sarah()
                voice_setting = "alloy"
            else:
                initial_message = get_interview_initial_message_aaron()
                voice_setting = "onyx"
            
            # Convert to speech
            try:
                audio_buffer = BytesIO()
                convert_text_to_speech(initial_message, audio_buffer, voice_setting)
                audio_buffer.seek(0)
                return initial_message, audio_buffer
            except Exception as e:
                print(f"Error generating audio: {e}")
                return initial_message, None
            
        except Exception as e:
            print(f"Error starting interview: {str(e)}")
            # Fallback message
            fallback_message = "Hello, I'm here to help you. How are you feeling today?"
            return fallback_message, None
    
    async def continue_interview(
        self,
        user_message: str,
        session_history: List[TherapyMessage],
        interviewer: str = "Sarah",
        language: str = "english"
    ) -> Tuple[str, Optional[BytesIO], int, bool]:
        """Continue the psychology interview with user response"""
        try:
            # Convert session history to interview format
            interview_history_list = []
            for msg in session_history:
                if msg.is_user:
                    interview_history_list.append(f"Q{len(interview_history_list)//2 + 1}: {msg.content}")
                else:
                    interview_history_list.append(f"A{len(interview_history_list)//2}: {msg.content}")
            
            # Update global interview history
            global interview_history, question_count
            interview_history = interview_history_list
            question_count = len([msg for msg in session_history if not msg.is_user])
            
            # Set voice based on interviewer
            voice = "alloy" if interviewer.lower() == "sarah" else "onyx"
            
            # Generate response using psychology module
            if self.knowledge_base_connected:
                # Reinitialize chains with current language if needed
                if question_count == 1:
                    self.interview_retrieval_chain, self.report_retrieval_chain, self.combined_retriever = setup_knowledge_retrieval(
                        self.llm, language, interviewer
                    )
                
                # Generate next question
                if question_count < n_of_questions():
                    result = self.interview_retrieval_chain.invoke({
                        "input": f"Based on the patient's statement: '{user_message}', what should be the next question?",
                        "history": "\n".join(interview_history),
                        "question_number": question_count + 1,
                        "language": language
                    })
                    response = result.get("answer", f"Can you tell me more about that? (in {language})")
                else:
                    # Generate final report
                    result = self._generate_report_from_history(interview_history, language)
                    response = result
                    return response, None, question_count, True
            else:
                # Use local LLM for response
                # Compose conversation history as pairs (user, ai)
                conversation_pairs = []
                for i in range(0, len(session_history) - 1, 2):
                    if i + 1 < len(session_history) and session_history[i].is_user and not session_history[i + 1].is_user:
                        conversation_pairs.append((session_history[i].content, session_history[i + 1].content))
                response, _ = await ai_service.generate_therapy_response(
                    user_message=user_message,
                    conversation_history=conversation_pairs,
                    personality="warm",
                    user_id=None
                )
            
            # Convert response to speech
            try:
                audio_buffer = BytesIO()
                convert_text_to_speech(response, audio_buffer, voice)
                audio_buffer.seek(0)
                return response, audio_buffer, question_count + 1, question_count >= n_of_questions()
            except Exception as e:
                print(f"Error generating audio: {e}")
                return response, None, question_count + 1, question_count >= n_of_questions()
            
        except Exception as e:
            print(f"Error continuing interview: {str(e)}")
            # Fallback response
            fallback_response = "I understand. Can you tell me more about how you're feeling?"
            return fallback_response, None, question_count, False
    
    async def generate_interview_report(
        self,
        messages: List[TherapyMessage],
        language: str = "english"
    ) -> Tuple[str, str]:
        """Generate clinical report from interview messages"""
        try:
            # Convert messages to interview history format
            interview_history_list = []
            for msg in messages:
                if msg.is_user:
                    interview_history_list.append(f"Q{len(interview_history_list)//2 + 1}: {msg.content}")
                else:
                    interview_history_list.append(f"A{len(interview_history_list)//2}: {msg.content}")
            
            # Generate report
            if self.knowledge_base_connected:
                # Reinitialize report chain with language
                _, report_retrieval_chain, _ = setup_knowledge_retrieval(self.llm, language)
                
                result = report_retrieval_chain.invoke({
                    "input": "Please provide a clinical report based on the following interview:",
                    "history": "\n".join(interview_history_list),
                    "language": language
                })
                report_content = result.get("answer", "Unable to generate report due to insufficient information.")
            else:
                report_content = self._generate_fallback_report(interview_history_list)
            
            # Create PDF
            pdf_path = self._create_pdf_report(report_content)
            
            return report_content, pdf_path
            
        except Exception as e:
            print(f"Error generating interview report: {str(e)}")
            fallback_content = "Unable to generate report at this time."
            return fallback_content, ""
    
    async def analyze_document(
        self,
        file_path: str,
        language: str = "english"
    ) -> Tuple[str, str]:
        """Analyze uploaded document and generate clinical report"""
        try:
            # Generate report from file
            if self.knowledge_base_connected:
                report_content, pdf_path = generate_report_from_file_original(
                    {"name": file_path, "content": open(file_path, 'rb').read()},
                    language
                )
            else:
                # Fallback document analysis
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:100000]  # Limit to 100K characters
                
                report_content = f"Document Analysis Report\n\nContent Length: {len(content)} characters\n\nThis is a basic analysis of the uploaded document. For detailed clinical analysis, please ensure the knowledge base is properly configured."
                pdf_path = self._create_pdf_report(report_content)
            
            return report_content, pdf_path
            
        except Exception as e:
            print(f"Error analyzing document: {str(e)}")
            fallback_content = "Unable to analyze document at this time."
            return fallback_content, ""
    
    def _generate_report_from_history(self, history: List[str], language: str) -> str:
        """Generate report from interview history"""
        try:
            if self.knowledge_base_connected:
                _, report_retrieval_chain, _ = setup_knowledge_retrieval(self.llm, language)
                
                result = report_retrieval_chain.invoke({
                    "input": "Please provide a clinical report based on the interview.",
                    "history": "\n".join(history),
                    "language": language
                })
                return result.get("answer", "Unable to generate report due to insufficient information.")
            else:
                return self._generate_fallback_report(history)
        except Exception as e:
            print(f"Error generating report from history: {str(e)}")
            return self._generate_fallback_report(history)
    
    def _generate_fallback_report(self, history: List[str]) -> str:
        """Generate a basic fallback report"""
        return f"""Clinical Interview Report

Interview Summary:
This interview consisted of {len(history)//2} question-answer exchanges.

Key Points:
- The patient participated in a structured clinical interview
- Responses were recorded for analysis
- This is a basic report generated without advanced knowledge base integration

Recommendations:
- Consider professional consultation for detailed clinical assessment
- This report is for educational purposes only
- Not a substitute for professional medical advice

Note: This is a fallback report. For comprehensive analysis, ensure the psychology knowledge base is properly configured.
"""
    
    def _create_pdf_report(self, content: str) -> str:
        """Create PDF report file"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_JUSTIFY
            import tempfile
            
            # Create reports directory if it doesn't exist
            reports_dir = Path(__file__).parent.parent / "uploads" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                pdf_path = temp_file.name
            
            # Create PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Clinical Psychology Report", title_style))
            story.append(Spacer(1, 12))
            
            # Content
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_JUSTIFY
            )
            
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), content_style))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
            # Move to reports directory with unique name
            import uuid
            final_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
            final_path = reports_dir / final_filename
            
            import shutil
            shutil.move(pdf_path, str(final_path))
            
            return str(final_path)
            
        except Exception as e:
            print(f"Error creating PDF report: {str(e)}")
            return ""


# Create singleton instance
psychology_service = PsychologyService() 