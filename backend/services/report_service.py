"""
Report Service for therapy session analysis and PDF generation
Creates comprehensive reports with insights and analytics.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from models.schemas import TherapySession, TherapyMessage
from core.config import get_settings

settings = get_settings()


class ReportService:
    """Report generation service for therapy sessions"""
    
    def __init__(self):
        self.reports_dir = "reports"
        self._ensure_reports_dir()
    
    def _ensure_reports_dir(self):
        """Ensure reports directory exists"""
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_session_report(
        self,
        session: TherapySession,
        messages: List[TherapyMessage],
        report_type: str = "summary",
        include_audio: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive therapy session report
        """
        
        # Analyze session data
        analysis = await self._analyze_session(session, messages)
        
        # Generate report content based on type
        if report_type == "summary":
            content = await self._generate_summary_report(session, messages, analysis)
        elif report_type == "progress":
            content = await self._generate_progress_report(session, messages, analysis)
        elif report_type == "analysis":
            content = await self._generate_analysis_report(session, messages, analysis)
        else:
            content = await self._generate_summary_report(session, messages, analysis)
        
        # Generate PDF
        file_path = await self._create_pdf_report(session, content, report_type)
        
        return {
            "content": json.dumps(content),
            "file_path": file_path,
            "download_url": f"/api/reports/download/{session.id}_{report_type}",
            "analysis": analysis
        }
    
    async def _analyze_session(
        self,
        session: TherapySession,
        messages: List[TherapyMessage]
    ) -> Dict[str, Any]:
        """Analyze therapy session for insights"""
        
        user_messages = [msg for msg in messages if msg.is_user]
        therapist_messages = [msg for msg in messages if not msg.is_user]
        
        # Basic statistics
        total_messages = len(messages)
        user_message_count = len(user_messages)
        therapist_message_count = len(therapist_messages)
        
        # Calculate session duration
        if messages:
            session_start = messages[0].created_at
            session_end = messages[-1].created_at
            duration_minutes = (session_end - session_start).total_seconds() / 60
        else:
            duration_minutes = 0
        
        # Analyze content
        user_word_count = sum(len(msg.content.split()) for msg in user_messages)
        therapist_word_count = sum(len(msg.content.split()) for msg in therapist_messages)
        
        # Mood analysis
        mood_distribution = {}
        for msg in therapist_messages:
            if msg.mood:
                mood_distribution[msg.mood] = mood_distribution.get(msg.mood, 0) + 1
        
        # Topic analysis (simple keyword extraction)
        topics = await self._extract_topics(user_messages)
        
        # Sentiment analysis (simple)
        sentiment = await self._analyze_sentiment(user_messages)
        
        return {
            "session_duration_minutes": round(duration_minutes, 2),
            "total_messages": total_messages,
            "user_messages": user_message_count,
            "therapist_messages": therapist_message_count,
            "user_word_count": user_word_count,
            "therapist_word_count": therapist_word_count,
            "mood_distribution": mood_distribution,
            "topics": topics,
            "sentiment": sentiment,
            "engagement_score": self._calculate_engagement_score(user_messages, therapist_messages)
        }
    
    async def _extract_topics(self, messages: List[TherapyMessage]) -> List[str]:
        """Extract key topics from user messages"""
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            "anxiety": ["anxious", "worry", "worried", "nervous", "stress", "panic"],
            "depression": ["sad", "depressed", "down", "hopeless", "empty"],
            "relationships": ["relationship", "partner", "family", "friend", "love"],
            "work": ["job", "work", "career", "boss", "colleague", "workplace"],
            "sleep": ["sleep", "insomnia", "tired", "exhausted", "rest"],
            "health": ["health", "medical", "doctor", "illness", "pain"],
            "self-esteem": ["confidence", "self-worth", "insecure", "doubt"],
            "trauma": ["trauma", "abuse", "ptsd", "flashback", "trigger"]
        }
        
        detected_topics = []
        all_text = " ".join(msg.content.lower() for msg in messages)
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics[:5]  # Return top 5 topics
    
    async def _analyze_sentiment(self, messages: List[TherapyMessage]) -> Dict[str, Any]:
        """Analyze overall sentiment of user messages"""
        
        positive_words = [
            "happy", "good", "great", "wonderful", "excellent", "better", "progress",
            "hopeful", "positive", "excited", "grateful", "thankful", "peaceful"
        ]
        
        negative_words = [
            "sad", "bad", "terrible", "awful", "worried", "anxious", "depressed",
            "angry", "frustrated", "hopeless", "lonely", "scared", "upset"
        ]
        
        all_text = " ".join(msg.content.lower() for msg in messages).split()
        
        positive_count = sum(1 for word in all_text if word in positive_words)
        negative_count = sum(1 for word in all_text if word in negative_words)
        total_words = len(all_text)
        
        if total_words == 0:
            return {"overall": "neutral", "positive_ratio": 0, "negative_ratio": 0}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio:
            overall = "positive"
        elif negative_ratio > positive_ratio:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall": overall,
            "positive_ratio": round(positive_ratio, 3),
            "negative_ratio": round(negative_ratio, 3)
        }
    
    def _calculate_engagement_score(
        self,
        user_messages: List[TherapyMessage],
        therapist_messages: List[TherapyMessage]
    ) -> float:
        """Calculate engagement score based on message patterns"""
        
        if not user_messages:
            return 0.0
        
        # Factors for engagement score
        avg_user_length = sum(len(msg.content) for msg in user_messages) / len(user_messages)
        response_ratio = len(therapist_messages) / len(user_messages) if user_messages else 0
        
        # Simple engagement calculation
        length_score = min(avg_user_length / 100, 1.0)  # Normalize to 0-1
        response_score = min(response_ratio, 1.0)
        
        engagement_score = (length_score + response_score) / 2
        return round(engagement_score * 100, 1)  # Return as percentage
    
    async def _generate_summary_report(
        self,
        session: TherapySession,
        messages: List[TherapyMessage],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate session summary report"""
        
        return {
            "title": "Therapy Session Summary",
            "session_info": {
                "title": session.title,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{analysis['session_duration_minutes']} minutes"
            },
            "overview": {
                "total_exchanges": analysis['user_messages'],
                "main_topics": analysis['topics'],
                "overall_sentiment": analysis['sentiment']['overall'],
                "engagement_level": self._get_engagement_level(analysis['engagement_score'])
            },
            "key_insights": self._generate_key_insights(analysis, messages),
            "recommendations": self._generate_recommendations(analysis)
        }
    
    async def _generate_progress_report(
        self,
        session: TherapySession,
        messages: List[TherapyMessage],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate progress tracking report"""
        
        return {
            "title": "Therapy Progress Report",
            "session_info": {
                "title": session.title,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M")
            },
            "progress_indicators": {
                "communication_quality": analysis['engagement_score'],
                "topic_exploration": len(analysis['topics']),
                "emotional_expression": analysis['sentiment']
            },
            "areas_of_focus": analysis['topics'],
            "mood_patterns": analysis['mood_distribution'],
            "next_steps": self._generate_next_steps(analysis)
        }
    
    async def _generate_analysis_report(
        self,
        session: TherapySession,
        messages: List[TherapyMessage],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed analysis report"""
        
        return {
            "title": "Detailed Session Analysis",
            "session_info": {
                "title": session.title,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{analysis['session_duration_minutes']} minutes"
            },
            "statistical_analysis": {
                "message_count": analysis['total_messages'],
                "word_count": analysis['user_word_count'],
                "avg_message_length": round(analysis['user_word_count'] / analysis['user_messages'], 1) if analysis['user_messages'] > 0 else 0
            },
            "content_analysis": {
                "topics": analysis['topics'],
                "sentiment": analysis['sentiment'],
                "mood_distribution": analysis['mood_distribution']
            },
            "therapeutic_insights": self._generate_therapeutic_insights(analysis, messages)
        }
    
    def _generate_key_insights(self, analysis: Dict[str, Any], messages: List[TherapyMessage]) -> List[str]:
        """Generate key insights from session"""
        
        insights = []
        
        # Engagement insight
        if analysis['engagement_score'] > 70:
            insights.append("High level of engagement and active participation observed.")
        elif analysis['engagement_score'] < 30:
            insights.append("Lower engagement levels - may benefit from different therapeutic approaches.")
        
        # Topic insight
        if len(analysis['topics']) > 3:
            insights.append("Multiple therapeutic areas identified for exploration.")
        
        # Sentiment insight
        if analysis['sentiment']['overall'] == 'positive':
            insights.append("Overall positive emotional tone throughout the session.")
        elif analysis['sentiment']['overall'] == 'negative':
            insights.append("Challenging emotions present - important therapeutic opportunity.")
        
        return insights
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate therapeutic recommendations"""
        
        recommendations = []
        
        # Based on topics
        if 'anxiety' in analysis['topics']:
            recommendations.append("Consider anxiety management techniques in future sessions.")
        
        if 'relationships' in analysis['topics']:
            recommendations.append("Explore relationship dynamics and communication patterns.")
        
        # Based on engagement
        if analysis['engagement_score'] < 50:
            recommendations.append("Consider adjusting therapeutic approach to increase engagement.")
        
        return recommendations
    
    def _generate_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps for therapy"""
        
        steps = [
            "Continue building therapeutic rapport",
            "Follow up on identified themes",
            "Introduce relevant coping strategies"
        ]
        
        return steps
    
    def _generate_therapeutic_insights(self, analysis: Dict[str, Any], messages: List[TherapyMessage]) -> List[str]:
        """Generate detailed therapeutic insights"""
        
        insights = [
            f"Session showed {analysis['engagement_score']}% engagement level",
            f"Primary therapeutic themes: {', '.join(analysis['topics'])}",
            f"Emotional tone: {analysis['sentiment']['overall']}"
        ]
        
        return insights
    
    def _get_engagement_level(self, score: float) -> str:
        """Convert engagement score to descriptive level"""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    async def _create_pdf_report(
        self,
        session: TherapySession,
        content: Dict[str, Any],
        report_type: str
    ) -> str:
        """Create PDF report from content"""
        
        filename = f"report_{session.id}_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(self.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        story.append(Paragraph(content['title'], title_style))
        story.append(Spacer(1, 12))
        
        # Session Info
        story.append(Paragraph("Session Information", styles['Heading2']))
        for key, value in content['session_info'].items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add other content sections
        for section_key, section_content in content.items():
            if section_key not in ['title', 'session_info'] and isinstance(section_content, dict):
                story.append(Paragraph(section_key.replace('_', ' ').title(), styles['Heading2']))
                for key, value in section_content.items():
                    if isinstance(value, list):
                        story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", styles['Normal']))
                        for item in value:
                            story.append(Paragraph(f"• {item}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return file_path
    
    async def get_report_file_path(self, report_id: int) -> str:
        """Get file path for report ID"""
        # This would typically query the database for the actual file path
        # For now, return a placeholder
        return None
    
    async def delete_report_file(self, report_id: int) -> bool:
        """Delete report file"""
        file_path = await self.get_report_file_path(report_id)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    async def generate_session_analytics(
        self,
        session: TherapySession,
        messages: List[TherapyMessage]
    ) -> Dict[str, Any]:
        """Generate real-time analytics for a session"""
        
        analysis = await self._analyze_session(session, messages)
        
        return {
            "session_id": session.id,
            "analytics": analysis,
            "charts": {
                "mood_distribution": analysis['mood_distribution'],
                "engagement_over_time": [analysis['engagement_score']],  # Would be time-series in real implementation
                "topic_coverage": analysis['topics']
            },
            "summary": {
                "total_messages": analysis['total_messages'],
                "duration": analysis['session_duration_minutes'],
                "main_topics": analysis['topics'][:3],
                "engagement_level": self._get_engagement_level(analysis['engagement_score'])
            }
        }


# Global report service instance
report_service = ReportService()