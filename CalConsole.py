""" 
MIT License

Copyright (c) 2025 Callum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import pygame
import sys
import os
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from RestrictedPython.Guards import safe_builtins

import threading

class SafeThread: # A custom wrapper for threading, for sandboxing reasons.
    def __init__(self, target):
        self.thread = threading.Thread(target=target)
    def start(self):
        self.thread.start()
    def join(self):
        self.thread.join()



# safe modules
SAFE_MODULES = {
    "math": __import__("math"),
    "random": __import__("random")
}


# Console specs
INTERNAL_WIDTH = 128
INTERNAL_HEIGHT = 128
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
FPS = 30
MAX_SPRITE_SIZE = 16


# Cartridge runtime consts
QUIT_REQUESTED = False
# Ask user where cartridge file is
CART_PATH = input("folder where the .callumcart file to load is located: ")
CART_NAME = input("name of .callumcart file to load: ")
if not os.path.exists(f"{CART_PATH}{CART_NAME}.callumcart"):
    print("Cartridge not found.")
    sys.exit(1)

# 16-color palette (RGB)
PALETTE = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
    (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (128, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
    (128, 128, 0), (128, 0, 128), (0, 128, 128), (192, 192, 192)
]

# Built-in sprite (8x8 smiley face)
SPRITE = [
    [0,0,1,1,1,1,0,0],
    [0,1,2,2,2,2,1,0],
    [1,2,3,2,2,3,2,1],
    [1,2,2,2,2,2,2,1],
    [1,2,4,2,2,4,2,1],
    [1,2,2,2,2,2,2,1],
    [0,1,2,2,2,2,1,0],
    [0,0,1,1,1,1,0,0]
]

# Safe dictionary access
def _getitem_(obj, key):
    try:
        return obj[key]
    except Exception:
        return None
def _getiter_(obj):
    try:
        return iter(obj)
    except Exception:
        return iter([])
def draw_sprite(surface, sprite, x, y):
    for row in range(len(sprite)):
        for col in range(len(sprite[row])):
            color_index = sprite[row][col]
            color = PALETTE[color_index]
            pygame.draw.rect(surface, color, (x + col, y + row, 1, 1))

def draw_custom_sprite(surface, sprite, x, y):
    if len(sprite) > MAX_SPRITE_SIZE or any(len(row) > MAX_SPRITE_SIZE for row in sprite):
        return
    for row in range(len(sprite)):
        for col in range(len(sprite[row])):
            color_index = sprite[row][col]
            if 0 <= color_index < len(PALETTE):
                pygame.draw.rect(surface, PALETTE[color_index], (x + col, y + row, 1, 1))

def load_cart(filename, api):
    with open(filename, "r") as f:
        code = f.read()
    try:
        compiled = compile_restricted(code, filename=filename, mode='exec')
    except SyntaxError as e:
        print("Syntax error in cartridge:", e)
        return {}
    exec(compiled, api, api)
    return api

def main():
    pygame.init()
    pygame.display.set_caption("CallumConsole")

    game_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    clock = pygame.time.Clock()
    keys = {}

    output_buffer = []

    # Define sandboxed API
    def api_draw_sprite(x_, y_):
        draw_sprite(game_surface, SPRITE, x_, y_)

    def api_draw_custom_sprite(sprite_, x_, y_):
        draw_custom_sprite(game_surface, sprite_, x_, y_)

    def api_get_input():
        return {
            "left": keys[pygame.K_LEFT],
            "right": keys[pygame.K_RIGHT],
            "up": keys[pygame.K_UP],
            "down": keys[pygame.K_DOWN],
            "a": keys[pygame.K_a],
            "b": keys[pygame.K_b]
        }
    def api_exit():
        global QUIT_REQUESTED
        QUIT_REQUESTED = True
        
    # Custom print wrapper for RestrictedPython
    class PrintWrapper:
        def __call__(self, *args):
            output_buffer.append(" ".join(str(arg) for arg in args))

        @property
        def _call_print(self):
            return self.__call__

    printer = PrintWrapper()

    # Setup sandbox
    print("Setting up API...")
    safe_api = safe_globals.copy()
    safe_api["__builtins__"] = safe_builtins.copy()
    safe_api["_print_"] = lambda _=None: printer
    safe_api["_getitem_"] = _getitem_
    safe_api["draw_sprite"] = api_draw_sprite
    safe_api["draw_custom_sprite"] = api_draw_custom_sprite
    safe_api["get_input"] = api_get_input
    safe_api["_write_"] = lambda x:x
    safe_api["quit"] = api_exit
    safe_api["_getiter_"] = _getiter_
    for name, mod in SAFE_MODULES.items():
        print(f"adding {name} to allowed modules!")
        safe_api[name] = mod
    safe_api["Thread"] = SafeThread

    # Load cartridge
    print("compiling cartridge:", f"{CART_PATH}{CART_NAME}.callumcart")
    try:
        cart = load_cart(f"{CART_PATH}{CART_NAME}.callumcart", safe_api)
        setup_fn = cart.get("setup")
        if setup_fn:
            try:
                setup_fn()
            except Exception as e:
                print("Cartridge setup error:", e)
        update_fn = cart.get("update")
    except Exception as e:
        print("Failed to load cartridge:", e)
        update_fn = None

    running = True
    while running:
        game_surface.fill(PALETTE[0])  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if update_fn:
            try:
                update_fn()
            except Exception as e:
                print("Cartridge error:", e)

        # Capture printed output
        if output_buffer:
            print("[CART OUTPUT]", "\n".join(output_buffer))
            output_buffer.clear()
        if QUIT_REQUESTED:
            running = False
        scaled = pygame.transform.scale(game_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
