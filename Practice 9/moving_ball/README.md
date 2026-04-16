# Moving Ball Game

This is a simple interactive game built with Python and pygame. A red ball appears in the center of the window and you can move it around using the arrow keys on your keyboard. The ball moves 20 pixels with each key press and cannot go outside the window boundaries. The current position of the ball is displayed on screen in real time.

## Requirements

You need Python 3.11 and the pygame library. To install pygame, run this command in your terminal:

```
py -3.11 -m pip install pygame
```

## How to Run

Navigate to the moving_ball folder in your terminal and run:

```
py -3.11 main.py
```

## Controls

Use the arrow keys to move the ball. Press the up arrow to move up, down arrow to move down, left arrow to move left, and right arrow to move right. Each key press moves the ball exactly 20 pixels in that direction. Close the window to exit.

## Notes

The ball stays within the window at all times. If it reaches any edge it simply stops there and cannot move further in that direction.
