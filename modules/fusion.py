"""
Fusion Logic Module
Combines text and visual highlight detections
"""

from typing import List, Dict
import json


class HighlightFusion:
    """Merges text and visual highlight detections"""
    
    def __init__(self, overlap_threshold: float = 5.0):
        """
        Initialize fusion logic
        
        Args:
            overlap_threshold: Time window (seconds) to consider overlaps
        """
        self.overlap_threshold = overlap_threshold
    
    def fuse(self, text_highlights: List[Dict], visual_highlights: List[Dict]) -> List[Dict]:
        """
        Merge text and visual highlights
        
        Args:
            text_highlights: List of text-based highlights
            visual_highlights: List of visual highlights
            
        Returns:
            Fused list of final highlights
        """
        fused = []
        used_text_indices = set()
        used_visual_indices = set()
        
        # First, try to merge overlapping highlights
        for i, text_hl in enumerate(text_highlights):
            text_time = text_hl.get("timestamp", 0)
            
            best_match_idx = None
            best_match_score = 0
            
            for j, visual_hl in enumerate(visual_highlights):
                visual_time = visual_hl.get("timestamp", 0)
                
                # Check if within threshold
                if abs(text_time - visual_time) <= self.overlap_threshold:
                    # Combined score
                    combined_score = text_hl.get("score", 5) + visual_hl.get("score", 0.5) * 2
                    
                    if combined_score > best_match_score:
                        best_match_score = combined_score
                        best_match_idx = j
            
            # Create fused highlight
            if best_match_idx is not None and best_match_idx not in used_visual_indices:
                visual_hl = visual_highlights[best_match_idx]
                used_visual_indices.add(best_match_idx)
                
                fused.append({
                    "timestamp": text_time,
                    "description": text_hl.get("description", "Exciting play"),
                    "score": best_match_score,
                    "source": "fused",
                    "text_score": text_hl.get("score", 5),
                    "visual_score": visual_hl.get("score", 0.5)
                })
                used_text_indices.add(i)
        
        # Add unmatched text highlights
        for i, text_hl in enumerate(text_highlights):
            if i not in used_text_indices:
                fused.append({
                    "timestamp": text_hl.get("timestamp", 0),
                    "description": text_hl.get("description", "Exciting play"),
                    "score": text_hl.get("score", 5),
                    "source": "text",
                    "text_score": text_hl.get("score", 5),
                    "visual_score": 0
                })
        
        # Add unmatched visual highlights (if space remaining)
        for j, visual_hl in enumerate(visual_highlights):
            if j not in used_visual_indices and len(fused) < 10:
                fused.append({
                    "timestamp": visual_hl.get("timestamp", 0),
                    "description": visual_hl.get("description", "Visual highlight"),
                    "score": visual_hl.get("score", 0.5) * 2,
                    "source": "visual",
                    "text_score": 0,
                    "visual_score": visual_hl.get("score", 0.5)
                })
        
        # Sort by score and return top highlights
        fused.sort(key=lambda x: x.get("score", 0), reverse=True)
        return fused[:5]  # Return top 5 final highlights
    
    def save_fused_highlights(self, highlights: List[Dict], output_path: str):
        """
        Save fused highlights to JSON
        
        Args:
            highlights: List of fused highlights
            output_path: Path to save the file
        """
        from pathlib import Path
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(highlights, f, indent=2, ensure_ascii=False)

