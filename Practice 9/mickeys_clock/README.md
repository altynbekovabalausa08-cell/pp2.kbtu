# Mickey's Clock Application

This is an animated clock built with Python and pygame. It displays a clock face with two hands that rotate in real time based on your system clock. One hand shows the minutes and the other shows the seconds. The current time is also displayed at the top of the window in digital format.

The clock face and hands are loaded from image files in the images folder. If those images are missing, the program automatically draws simple fallback shapes so it still works without any external files.

## Requirements

You need Python 3.11 and the pygame library. To install pygame, run this command in your terminal:

```
py -3.11 -m pip install pygame
```

## How to Run

Navigate to the mickeys_clock folder in your terminal and run:

```
py -3.11 main.py
```

## Adding Images

Place your image files in the images folder inside the project directory. The program expects three files: clock.png for the clock face, right_hand.png for the minute hand, and left_hand.png for the second hand. If any of these are missing, the program will still run using simple drawn shapes instead.

## Notes

The clock updates in real time at 60 frames per second. No keyboard input is needed — just run it and watch it go. Close the window to exit.
