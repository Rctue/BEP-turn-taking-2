import time

class VideoEyeBrightnessController:
    """
    Controls Misty robot's eye brightness using video playback.
    
    This controller manages transitions between bright and dim eye states
    using pre-created videos to maintain natural blinking behavior.
    """
    
    # Constants for transition styles
    DIRECT = "direct"
    SMOOTH = "smooth"
    
    def __init__(self, misty_robot, transition_style=DIRECT):
        """
        Initialize the Video Eye Brightness Controller
        
        Args:
            misty_robot: Instance of the Misty robot
            transition_style: "direct" or "smooth"
        """
        self.misty = misty_robot
        self.transition_style = transition_style
        self.current_state = "listening"  # or "speaking"
        
        # Video file names WITH extensions
        self.bright_loop_video = "loop_bright.mp4"
        self.dim_loop_video = "loop_dim.mp4"
        self.bright_to_dim_video = "bright_to_dim_smooth.mp4"
        self.dim_to_bright_video = "dim_to_bright_smooth.mp4"
        
        # Transition duration (in seconds)
        self.transition_duration = 1.0
        
        # Initialize - start in listening mode
        self._display_dim_video()
        
    def set_transition_style(self, style):
        """
        Set transition style to direct or smooth
        
        Args:
            style: "direct" or "smooth"
        """
        if style.lower() in ["d", "direct", self.DIRECT]:
            self.transition_style = self.DIRECT
        else:
            self.transition_style = self.SMOOTH
    
    def set_speaking_mode(self):
        """
        Set eyes to bright mode (robot is speaking)
        """
        if self.current_state == "speaking":
            return  # Already in speaking mode
            
        print(f"BRIGHT MODE: Robot is now talking (Style: {self.transition_style})")
        
        # Stop any current videos
        self.misty.stop_video()
        
        if self.transition_style == self.DIRECT:
            # Just switch directly to the bright video
            self._display_bright_video()
        else:
            # For smooth transition, play transition video first
            self.misty.display_video(
                fileName=self.dim_to_bright_video,
                layer="DefaultVideoLayer"
            )
            
            # Then switch to the bright loop after transition completes
            time.sleep(self.transition_duration)
            self._display_bright_video()
        
        self.current_state = "speaking"
    
    def set_listening_mode(self):
        """
        Set eyes to dim mode (robot is listening)
        """
        if self.current_state == "listening":
            return  # Already in listening mode
            
        print(f"DIM MODE: Robot is now listening (Style: {self.transition_style})")
        
        # Stop any current videos
        self.misty.stop_video()
        
        if self.transition_style == self.DIRECT:
            # Just switch directly to the dim video
            self._display_dim_video()
        else:
            # For smooth transition, play transition video first
            self.misty.display_video(
                fileName=self.bright_to_dim_video,
                layer="DefaultVideoLayer"
            )
            
            # Then switch to the dim loop after transition completes
            time.sleep(self.transition_duration)
            self._display_dim_video()
        
        self.current_state = "listening"
    
    def _display_bright_video(self):
        """Display the bright eyes loop video"""
        self.misty.display_video(
            fileName=self.bright_loop_video,
            layer="DefaultVideoLayer",
            repeat=True  # Loop the video
        )
    
    def _display_dim_video(self):
        """Display the dim eyes loop video"""
        self.misty.display_video(
            fileName=self.dim_loop_video,
            layer="DefaultVideoLayer",
            repeat=True  # Loop the video
        )