# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:30:53 2024

@author: 20212599
"""

import requests
from requests import request, Response
import datetime
from collections import namedtuple
import cv2
import base64
import numpy as np


class Misty:
    def __init__(self, ip_address: str):
        # Correct base URL with the http:// scheme and Misty's IP address
        self.base_url = f"http://{ip_address}/api/"
        self.ip = ip_address

    def _generic_request(self, verb: str, endpoint: str, **kwargs):
        url = "http://" + self.ip + "/api/" + endpoint
        return request(verb, url, **kwargs)

    def get_request(self, endpoint: str, **kwargs):
        return self._generic_request("get", endpoint, **kwargs)
    
    def post_request(self, endpoint: str, json=None):
        """Send a POST request to Misty's API"""
        url = self.base_url + endpoint  # Full URL
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=json, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error in POST request: {e}")
            return None
    
    def get_audio_list(self) -> requests.Response:
        """Retrieve a list of audio files stored on Misty"""
        url = self.base_url + "audio/list"  # Full URL for the GET request
        try:
            response = requests.get(url)  # Perform GET request
            response.raise_for_status()  # Raise error for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving audio list: {e}")
            return None
        
    def enable_camera_service(self) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#enable_camera_service"""

        return self.post_request("services/camera/enable")

    def get_image_list(self) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#get_image_list"""

        return self.get_request("images/list")

    def play_audio(self, audioFile: str) -> requests.Response:
        """Play an audio file on Misty."""
        url = self.base_url + "audio/play"
        json = {"fileName" : audioFile}
        try:
            response = requests.post(url, json=json)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error playing audio: {e}")
            return None

    def speak(self,
              text: str = None,
              pitch: float = None,
              speechRate: float = None,
              voice: str = None,
              flush: bool = None,
              utteranceId: str = None,
              language: str = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#speak"""

        json = {
            "text": text,
            "pitch": pitch,
            "speechRate": speechRate,
            "voice": voice,
            "flush": flush,
            "utteranceId": utteranceId,
            "language": language
        }

        return self.post_request("tts/speak", json=json)
    
    def take_picture(self,
                     base64: bool = None,
                     fileName: str = None,
                     width: int = None,
                     height: int = None,
                     displayOnScreen: bool = None,
                     overwriteExisting: bool = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#take_picture"""

        json = {
            "base64": base64,
            "fileName": fileName,
            "width": width,
            "height": height,
            "displayOnScreen": displayOnScreen,
            "overwriteExisting": overwriteExisting
        }

        return self.get_request("cameras/rgb", json=json)

    def display_image(self,
                      fileName: str = None,
                      alpha: float = None,
                      layer: str = None,
                      isURL: bool = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#display_image"""

        json = {
            "fileName": fileName,
            "alpha": alpha,
            "layer": layer,
            "isURL": isURL
        }

        return self.post_request("images/display", json=json)

    def move_head(self,
                  pitch: float = None,
                  roll: float = None,
                  yaw: float = None,
                  velocity: float = None,
                  duration: float = None,
                  units: str = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#move_head"""

        json = {
            "pitch": pitch,
            "roll": roll,
            "yaw": yaw,
            "velocity": velocity,
            "duration": duration,
            "units": units
        }

        return self.post_request("head", json=json)

    def enable_audio_service(self) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#enable_audio_service"""

        return self.post_request("services/audio/enable")
    
    def take_picture(self,
                     base64: bool = None,
                     fileName: str = None,
                     width: int = None,
                     height: int = None,
                     displayOnScreen: bool = None,
                     overwriteExisting: bool = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#take_picture"""

        json = {
            "base64": base64,
            "fileName": fileName,
            "width": width,
            "height": height,
            "displayOnScreen": displayOnScreen,
            "overwriteExisting": overwriteExisting
        }

        return self.get_request("cameras/rgb", json=json)
    
    def save_image(self,
                   fileName: str = None,
                   data: str = None,
                   width: int = None,
                   height: int = None,
                   immediatelyApply: bool = None,
                   overwriteExisting: bool = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#save_image"""

        json = {
            "fileName": fileName,
            "data": data,
            "width": width,
            "height": height,
            "immediatelyApply": immediatelyApply,
            "overwriteExisting": overwriteExisting
        }

        return self.post_request("images", json=json)

    def get_image(self, fileName: str = None, base64: bool = None) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#get_image"""

        json = {"fileName": fileName, "base64": base64}

        return self.get_request("images", json=json)
    
    def get_camera_details(self) -> Response:
        """https://docs.mistyrobotics.com/misty-ii/reference/rest/#get_camera_details"""

        return self.get_request("camera")
    
    def get_head_position(self) -> dict:
        """Retrieve the current head position of Misty."""
        response = self.get_request("head")  # Assuming "head" endpoint gives current head position
        print("hier is hij geweest")
        return response.json().get('result', {})
        #deze functie werkt niet idk hoe ik hem moet fixen. 
        



    
def getMistyImage(misty):
    result = misty.take_picture(base64 = True, fileName = "TempImage01", width = 800, height = 600, displayOnScreen = False, overwriteExisting = True)
    if (result.json()['status'] == "Success"):
        returnvalue = True
        result = misty.get_image(fileName = "TempImage01.jpg", base64 = True)
        image = result.json()['result']['base64']  # raw data with base64 encoding
        np_data = np.fromstring(base64.b64decode(image),np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)

    else:
        returnvalue = False
        img = None
    return returnvalue, img
