import time
import threading
from Misty_commands import Misty
def delay_playback(misty, delay, video_name):
    t_0= time.time()
    if delay < 0.5:
        delay = 0.5

    misty.set_video_display_settings(
        layer="DefaultVideoLayer",
        deleted=True
    )

    time.sleep(0.5)
    #print(time.time()-t_0)
    if video_name != None:
        time.sleep(delay)
        #print(time.time()-t_0)
        # Set and play the first video
        misty.set_video_display_settings(
            layer="DefaultVideoLayer",
            opacity=1.0,
            visible=True,
            width=480,
            height=272,
            stretch="UniformToFill",
            repeat=True,
            placeOnTop=True
        )
        #print(time.time()-t_0)
        misty.display_video(video_name, "DefaultVideoLayer", False)
        time.sleep(0.5
                   )
        #print(time.time()-t_0)

def thread_playback (misty, delay, video_name):
    x = threading.Thread(target=delay_playback, args=(misty, 10, "loop_dim.mp4",))
    x.start()
    return x

def delete_video_layer(misty):
    misty.set_video_display_settings(
        layer="DefaultVideoLayer",
        deleted=True
    )

if __name__ == "__main__":
        robot_ip = "192.168.0.104"
        misty    = Misty(ip_address=robot_ip)
        misty.speak("hello! I am Misty and today we are going to talk about your dream house.")
        delay_playback(misty, 10, "loop_bright.mp4")
        input("press enter to continue")
        x = thread_playback(misty, 10, "loop_dim.mp4")
        misty.speak("hello! I am Misty and today we are going to talk about your dream house.")
        #print("stop thread")
        x.join()
        #print("finish")



