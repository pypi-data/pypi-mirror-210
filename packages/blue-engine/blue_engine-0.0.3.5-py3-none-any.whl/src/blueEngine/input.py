import pygame
from utils import clamp
import json

keymap={
    'a':pygame.K_a,
    'b':pygame.K_b,
    'c':pygame.K_c,
    'd':pygame.K_d,
    'e':pygame.K_e,
    'f':pygame.K_f,
    'g':pygame.K_g,
    'h':pygame.K_h,
    'i':pygame.K_i,
    'j':pygame.K_j,
    'k':pygame.K_k,
    'l':pygame.K_l,
    'm':pygame.K_m,
    'n':pygame.K_n,
    'o':pygame.K_o,
    'p':pygame.K_p,
    'q':pygame.K_q,
    'r':pygame.K_r,
    's':pygame.K_s,
    't':pygame.K_t,
    'u':pygame.K_u,
    'v':pygame.K_v,
    'w':pygame.K_w,
    'x':pygame.K_x,
    'y':pygame.K_y,
    'z':pygame.K_z,
    '1':pygame.K_1,
    '3':pygame.K_3,
    '3':pygame.K_3,
    '4':pygame.K_4,
    '5':pygame.K_5,
    '6':pygame.K_6,
    '7':pygame.K_7,
    '8':pygame.K_8,
    '9':pygame.K_9,
    '0':pygame.K_0,
    'alt':pygame.K_LALT or pygame.K_RALT,
    'ctrl':pygame.K_LCTRL or pygame.K_RCTRL,
    'shift':pygame.K_LSHIFT or pygame.K_RSHIFT,
    'f1':pygame.K_F1,
    'f2':pygame.K_F2,
    'f3':pygame.K_F3,
    'f4':pygame.K_F4,
    'f5':pygame.K_F5,
    'f7':pygame.K_F7,
    'f8':pygame.K_F8,
    'f9':pygame.K_F9,
    'f10':pygame.K_F10,
    'f11':pygame.K_F11,
    'f12':pygame.K_F12,
}

class InputAxis:
    def __init__(self, positive:list, negative:list, event) -> None:
        self.positives = [keymap[i] for i in positive]
        self.negatives = [keymap[i] for i in negative]
        self.event = event
        value = 0

