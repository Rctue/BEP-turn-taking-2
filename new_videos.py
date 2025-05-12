##############################################################################
# ░░░ IMPLEMENTATION OF EYE TRANSITION STYLE░░░
##############################################################################
#This file displays 4 videos to simulate an 'idle' state when Misty is silent, where the robot's eyes have a 70% brightness, and an 'active' state when Misty is speaking, where the robot's eyes have maximum brightness (100%). These states alternate through a direct change and a smooth change (the smooth change implements two other videos).  
#BE AWARE: This implementation only works if you upload the videos on the web interface of the Misty robot
#The following videos (find them in this repository) are used for this part: loop_bright.mp4, loop_dim.mp4, bright_to_dim_smooth.mp4, dim_to_bright_smooth.mp4

import time
from mistyPy.Robot import Robot
from mistyPy.Events import Events
from mistyPy.EventFilters import EventFilters


class Video_player :
    SMOOTH = "smooth"
    DIRECT = "direct"
    def __init__(self, robot, transition_style):
        self.misty_robot = robot
        self.transition_style = transition_style
        self.current_state = None

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

    def set_listening_mode(self):
        """
        Set eyes to dim mode (robot is listening)
        """
        
        if self.current_state == "listening":
            return  
            
        print(f"DIM MODE: Robot is now listening (Style: {self.transition_style})")
        self.current_state = "listening"
        if self.transition_style == self.DIRECT :
            self.misty_robot.display_video("loop_dim.mp4","DefaultVideoLayer",False)
        elif self.transition_style == self.SMOOTH :
            self.misty_robot.display_video("bright_to_dim_smooth.mp4","DefaultVideoLayer",False)
            time.sleep(0.1)
            self.misty_robot.display_video("loop_dim.mp4","DefaultVideoLayer",False)
    
    def set_speaking_mode(self):
        
        if self.current_state == "speaking":
            return
        print(f"BRIGHT MODE: Robot is now talking (Style: {self.transition_style})")

        self.current_state = "speaking"
        if self.transition_style == self.DIRECT :
            self.misty_robot.display_video("loop_bright.mp4","DefaultVideoLayer",False)
        elif self.transition_style == self.SMOOTH:
            self.misty_robot.display_video("dim_to_bright_smooth.mp4","DefaultVideoLayer",False)
            time.sleep(0.1)
            self.misty_robot.display_video("loop_bright.mp4","DefaultVideoLayer",False)
    
#Mock robot implementation that allowed for testing the code without a robot        
# if __name__=="__main__":
#     ROBOT_IP = "192.168.0.100"
#     misty_robot = Robot(ROBOT_IP)
#     transition_style = Video_player.SMOOTH # if eye_controller.lower() == "s" else VideoEyeBrightnessController.DIRECT
#     eye_controller = Video_player(misty_robot, transition_style=transition_style)

# class MockRobot:
#     def display_video(self, video_file, layer, loop):
#         print(f"[MOCK] Playing video: {video_file} on layer {layer} with loop={loop}")

# if __name__ == "__main__":
#     mock_robot = MockRobot()
#     transition_style = Video_player.SMOOTH
#     eye_controller = Video_player(mock_robot, transition_style)

#     # Simulate actions
#     eye_controller.set_speaking_mode()
#     time.sleep(1)
#     eye_controller.set_listening_mode()
#     time.sleep(1)
#     eye_controller.set_speaking_mode()

#Add to the hardcoded
#from new_videos import Video_player
# transition_style = Video_player.SMOOTH if condition_eye.lower() == "s" else Video_player.DIRECT
#             eye_controller = Video_player(misty, transition_style=transition_style)
#             print(f"LED controller initialized with {transition_style} transitions")
# eye_controller.set_speaking_mode()                
# misty.speak(...)
# eye_controller.set_listening_mode()