#!/usr/bin/env python3
import pygame
import pigpio
import collections
import time
import threading
import os
import glob

GPIO_SERVO = 20
GPIO_BUTTON = 21

GPIO_LED_RED = 14
GPIO_LED_GREEN = 15
GPIO_LED_BLUE = 18

BASE_DIR = os.path.expanduser('~/hut_niklas')
EFFECTS_DIR = os.path.join(BASE_DIR, 'effects')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')


class LedHandler():

    def __init__(self,
                 red_pin=GPIO_LED_RED,
                 green_pin=GPIO_LED_GREEN,
                 blue_pin=GPIO_LED_BLUE):
        self.pi = pigpio.pi()
        self.pins = collections.deque([red_pin, green_pin, blue_pin], maxlen=3)
        self.led_mask = [True, False, False]

        for pin in self.pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, pigpio.LOW)

    def toggle_led(self):
        self.pins.rotate()
        for pin, mask in zip(self.pins, self.led_mask):
            self.pi.write(pin, mask)

    def run(self):
        while True:
            self.toggle_led()
            time.sleep(0.5)


class ServoHandler():

    def __init__(self, pin=GPIO_SERVO):
        self.pi = pigpio.pi()
        self.pin = pin
        self.pi.set_servo_pulsewidth(self.pin, 1600)

    def run(self):
        while True:
            time.sleep(0.5)


class SoundHandler():

    def __init__(self, button_pin=GPIO_BUTTON):
        self.button_pin = button_pin
        self.load_ok_sound()
        self.load_music()
        self.pi = pigpio.pi()
        self.pi.set_pull_up_down(self.button_pin, pigpio.PUD_UP)
        self.pi.callback(self.button_pin, pigpio.FALLING_EDGE, self.on_falling_edge)
        self.t_last = 0.0
        self.music_counter = 0
        self.finished = True

    def on_falling_edge(self, gpio, *_):
        now = time.time()
        if now - self.t_last < 1.0:
            return
        print('Button pressed')
        self.t_last = now
        self.play_ok()
        self.finished = False
        self.play_next_song()

    def load_ok_sound(self):
        path = os.path.join(EFFECTS_DIR, 'ok.wav')
        print(f'Loading file: {path}')
        self.ok_sound = pygame.mixer.Sound(path)
        pygame.mixer.Sound.play(self.ok_sound)

    def load_music(self):
        path = SOUNDS_DIR
        self.music_files = collections.deque([])
        for filename in glob.glob(os.path.join(path, '*.wav')):
            self.music_files.append(filename)

    def play_next_song(self):
        if self.finished:
            pygame.mixer.music.stop()
            return
        song = self.music_files[0]
        self.music_counter += 1
        if self.music_counter >= len(self.music_files):
            self.music_counter = 0
            self.finished = True
            pygame.mixer.music.stop()
        print(f'Playing "{os.path.basename(song)}"')
        pygame.mixer.music.load(song)
        self.music_files.rotate()
        pygame.mixer.music.play()

    def play_ok(self):
        pygame.mixer.Sound.play(self.ok_sound)

    def run(self):
        while True:
            if not pygame.mixer.music.get_busy():
                self.play_next_song()
            time.sleep(0.5)


def main():
    pygame.mixer.init()
    handler = LedHandler()
    led_thread = threading.Thread(target=handler.run, args=())
    led_thread.setDaemon(True)
    led_thread.start()

    servo_handler = ServoHandler()
    servo_thread = threading.Thread(target=servo_handler.run, args=())
    servo_thread.setDaemon(True)
    servo_thread.start()

    sound_handler = SoundHandler()
    sound_thread = threading.Thread(target=sound_handler.run, args=())
    sound_thread.setDaemon(True)
    sound_thread.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
