"""
Player Tracking Module
Tracks the player with the ball in video frames for smart cropping
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import json


class PlayerTracker:
    """Tracks the player with the ball in video frames"""
    
    def __init__(self):
        """Initialize the player tracker"""
        # Load HOG person detector (built into OpenCV)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Ball detection for finding player closest to ball
        self.lower_orange = np.array([5, 50, 50])
        self.upper_orange = np.array([25, 255, 255])
        
        # Tracking variables
        self.tracker = None
        self.tracked_bbox = None
    
    def detect_ball_position(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect basketball position in a single frame
        
        Args:
            frame: BGR frame from video
            
        Returns:
            (x, y) center coordinates of ball, or None if not found
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_orange, self.upper_orange)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area < 50 or area > 50000:
            return None
        
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        return (cx, cy)
    
    def detect_players(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect players (people) in a frame using HOG detector
        
        Args:
            frame: BGR frame from video
            
        Returns:
            List of (x, y, w, h) bounding boxes for detected players
        """
        # Resize frame for faster detection
        height, width = frame.shape[:2]
        scale = 1.0
        if width > 1280:
            scale = 1280.0 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame_resized = cv2.resize(frame, (new_width, new_height))
        else:
            frame_resized = frame
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            frame_resized,
            winStride=(8, 8),
            padding=(32, 32),
            scale=1.05,
            hitThreshold=0.6  # Lower threshold for better detection
        )
        
        # Scale boxes back to original size if needed
        if scale != 1.0:
            boxes = (boxes / scale).astype(int)
        
        # Filter and return bounding boxes
        player_boxes = []
        for (x, y, w, h) in boxes:
            # Filter by aspect ratio (players are taller than wide)
            if h > w * 0.8:  # Height should be at least 80% of width
                player_boxes.append((x, y, w, h))
        
        return player_boxes
    
    def find_player_with_ball(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Find the player most likely to have the ball
        
        Args:
            frame: BGR frame from video
            
        Returns:
            (x, y) center position of player with ball, or None
        """
        # Detect ball position
        ball_pos = self.detect_ball_position(frame)
        
        # Detect players
        players = self.detect_players(frame)
        
        if not players:
            return None
        
        # If ball detected, find player closest to ball
        if ball_pos:
            ball_x, ball_y = ball_pos
            min_dist = float('inf')
            closest_player = None
            
            for (x, y, w, h) in players:
                player_center_x = x + w // 2
                player_center_y = y + h // 2
                
                # Distance from ball to player center
                dist = np.sqrt((ball_x - player_center_x)**2 + (ball_y - player_center_y)**2)
                
                if dist < min_dist:
                    min_dist = dist
                    closest_player = (player_center_x, player_center_y)
            
            if closest_player and min_dist < 200:  # Ball within reasonable distance
                return closest_player
        
        # Fallback: find player closest to center of frame (often the ball handler)
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        min_dist = float('inf')
        center_player = None
        
        for (x, y, w, h) in players:
            player_center_x = x + w // 2
            player_center_y = y + h // 2
            
            dist = np.sqrt((center_x - player_center_x)**2 + (center_y - player_center_y)**2)
            
            if dist < min_dist:
                min_dist = dist
                center_player = (player_center_x, player_center_y)
        
        return center_player
    
    def track_player_with_ball(self, video_path: str, start_time: float = 0, 
                               duration: float = 30) -> List[Tuple[float, int, int]]:
        """
        Track the player with the ball throughout video clip
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration to track in seconds
            
        Returns:
            List of (timestamp, x, y) tuples for player positions
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Seek to start time
        frame_start = int(start_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_start)
        
        positions = []
        frame_num = 0
        last_position = None
        
        # Use CSRT tracker for smooth tracking between detections
        tracker = None
        tracked_bbox = None
        
        # Smoothing: use moving average for position
        position_history = []
        history_size = 7  # Larger history for smoother tracking
        
        # Process every Nth frame for detection (every 0.5 seconds)
        detection_interval = int(fps * 0.5)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = start_time + (frame_num / fps)
            if current_time > start_time + duration:
                break
            
            player_pos = None
            
            # Detection phase: detect player with ball
            if frame_num % detection_interval == 0 or tracker is None:
                player_pos = self.find_player_with_ball(frame)
                
                if player_pos:
                    # Initialize or reinitialize tracker
                    # Create bounding box around player
                    px, py = player_pos
                    bbox_size = 150  # Estimated player size
                    bbox = (px - bbox_size//2, py - bbox_size//2, bbox_size, bbox_size)
                    bbox = tuple(max(0, int(v)) for v in bbox)
                    
                    if tracker is None:
                        tracker = cv2.TrackerCSRT_create()
                        tracker.init(frame, bbox)
                        tracked_bbox = bbox
                        last_position = player_pos
                    else:
                        # Reinitialize tracker if detection found
                        tracker = cv2.TrackerCSRT_create()
                        tracker.init(frame, bbox)
                        tracked_bbox = bbox
                        last_position = player_pos
            
            # Tracking phase: use tracker to follow player
            if tracker is not None:
                success, bbox = tracker.update(frame)
                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    player_pos = (x + w // 2, y + h // 2)
                    tracked_bbox = bbox
                    last_position = player_pos
                else:
                    # Tracker lost, use last position
                    if last_position:
                        player_pos = last_position
            
            # Fallback if no position found
            if player_pos is None:
                if last_position is not None:
                    player_pos = last_position
                else:
                    # Use frame center as fallback
                    h, w = frame.shape[:2]
                    player_pos = (w // 2, h // 2)
            
            # Add to history for smoothing
            position_history.append(player_pos)
            if len(position_history) > history_size:
                position_history.pop(0)
            
            # Average position for smoothing (weighted towards recent positions)
            weights = np.linspace(0.5, 1.0, len(position_history))
            avg_x = int(np.average([p[0] for p in position_history], weights=weights))
            avg_y = int(np.average([p[1] for p in position_history], weights=weights))
            
            positions.append((current_time, avg_x, avg_y))
            
            frame_num += 1
        
        cap.release()
        return positions
    
    def get_crop_region(self, player_x: int, player_y: int, frame_width: int, 
                       frame_height: int, crop_width: int, crop_height: int) -> Tuple[int, int]:
        """
        Calculate crop region centered on player position
        
        Args:
            player_x: Player X position
            player_y: Player Y position
            frame_width: Full frame width
            frame_height: Full frame height
            crop_width: Desired crop width
            crop_height: Desired crop height
            
        Returns:
            (crop_x, crop_y) top-left corner of crop region
        """
        # Center crop on player, offset slightly upward to show player better
        offset_y = int(crop_height * 0.1)  # Shift up 10% to show player better
        
        crop_x = max(0, min(player_x - crop_width // 2, frame_width - crop_width))
        crop_y = max(0, min(player_y - crop_height // 2 - offset_y, frame_height - crop_height))
        
        return (crop_x, crop_y)

