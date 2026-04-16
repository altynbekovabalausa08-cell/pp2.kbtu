# Practice 9 — Pygame Projects

This folder contains three mini projects built with Python and pygame. Each project is a small interactive application that runs in its own window.

## Requirements

All three projects require Python 3.11 and the pygame library. Install pygame with this command:

```
py -3.11 -m pip install pygame
```

## Projects

### 1. Mickey's Clock
An animated analog clock that shows the current time using two rotating hands. The minute hand and second hand move in real time based on your system clock. The current time is also shown in digital format at the top of the window. If the image files are missing, the program draws simple fallback shapes automatically.

To run:
```
cd mickeys_clock
py -3.11 main.py
```

### 2. Music Player
A keyboard-controlled music player that lets you play, stop, and switch between audio tracks. It displays the current track name, playback status, and how long the track has been playing. Place your `.mp3` or `.wav` files in the music folder to use your own songs.

To run:
```
cd music_player
py -3.11 main.py
```

Keyboard controls: P = Play, S = Stop, N = Next track, B = Previous track, Q = Quit.

### 3. Moving Ball
A simple interactive game where a red ball starts in the center of the screen and you move it around using the arrow keys. The ball moves 20 pixels per key press and cannot go outside the window boundaries. The current position is shown on screen in real time.

To run:
```
cd moving_ball
py -3.11 main.py
```

## Notes

Each project has its own README with more details. The `__pycache__` folders that appear after running the projects are created automatically by Python and can be ignored.
