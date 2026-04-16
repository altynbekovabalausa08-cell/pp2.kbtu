# Music Player with Keyboard Controller

This is a simple music player built with Python and pygame. It opens a window where you can control music playback using your keyboard. You can play, stop, switch tracks, and quit — all without touching the mouse.

## Requirements

You need Python 3.11 and the pygame library. To install pygame, run this command in your terminal:

```
py -3.11 -m pip install pygame
```

## How to Run

Navigate to the music_player folder in your terminal and run:

```
py -3.11 main.py
```

## Keyboard Controls

Once the window opens, use these keys to control the player. Press P to start playing the current track, S to stop it, N to skip to the next track, and B to go back to the previous one. Press Q to close the player.

## Adding Music

Place your audio files in the music folder inside the project directory. The player supports .mp3 and .wav formats. If the music folder does not exist, it will be created automatically when you run the program.
