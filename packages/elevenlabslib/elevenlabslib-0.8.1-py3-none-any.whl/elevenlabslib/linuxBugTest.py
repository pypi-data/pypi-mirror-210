import logging
import time

import sounddevice

from elevenlabslib import *
import keyring
import pyaudio


#Config data (fill this in)
elevenAPIKey = None
elevenLabsVoiceName = "Rachel"
latencyOptimizationLevel=3      #4 is slightly faster but can mispronounce dates and numbers. Not worth it imo.

user = ElevenLabsUser(elevenAPIKey or keyring.get_password("openai_chat_app", "elevenlabs_key"))

#Get the voice
voice = user.get_voices_by_name(elevenLabsVoiceName)[0]

#pyAudio backend, used to get info about the audio devices
pyABackend = pyaudio.PyAudio()
outputDeviceIndex = -1
logging.basicConfig(level=logging.DEBUG)

def main():
    #Audio output setup
    useStream = True
    backgroundPlayback = True
    prompt = "I am currently trying to debug a Linux issue."
    print(sounddevice.get_portaudio_version())
    defaultOutputInfo = pyABackend.get_default_output_device_info()
    print(f"Default output device: {defaultOutputInfo['name']} - {defaultOutputInfo['index']}")

    for device in get_list_of_portaudio_devices("output"):
        print(device)

    if useStream:
        voice.generate_and_stream_audio(prompt, streamInBackground=backgroundPlayback)
    else:
        voice.generate_play_audio(prompt, playInBackground=backgroundPlayback)

    for device in get_list_of_portaudio_devices("output"):
        print(device)

    if useStream:
        voice.generate_and_stream_audio(prompt, streamInBackground=backgroundPlayback)
    else:
        voice.generate_play_audio(prompt, playInBackground=backgroundPlayback)
    #voice.generate_play_audio("I am currently trying to debug a linux issue.", portaudioDeviceID=outputDeviceIndex, playInBackground=False)
    print("Waiting for you to exit...")
    while True:
        time.sleep(1)



#UI stuff, not relevant to the main program.

def get_list_of_portaudio_devices(deviceType:str) -> list[str]:
    """
    Returns a list containing all the names of portaudio devices of the specified type.
    """
    if deviceType != "output" and deviceType != "input":
        raise ValueError("Invalid audio device type.")

    deviceNames = list()
    for hostAPI in range(pyABackend.get_host_api_count()):
        hostAPIinfo = pyABackend.get_host_api_info_by_index(hostAPI)
        for i in range(hostAPIinfo["deviceCount"]):
            device = pyABackend.get_device_info_by_host_api_device_index(hostAPIinfo["index"], i)
            if device["max" + deviceType[0].upper() + deviceType[1:] + "Channels"] > 0:
                deviceNames.append(f"{device['name']} (API: {hostAPIinfo['name']}) - {device['index']}")

    return deviceNames

def get_portaudio_device_info_from_name(deviceName:str):
    chosenDeviceID = int(deviceName[deviceName.rfind(" - ") + 3:])
    chosenDeviceInfo = pyABackend.get_device_info_by_index(chosenDeviceID)
    return chosenDeviceInfo

def choose_int(prompt, minValue, maxValue) -> int:
    print(prompt)
    chosenVoiceIndex = -1
    while not (minValue <= chosenVoiceIndex <= maxValue):
        try:
            chosenVoiceIndex = int(input("Input a number between " + str(minValue) +" and " + str(maxValue)+"\n"))
        except ValueError:
            print("Not a valid number.")
    return chosenVoiceIndex
def choose_from_list_of_strings(prompt, options:list[str]) -> str:
    print(prompt)
    if len(options) == 1:
        print("Choosing the only available option: " + options[0])
        return options[0]

    for index, option in enumerate(options):
        print(str(index+1) + ") " + option)

    chosenOption = choose_int("", 1, len(options)) - 1
    return options[chosenOption]



if __name__=="__main__":
    main()