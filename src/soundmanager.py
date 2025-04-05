#python3
"""
    File: soundmanager.py
    Sound manager from pygame
    Date: Sat, 05/04/2025
    Author: Coolbrother
"""
import os
import pygame

curdir = os.path.dirname(__file__) # directory for the current script
_basedir = os.path.dirname(curdir) # base directory for the application
_mediadir = os.path.join(_basedir, "media")

# Charger les sons de batterie

# Son du métronome
_CLICKNAME1 = f"{_mediadir}/hi_wood_block_mono.wav"
_CLICKNAME2 = f"{_mediadir}/low_wood_block_mono.wav"
#----------------------------------------


class SoundManager(object):
    """ Sound manager """
    def __init__(self):
        pygame.init()
        self.drum_sounds = [
                pygame.mixer.Sound(f"{_mediadir}/{i}.wav") for i in range(1, 17)
        ]
        self.sound_click1 = pygame.mixer.Sound(_CLICKNAME1)
        self.sound_click2 = pygame.mixer.Sound(_CLICKNAME2)


    #----------------------------------------

    def play(self, index):
         self.drum_sounds[index].play()

    #----------------------------------------

    def play_sound(self, sound_name):
         self.drum_sounds[sound_name].play()

    #----------------------------------------
     
    def preview_sound(self, sound_name):
        if sound_name in self.sounds:
            self.play_sound(sound_name)

    #----------------------------------------

    def set_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume / 100)

    #----------------------------------------

#=========================================

if __name__ == "__main__":
    input("It's OK...")
#----------------------------------------
