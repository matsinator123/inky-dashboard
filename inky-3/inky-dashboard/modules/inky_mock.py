"""
Mock Inky display for development and testing.
Provides a dummy display object with the same interface as the real Inky display.
"""

def auto():
    class DummyDisplay:
        def set_image(self, img):
            pass
        def show(self):
            print("[MOCK] Display would update now.")
    return DummyDisplay()
