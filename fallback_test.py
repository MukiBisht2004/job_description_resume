#!/usr/bin/env python3
"""
Test fallback functionality when original DOCX content is invalid
"""

import requests
import json
from docx import Document
import io
import base64

BACKEND_URL = "https://resumeai-29.preview.emergentagent.com/api"

def test_fallback_with_invalid_docx():
    """Test fallback when original_docx_content is invalid"""
    session = requests.Session()
    
    print("Testing fallback functionality with invalid DOCX content...")
    
    job_description = "Software Engineer position requiring Python and API development skills."
    
    # Test with invalid base64 content to trigger fallback
    data = {
        'resume_text': "John Doe\nSoftware Developer\nExperience with Python and web development.",
        'job_description': job_description,
        'original_docx_content': "invalid_base64_content_that_should_trigger_fallback"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/tailor-resume", data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis_id = result.get("analysis_id")
                print(f"✅ Tailoring succeeded with invalid DOCX: {analysis_id}")
                
                # Test download to see if fallback formatting works
                download_response = session.get(f"{BACKEND_URL}/download-resume/{analysis_id}", timeout=30)
                
                if download_response.status_code == 200:
                    try:
                        fallback_doc = Document(io.BytesIO(download_response.content))
                        paragraphs = [p.text for p in fallback_doc.paragraphs if p.text.strip()]
                        
                        print(f"✅ Fallback DOCX created successfully with {len(paragraphs)} paragraphs")
                        print("Sample content:")
                        for i, para in enumerate(paragraphs[:5]):
                            print(f"  {i+1}. {para}")
                        
                        return True
                    except Exception as docx_error:
                        print(f"❌ Fallback DOCX is invalid: {str(docx_error)}")
                        return False
                else:
                    print(f"❌ Download failed: HTTP {download_response.status_code}")
                    return False
            else:
                print(f"❌ Tailoring failed: {result}")
                return False
        else:
            print(f"❌ Tailoring request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during fallback test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_fallback_with_invalid_docx()
    if success:
        print("\n🎉 Fallback functionality works correctly!")
    else:
        print("\n⚠️ Fallback functionality has issues.")