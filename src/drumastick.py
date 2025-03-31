#!/usr/bin/python3
"""
    File: drumastick.py
    Mini Drum Machine for test
    Date: Mon, 31/03/2025
    Author: Coolbrother
"""

from os import path
import time
import curses
import pygame

# Initialiser Pygame
pygame.init()

DEBUG = 1
curdir = path.dirname(__file__) # directory for the current script
_basedir = path.dirname(curdir) # base directory for the application
_mediadir = path.join(_basedir, "media")

# Charger les sons de batterie
sounds = [
    pygame.mixer.Sound(f"{_mediadir}/{i}.wav") for i in range(1, 17)
]

# Son du métronome
metronome_sound1 = pygame.mixer.Sound(f"{_mediadir}/hi_wood_block_mono.wav")
metronome_sound2 = pygame.mixer.Sound(f"{_mediadir}/low_wood_block_mono.wav")

# Mappage des touches du clavier aux pads
key_mapping = {
    ord('q'): 0, ord('s'): 1, ord('d'): 2, ord('f'): 3,
    ord('g'): 4, ord('h'): 5, ord('j'): 6, ord('k'): 7,
    ord('a'): 8, ord('z'): 9, ord('e'): 10, ord('r'): 11,
    ord('t'): 12, ord('y'): 13, ord('u'): 14, ord('i'): 15
}

# Motif rythmique (True si le pad est activé, False sinon)
pattern = [[False] * 16 for _ in range(16)]

# Motif prédéfini pattern_01
pattern_01 = [[False] * 16 for _ in range(16)]
pattern_01[0][0] = True  # 1.1
pattern_01[0][4] = True  # 1.5
pattern_01[0][8] = True  # 1.9
pattern_01[0][12] = True  # 1.13
pattern_01[4][2] = True  # 5.3
pattern_01[4][6] = True  # 5.7
pattern_01[4][10] = True  # 5.11
pattern_01[5][1:4] = [True] * 3  # 6.2-4
pattern_01[5][5:8] = [True] * 3  # 6.6-8
pattern_01[5][9:12] = [True] * 3  # 6.10-12
pattern_01[5][13:16] = [True] * 3  # 6.14-16
pattern_01[7][15] = True  # 8.16
pattern_01[8][14] = True  # 9.15
pattern_01[9][13] = True  # 10.14
pattern_01[10][0] = True  # 11.1

def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" % (title, msg))
        if bell:
            print("\a")

#------------------------------------------------------------------------------

def beep():
    curses.beep()

#------------------------------------------------------------------------------

class Player(object):
    def __init__(self, bpm=100):
        self.bpm = bpm
        self.step_duration = 60.0 / bpm / 4
        self.current_step = 0
        self.beat_counter = 0
        self.cycle_counter = 0
        self.playing = False
        self.metronome_active = False
        self.pattern = pattern

    #----------------------------------------

    def play_pattern(self, sounds):
        """Joue l'étape actuelle du motif."""
        for i in range(16):
            if self.pattern[i][self.current_step]:
                sounds[i].play()

    #----------------------------------------

    def play_metronome(self):
        """Joue le son du métronome."""
        if self.beat_counter == 0:
            metronome_sound1.play()
        else:
            metronome_sound2.play()

    #----------------------------------------

    def change_bpm(self, new_bpm):
        """Change le tempo du motif."""
        self.bpm = new_bpm
        self.step_duration = 60.0 / self.bpm / 4

    #----------------------------------------

    def update(self):
        """Met à jour les compteurs et joue le métronome si nécessaire."""
        if self.metronome_active and self.cycle_counter % 4 == 0:
            self.play_metronome()
            self.beat_counter = (self.beat_counter + 1) % 4

        self.cycle_counter = (self.cycle_counter + 1) % 16
        if self.cycle_counter == 0:
            self.beat_counter = 0

        if self.playing:
            self.current_step = (self.current_step + 1) % 16

        time.sleep(self.step_duration)

    #----------------------------------------
#=========================================

class MainApp(object):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.player = Player()
        self.cursor_position = [0, 0]
        self.last_played_pad = self.cursor_position[0]
        self.pad_auto_played = True
        self.mode_lst = ["Normal", "Select", "Transport"]  # Liste des modes
        self.mode_index = 0  # Index du mode actuel
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

    #----------------------------------------

    def show_status(self, message):
        """Affiche un message de statut en bas de l'écran."""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(height - 1, 0, message)
        self.stdscr.clrtoeol()  # Efface la fin de la ligne
        self.stdscr.refresh()
        time.sleep(0.1)

    #----------------------------------------

    def update_screen(self):
        """Redessine l'écran."""
        self.stdscr.clear()
        for i in range(16):
            for j in range(16):
                if self.player.pattern[i][j]:
                    self.stdscr.addch(i + 1, j * 2, '#')
                else:
                    self.stdscr.addch(i + 1, j * 2, '.')
        self.stdscr.addch(self.cursor_position[0] + 1, self.cursor_position[1] * 2, 'X')
        self.stdscr.refresh()

    #----------------------------------------

    def main(self):
        """Boucle principale de l'application."""
        running = True
        self.player.playing = False
        self.update_screen()
        while running:
            if self.player.playing or self.player.metronome_active:
                self.stdscr.timeout(0)
            else:
                self.stdscr.timeout(100)

            key = self.stdscr.getch()

            # To debug keycode
            # self.show_status(f"Key: {key}")
            if key == ord('Q'):
                running = False
            elif key == ord(' '):
                self.player.playing = not self.player.playing
                if self.player.playing and self.player.metronome_active:
                    self.player.cycle_counter = self.player.current_step
                    self.player.beat_counter = 0 if self.player.current_step == 0 else (self.player.current_step - 1) // 4
                self.show_status("Playing" if self.player.playing else "Paused")
            elif key == ord('v'):
                self.player.playing = False
                self.player.metronome_active = False
                self.player.current_step = 0
                self.player.beat_counter = 0
                self.player.cycle_counter = 0
                self.show_status("Stopped")
            elif key == curses.KEY_LEFT:
                if self.mode_lst[self.mode_index] == "Normal":
                    if self.cursor_position[1] > 0:
                        self.cursor_position[1] -= 1
                    else:
                        beep()
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: {'Activé' if self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] else 'Désactivé'}")
            elif key == curses.KEY_RIGHT:
                if self.mode_lst[self.mode_index] == "Normal":
                    if self.cursor_position[1] < 15:
                        self.cursor_position[1] += 1
                    else:
                        beep()
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: {'Activé' if self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] else 'Désactivé'}")
            elif key == curses.KEY_UP:
                if self.mode_lst[self.mode_index] == "Normal":
                    if self.cursor_position[0] > 0:
                        self.cursor_position[0] -= 1
                        if self.pad_auto_played:
                            sounds[self.cursor_position[0]].play()
                    else:
                        beep()
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: {'Activé' if self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] else 'Désactivé'}")
            elif key == curses.KEY_DOWN:
                if self.mode_lst[self.mode_index] == "Normal":
                    if self.cursor_position[0] < 15:
                        self.cursor_position[0] += 1
                        if self.pad_auto_played:
                            sounds[self.cursor_position[0]].play()
                    else:
                        beep()
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: {'Activé' if self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] else 'Désactivé'}")
            elif key == curses.KEY_ENTER or key == 10:
                if self.mode_lst[self.mode_index] == "Normal":
                    self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] = True
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: Activé")
            elif key == curses.KEY_BACKSPACE:
                if self.mode_lst[self.mode_index] == "Normal":
                    self.player.pattern[self.cursor_position[0]][self.cursor_position[1]] = False
                    self.show_status(f"Pad {self.cursor_position[0] + 1}/{self.cursor_position[1] + 1}: Désactivé")
            elif key in key_mapping:
                sounds[key_mapping[key]].play()
                self.last_played_pad = key_mapping[key]
            elif key == ord('l'):
                sounds[self.cursor_position[0]].play()
                self.last_played_pad = self.cursor_position[0]
            elif key == ord('m'):
                if self.last_played_pad is not None:
                    sounds[self.last_played_pad].play()
            elif key == 12:  # Ctrl + l
                self.player.metronome_active = True
                self.player.beat_counter = 0
            elif key == ord('L'):  # Shift + l
                self.player.metronome_active = False
            elif key == curses.KEY_F4:  # Touche F4 pour charger pattern_01
                self.player.pattern = [row[:] for row in pattern_01]
                self.show_status("Pattern 01 chargé")
            elif key == ord('+'):  # Augmenter le BPM
                self.player.change_bpm(self.player.bpm + 5)
                self.show_status(f"BPM: {self.player.bpm}")
            elif key == ord('-'):  # Diminuer le BPM
                self.player.change_bpm(max(5, self.player.bpm - 5))
                self.show_status(f"BPM: {self.player.bpm}")

            elif key == 9:  # Tab pour passer d'un mode à un autre
                if self.mode_index < len(self.mode_lst) -1:
                    self.mode_index += 1
                    self.show_status(f"Mode: {self.mode_lst[self.mode_index]}")
                else:
                    beep()
            elif key == 353:  # Shift+Tab pour passer d'un mode à un autre
                if self.mode_index >0:
                    self.mode_index -= 1
                    self.show_status(f"Mode: {self.mode_lst[self.mode_index]}")
                else:
                    beep()

            # Jouer le pattern et le metronome
            if self.player.playing or self.player.metronome_active:
                if self.player.playing:
                    self.player.play_pattern(sounds)
                self.player.update()

        pygame.quit()

    #----------------------------------------

#=========================================

def main(stdscr):
    app = MainApp(stdscr)
    app.main()

#----------------------------------------

if __name__ == "__main__":
    curses.wrapper(main)

#----------------------------------------

