import pyautogui

mouse_pos = None

def steal():
    global mouse_pos
    mouse_pos = pyautogui.position()

def restore():
    if mouse_pos:
        pyautogui.moveTo(mouse_pos)