"""
Text-based Highlight Detection Module
Uses DeepSeek API to analyze transcripts and find exciting moments
"""

import json
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class HighlightFinder:
    """Finds highlights in transcripts using AI analysis"""
    
    def __init__(self):
        """Initialize the highlight finder"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def find_highlights(self, transcript: Dict, top_k: int = 5) -> List[Dict]:
        """
        Analyze transcript to find exciting moments
        
        Args:
            transcript: Transcript dictionary with segments
            top_k: Number of highlights to return
            
        Returns:
            List of highlight dictionaries with timestamps and descriptions
        """
        if not self.api_key:
            print("Warning: No OPENROUTER_API_KEY found in environment")
            return []
        
        try:
            # Build prompt
            segments_text = self._format_segments(transcript.get("segments", []))
            
            prompt = f"""Analyze this NBA video transcript and identify the TOP {top_k} most exciting moments.

Transcription:
{segments_text}

For each exciting moment, provide:
1. Exact timestamp (start time)
2. Brief description (max 10 words)
3. Excitement score (1-10)

Return ONLY a valid JSON array in this exact format:
[
  {{"timestamp": float, "description": "string", "score": int}},
  ...
]

Be selective - only include truly exciting plays like dunks, game-winners, amazing assists, blocks, or clutch moments."""

            # Call DeepSeek API
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract and parse JSON from response
            content = data["choices"][0]["message"]["content"]
            
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            highlights = json.loads(content)
            
            # Validate and return
            if isinstance(highlights, list):
                return highlights[:top_k]
            else:
                return []
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return []
        except requests.RequestException as e:
            print(f"API error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error finding highlights: {e}")
            return []
    
    def _format_segments(self, segments: List[Dict]) -> str:
        """
        Format transcript segments for the prompt
        
        Args:
            segments: List of transcript segments
            
        Returns:
            Formatted string
        """
        formatted = []
        for seg in segments:
            start_time = seg.get("start", 0)
            text = seg.get("text", "").strip()
            formatted.append(f"[{start_time:.1f}s] {text}")
        
        return "\n".join(formatted)

