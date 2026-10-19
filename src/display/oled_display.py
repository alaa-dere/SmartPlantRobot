
import os
import math
import time
import pygame


class OLEDDisplay:
    WIDTH = 800
    HEIGHT = 480

    COLORS = {
        "HAPPY": (88, 205, 151),
        "THIRSTY": (100, 167, 235),
        "NEEDS_WATER": (75, 135, 220),
        "HOT": (255, 150, 99),
        "NEEDS_LIGHT": (175, 150, 225),
        "SEARCHING": (95, 195, 215),
        "SLEEPING": (90, 112, 170),
        "WAKE_UP": (250, 173, 192),
        "LISTENING": (105, 185, 225),
        "TALKING": (96, 207, 155),
        "ERROR": (235, 105, 115),
    }

    def __init__(self):
        pygame.init()

        # Use the HDMI display
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.FULLSCREEN
        )

        pygame.display.set_caption("Smart Plant Robot - F03")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 34)
        self.title_font = pygame.font.Font(None, 42)

        self.current_emotion = "HAPPY"
        self.message = ""
        self.start_time = time.monotonic()
        self.running = True

    def draw_eye(self, x, y, blink=False, pupil_offset=0):
        WHITE = (255, 255, 255)
        DARK = (28, 48, 61)

        if blink:
            pygame.draw.line(
                self.screen, DARK,
                (x - 58, y),
                (x + 58, y),
                10
            )
            return

        pygame.draw.ellipse(
            self.screen, WHITE,
            (x - 65, y - 80, 130, 160)
        )

        pygame.draw.ellipse(
            self.screen, DARK,
            (x - 24 + pupil_offset, y - 36, 48, 72)
        )

        pygame.draw.circle(
            self.screen, WHITE,
            (x - 8 + pupil_offset, y - 22),
            11
        )

    def draw_mouth(self, emotion, t):
        DARK = (28, 48, 61)
        WHITE = (255, 255, 255)

        if emotion in ("HAPPY", "WAKE_UP", "SEARCHING"):
            pygame.draw.arc(
                self.screen, DARK,
                (310, 200, 180, 115),
                math.pi, 2 * math.pi,
                10
            )

        elif emotion == "TALKING":
            opening = int(25 + 22 * abs(math.sin(t * 7)))

            pygame.draw.ellipse(
                self.screen, DARK,
                (360, 255, 80, opening + 20)
            )

        elif emotion in ("THIRSTY", "NEEDS_WATER"):
            pygame.draw.arc(
                self.screen, DARK,
                (330, 270, 140, 80),
                0, math.pi,
                10
            )

        elif emotion == "HOT":
            pygame.draw.ellipse(
                self.screen, DARK,
                (365, 255, 70, 88)
            )

            pygame.draw.ellipse(
                self.screen, (245, 110, 130),
                (377, 305, 46, 32)
            )

        elif emotion in ("NEEDS_LIGHT", "LISTENING"):
            pygame.draw.line(
                self.screen, DARK,
                (345, 290), (455, 290), 9
            )

        elif emotion == "SLEEPING":
            pygame.draw.arc(
                self.screen, DARK,
                (365, 260, 70, 35),
                math.pi, 2 * math.pi, 7
            )

        elif emotion == "ERROR":
            pygame.draw.line(
                self.screen, DARK,
                (365, 260), (435, 320), 10
            )

            pygame.draw.line(
                self.screen, DARK,
                (435, 260), (365, 320), 10
            )

    def draw_tears(self, emotion, t):
        if emotion not in ("THIRSTY", "NEEDS_WATER"):
            return

        BLUE = (48, 125, 230)

        amount = 2 if emotion == "NEEDS_WATER" else 1

        for i in range(amount):
            offset = int((t * 50 + i * 45) % 90)

            for x in (240, 560):
                pygame.draw.ellipse(
                    self.screen, BLUE,
                    (x, 250 + offset, 18, 32)
                )

    def draw_sleeping(self):
        DARK = (28, 48, 61)

        for x in (260, 540):
            pygame.draw.arc(
                self.screen, DARK,
                (x - 65, 160, 130, 75),
                0, math.pi, 9
            )

        text = self.title_font.render(
            "Zzz", True, (255, 255, 255)
        )
        self.screen.blit(text, (635, 80))

    def draw_error_eyes(self):
        DARK = (28, 48, 61)

        for x in (260, 540):
            pygame.draw.line(
                self.screen, DARK,
                (x - 45, 150), (x + 45, 240), 12
            )

            pygame.draw.line(
                self.screen, DARK,
                (x + 45, 150), (x - 45, 240), 12
            )

    def show_emotion(self, emotion_key, message=""):
        if emotion_key != self.current_emotion:
            self.current_emotion = emotion_key
            self.start_time = time.monotonic()

        self.message = message
        self.render()

    def render(self):
        emotion = self.current_emotion
        t = time.monotonic() - self.start_time

        bg = self.COLORS.get(emotion, (80, 180, 140))
        self.screen.fill(bg)

        DARK = (28, 48, 61)

        # Automatic blinking every 4 seconds
        blink = (t % 4.0) < 0.15

        if emotion == "SLEEPING":
            self.draw_sleeping()

        elif emotion == "ERROR":
            self.draw_error_eyes()

        else:
            pupil_offset = 0

            if emotion == "SEARCHING":
                pupil_offset = int(25 * math.sin(t * 2.5))

            self.draw_eye(
                260, 190, blink, pupil_offset
            )
            self.draw_eye(
                540, 190, blink, pupil_offset
            )

        self.draw_mouth(emotion, t)
        self.draw_tears(emotion, t)

        if emotion == "LISTENING":
            pygame.draw.arc(
                self.screen, DARK,
                (650, 160, 75, 100),
                -1.2, 1.2, 8
            )

        # Message at bottom
        if self.message:
            text = self.font.render(
                self.message[:55],
                True,
                (255, 255, 255)
            )

            rect = text.get_rect(
                center=(self.WIDTH // 2, 430)
            )

            self.screen.blit(text, rect)

        pygame.display.flip()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

        if self.running:
            self.render()
            self.clock.tick(30)

        return self.running

    def clear(self):
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def close(self):
        pygame.mouse.set_visible(True)
        pygame.quit()
