#!/usr/bin/env python3
"""
AI Resume Analyzer - Demo Preparation Utilities
Hackathon demo script with sample presentation lines and troubleshooting tips
"""

import os
import sys
import time
from pathlib import Path

class DemoPreparation:
    """Demo preparation utilities for hackathon presentation"""
    
    def __init__(self):
        self.demo_checklist = [
            "✅ Environment setup complete (.env configured)",
            "✅ Supabase session pooler configured (recommended)",
            "✅ Sample resume files ready (samples/)",
            "✅ Sample job descriptions ready (sample_jobs/)",
            "✅ Internet connection stable",
            "✅ Browser ready for Streamlit app",
            "✅ Backup video files prepared",
            "✅ Demo script practiced"
        ]
        
        self.troubleshooting_tips = {
            "API Key Issues": [
                "Check .env file has correct OPENAI_API_KEY",
                "Verify API key has sufficient credits",
                "Test API connection with simple call"
            ],
            "Database Connection Issues": [
                "Verify Supabase configuration in .env file",
                "Test session pooler connection with setup_supabase_pooler.py",
                "Check if USE_SESSION_POOLER=true and SUPABASE_POOLER_URL is set",
                "Fallback to direct connection if pooler fails"
            ],
            "Video Generation Fails": [
                "Check internet connection for Gemini API",
                "Fallback to MoviePy generation available",
                "Use pre-generated demo videos if needed"
            ],
            "File Upload Issues": [
                "Use sample files from samples/ directory",
                "Check file format (PDF/DOCX supported)",
                "Verify file size under 10MB"
            ],
            "Streamlit Not Loading": [
                "Check port 8501 is available",
                "Try different browser",
                "Restart application with run.sh"
            ]
        }
    
    def print_60_second_pitch(self):
        """Print the 60-second hackathon pitch script"""
        print("🎤 60-SECOND HACKATHON PITCH SCRIPT")
        print("=" * 50)
        print()
        
        pitch_segments = [
            {
                "time": "0-10s",
                "content": "Hi judges! I'm presenting the AI Resume Analyzer - a tool that transforms resume screening from hours to seconds using AI-powered analysis and personalized video generation."
            },
            {
                "time": "10-20s", 
                "content": "The problem: Recruiters spend 6 seconds per resume, missing great candidates. Job seekers struggle to tailor applications and stand out in crowded markets."
            },
            {
                "time": "20-35s",
                "content": "Our solution: Upload any resume, get instant AI analysis with strengths, weaknesses, and improvement suggestions. Compare against job descriptions for skill gap analysis. Generate personalized 10-second video pitches automatically."
            },
            {
                "time": "35-45s",
                "content": "Key features: Multi-language support, OCR fallback for scanned documents, job-specific optimization advice, and professional video generation using Google's Gemini AI."
            },
            {
                "time": "45-55s",
                "content": "Built with Python, Streamlit, OpenAI GPT, and Google Gemini. Fully functional with database persistence, ready for production deployment."
            },
            {
                "time": "55-60s",
                "content": "This democratizes professional resume services and video creation, helping job seekers compete effectively. Thank you!"
            }
        ]
        
        for segment in pitch_segments:
            print(f"⏱️  {segment['time']}: {segment['content']}")
            print()
        
        print("💡 DELIVERY TIPS:")
        print("• Speak clearly and confidently")
        print("• Show the live demo during 20-35s segment")
        print("• Have backup screenshots ready")
        print("• Practice timing with a stopwatch")
        print("• End with enthusiasm and eye contact")
        print()
    
    def print_demo_script(self):
        """Print the detailed demo script with spoken lines"""
        print("🎬 DETAILED DEMO SCRIPT")
        print("=" * 50)
        print()
        
        demo_steps = [
            {
                "step": "1. Introduction",
                "action": "Open browser to localhost:8501",
                "spoken": "Welcome to the AI Resume Analyzer! Let me show you how this transforms resume screening."
            },
            {
                "step": "2. File Upload Demo",
                "action": "Upload sample_resume_en.txt",
                "spoken": "I'll upload this sample resume. Notice it supports PDF, DOCX, and even scanned documents with OCR fallback."
            },
            {
                "step": "3. Text Extraction",
                "action": "Show extracted text section",
                "spoken": "The system extracts and cleans the text automatically. You can verify the extraction quality here."
            },
            {
                "step": "4. AI Analysis",
                "action": "Wait for GPT analysis to complete",
                "spoken": "Now watch as GPT analyzes the resume, identifying strengths, weaknesses, and providing actionable suggestions."
            },
            {
                "step": "5. Results Display",
                "action": "Expand analysis results",
                "spoken": "Here's the structured analysis - specific strengths with evidence, clear improvement areas, and professional suggestions."
            },
            {
                "step": "6. Job Comparison",
                "action": "Add sample job description",
                "spoken": "Let's add a job description to see skill gap analysis and get tailored optimization advice."
            },
            {
                "step": "7. Video Generation",
                "action": "Click Generate Pitch Video",
                "spoken": "Finally, we'll generate a personalized 10-second video pitch using AI. This creates professional presentations automatically."
            },
            {
                "step": "8. Video Playback",
                "action": "Play generated video",
                "spoken": "Here's the result - a professional video pitch that job seekers can use on LinkedIn or in applications."
            },
            {
                "step": "9. Download Features",
                "action": "Show download buttons",
                "spoken": "Users can download both the analysis report and the video for their job applications."
            },
            {
                "step": "10. Closing",
                "action": "Show additional features",
                "spoken": "The system also includes history tracking, multi-language support, and database persistence. Questions?"
            }
        ]
        
        for i, step in enumerate(demo_steps, 1):
            print(f"🎯 STEP {i}: {step['step']}")
            print(f"   Action: {step['action']}")
            print(f"   Say: \"{step['spoken']}\"")
            print()
        
        print("⚠️  BACKUP PLAN:")
        print("• Have pre-generated videos ready if live generation fails")
        print("• Use sample files that you've tested beforehand")
        print("• Keep screenshots of key features as backup")
        print("• Practice the demo multiple times")
        print()
    
    def run_demo_checklist(self):
        """Interactive demo checklist"""
        print("📋 DEMO CHECKLIST")
        print("=" * 50)
        print()
        
        print("Please verify each item before your demo:")
        print()
        
        for item in self.demo_checklist:
            print(f"  {item}")
        
        print()
        input("Press Enter when all items are checked...")
        
        # Quick system check
        print("\n🔍 Running quick system check...")
        
        checks = [
            ("app.py exists", os.path.exists("app.py")),
            (".env file exists", os.path.exists(".env")),
            ("samples directory exists", os.path.exists("samples")),
            ("sample_jobs directory exists", os.path.exists("sample_jobs")),
            ("requirements.txt exists", os.path.exists("requirements.txt"))
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All checks passed! You're ready for the demo!")
        else:
            print("\n⚠️  Some checks failed. Please fix the issues above.")
        
        print()
    
    def print_troubleshooting_guide(self):
        """Print troubleshooting guide for common demo issues"""
        print("🔧 TROUBLESHOOTING GUIDE")
        print("=" * 50)
        print()
        
        for issue, solutions in self.troubleshooting_tips.items():
            print(f"❗ {issue}:")
            for solution in solutions:
                print(f"   • {solution}")
            print()
        
        print("🆘 EMERGENCY CONTACTS:")
        print("   • Have team member ready to help with technical issues")
        print("   • Keep backup laptop/device ready")
        print("   • Have mobile hotspot as internet backup")
        print()
    
    def create_demo_files(self):
        """Create demo-specific files and shortcuts"""
        print("📁 Creating demo files...")
        
        # Create demo shortcuts script
        demo_shortcuts = """#!/bin/bash
# Quick demo shortcuts

echo "🚀 AI Resume Analyzer Demo Shortcuts"
echo "=================================="
echo "1. Start app: ./run.sh"
echo "2. Open browser: open http://localhost:8501"
echo "3. Sample files: ls samples/"
echo "4. Sample jobs: ls sample_jobs/"
echo "5. Check logs: tail -f ~/.streamlit/logs/streamlit.log"
echo ""
echo "Demo files ready in samples/ and sample_jobs/"
"""
        
        with open("demo_shortcuts.sh", "w") as f:
            f.write(demo_shortcuts)
        
        os.chmod("demo_shortcuts.sh", 0o755)
        
        # Create quick demo notes
        demo_notes = """# AI Resume Analyzer - Demo Notes

## Key Selling Points
- Instant AI-powered resume analysis
- Personalized video pitch generation
- Job-specific optimization advice
- Multi-language support (EN/RO)
- Professional video creation with Gemini AI

## Technical Highlights
- Built with modern Python stack
- OpenAI GPT integration
- Google Gemini Veo 3 for video generation
- Supabase database for persistence
- Streamlit for rapid UI development

## Demo Flow (60 seconds)
1. Upload resume (10s)
2. Show AI analysis (20s)
3. Add job description (10s)
4. Generate video pitch (15s)
5. Show results and downloads (5s)

## Backup Plans
- Pre-generated videos in case of API issues
- Screenshots of key features
- Sample data ready to go
- Team member as technical backup

## Questions to Anticipate
- "How accurate is the AI analysis?"
- "What file formats are supported?"
- "How long does video generation take?"
- "Is this ready for production?"
- "What's the business model?"
"""
        
        with open("DEMO_NOTES.md", "w") as f:
            f.write(demo_notes)
        
        print("✅ Created demo_shortcuts.sh")
        print("✅ Created DEMO_NOTES.md")
        print()

def main():
    """Main demo preparation interface"""
    demo = DemoPreparation()
    
    print("🎪 AI RESUME ANALYZER - DEMO PREPARATION")
    print("=" * 60)
    print()
    
    while True:
        print("Choose an option:")
        print("1. 📋 Run demo checklist")
        print("2. 🎤 Show 60-second pitch script")
        print("3. 🎬 Show detailed demo script")
        print("4. 🔧 Show troubleshooting guide")
        print("5. 📁 Create demo files")
        print("6. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            demo.run_demo_checklist()
        elif choice == "2":
            demo.print_60_second_pitch()
        elif choice == "3":
            demo.print_demo_script()
        elif choice == "4":
            demo.print_troubleshooting_guide()
        elif choice == "5":
            demo.create_demo_files()
        elif choice == "6":
            print("Good luck with your demo! 🍀")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()