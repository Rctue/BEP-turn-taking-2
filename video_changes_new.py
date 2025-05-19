import time
import threading
from Misty_commands import Misty
is_playing = False

#DON'T FORGET: 
# !!!!Always choose open_70.jpg from the web interface of Misty!!!
# Otherwise you can see for a brief moment the default eye image. 

def delay_playback(misty, delay, video_name):
    global is_playing
    if is_playing:
         print("Already changing video")
         return
    is_playing = True 
    # t_0= time.time()
    if delay < 0.5:
        delay = 0.5
    time.sleep(delay- 0.5)
    misty.set_video_display_settings(
        layer="DefaultVideoLayer",
        deleted=True
    )

    # time.sleep(0.5)
    #print(time.time()-t_0)
    if video_name != None:
        # time.sleep(delay)
        #print(time.time()-t_0)
        # Set and play the first video
        if video_name == "bright_to_dim_smooth.mp4" or  video_name == "dim_to_bright_smooth.mp4":
            misty.set_video_display_settings(
                layer="DefaultVideoLayer",
                opacity=1.0,
                visible=True,
                width=480,
                height=272,
                stretch="UniformToFill",
                repeat=False,
                placeOnTop=True
            )
            #print(time.time()-t_0)
            misty.display_video(video_name, "DefaultVideoLayer", False)
        else:
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
        # time.sleep(0.5
        #            )
        #print(time.time()-t_0)
    is_playing = False

def thread_playback (misty, delay, video_name):
    x = threading.Thread(target=delay_playback, args=(misty, delay, video_name,))
    x.start()
    return x

def delete_video_layer(misty):
    misty.set_video_display_settings(
        layer="DefaultVideoLayer",
        deleted=True
    )

if __name__ == "__main__":
        robot_ip = "192.168.0.100"
        misty    = Misty(ip_address=robot_ip)
        # misty.speak("hello! I am Misty and today we are going to talk about your dream house.")
        # delay_playback(misty, 10, "loop_bright.mp4")
        # input("press enter to continue")
        # x = thread_playback(misty, 10, "loop_dim.mp4")
        misty.speak("hello! I am Misty and today we are going to talk about your dream house.")
        #print("stop thread")
        delay_playback(misty, 10, "bright_to_dim_smooth.mp4")
        # x.join()
        #print("finish")
        
    


