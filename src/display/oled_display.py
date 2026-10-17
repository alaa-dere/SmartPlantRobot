from PIL import Image, ImageDraw, ImageFont

try:
    from luma.oled.device import sh1106  # type: ignore
    from luma.core.interface.serial import i2c  # type: ignore
    HAS_LUMA = True
except ImportError:
    HAS_LUMA = False

class OLEDDisplay:
    def __init__(self):
        self.has_hardware = False
        
        if HAS_LUMA:
            try:
                serial = i2c(port=1, address=0x3C)
                self.device = sh1106(serial)
                self.width = self.device.width
                self.height = self.device.height
                self.has_hardware = True
            except Exception:
                self.width, self.height = 128, 64
        else:
            self.width, self.height = 128, 64
            
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def show_emotion(self, emotion_key, message=""):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # 1. HAPPY
        if emotion_key == "HAPPY":
            self.draw.arc((20, 15, 45, 35), 180, 360, fill=255)
            self.draw.arc((83, 15, 108, 35), 180, 360, fill=255)
            self.draw.arc((50, 30, 78, 45), 0, 180, fill=255)

        # 2. THIRSTY
        elif emotion_key == "THIRSTY":
            self.draw.line((20, 20, 45, 30), fill=255)
            self.draw.line((108, 20, 83, 30), fill=255)
            self.draw.arc((50, 35, 78, 48), 180, 360, fill=255)

        # 3. NEEDS_WATER
        elif emotion_key == "NEEDS_WATER":
            self.draw.line((20, 20, 45, 30), fill=255)
            self.draw.line((108, 20, 83, 30), fill=255)
            self.draw.arc((50, 35, 78, 48), 180, 360, fill=255)
            self.draw.line((25, 32, 25, 42), fill=255)
            self.draw.line((103, 32, 103, 42), fill=255)

        # 4. HOT
        elif emotion_key == "HOT":
            self.draw.line((20, 25, 45, 25), fill=255)
            self.draw.line((83, 25, 108, 25), fill=255)
            self.draw.ellipse((58, 32, 70, 44), outline=255, fill=255)

        # 5. NEEDS_LIGHT
        elif emotion_key == "NEEDS_LIGHT":
            self.draw.ellipse((22, 18, 42, 38), outline=255)
            self.draw.ellipse((85, 18, 105, 38), outline=255)
            self.draw.line((50, 40, 78, 40), fill=255)

        # 6. SEARCHING
        elif emotion_key == "SEARCHING":
            self.draw.ellipse((25, 15, 45, 35), outline=255, fill=0)
            self.draw.ellipse((35, 20, 43, 28), outline=255, fill=255)
            self.draw.ellipse((83, 15, 103, 35), outline=255, fill=0)
            self.draw.ellipse((93, 20, 101, 28), outline=255, fill=255)

        # 7. SLEEPING
        elif emotion_key == "SLEEPING":
            self.draw.line((20, 25, 45, 25), fill=255)
            self.draw.line((83, 25, 108, 25), fill=255)
            self.draw.text((100, 8), "Zzz", font=self.font, fill=255)

        # 8. WAKE_UP
        elif emotion_key == "WAKE_UP":
            self.draw.ellipse((18, 12, 48, 42), outline=255, fill=255)
            self.draw.ellipse((80, 12, 110, 42), outline=255, fill=255)
            self.draw.ellipse((58, 35, 70, 45), outline=255, fill=0)

        # 9. LISTENING
        elif emotion_key == "LISTENING":
            self.draw.ellipse((22, 18, 42, 38), outline=255, fill=255)
            self.draw.ellipse((85, 18, 105, 38), outline=255, fill=255)
            self.draw.arc((110, 15, 125, 35), 270, 90, fill=255)

        # 10. TALKING
        elif emotion_key == "TALKING":
            self.draw.arc((20, 15, 45, 35), 180, 360, fill=255)
            self.draw.arc((83, 15, 108, 35), 180, 360, fill=255)
            self.draw.chord((52, 28, 76, 46), 0, 180, fill=255)

        # 11. ERROR
        elif emotion_key == "ERROR":
            self.draw.line((20, 15, 45, 35), fill=255)
            self.draw.line((20, 35, 45, 15), fill=255)
            self.draw.line((83, 15, 108, 35), fill=255)
            self.draw.line((83, 35, 108, 15), fill=255)

        if message:
            self.draw.text((5, 52), message, font=self.font, fill=255)

        if self.has_hardware:
            try:
                self.device.display(self.image)
            except Exception:
                pass

    def clear(self):
        if self.has_hardware:
            try:
                self.device.clear()
            except Exception:
                pass