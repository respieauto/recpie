import sys
from PIL import Image
from modules.image_handler import ImageHandler

class DummyConfig:
    def get(self, key, default=None):
        if key == "pexels_api_key":
            return "563492ad6f91700001000001a1c9df25828f4c7ab4e6f47738c6422d" # public key or anything, just for testing
        return default

handler = ImageHandler(DummyConfig())
res = handler._download_and_optimize("https://images.pexels.com/photos/952629/pexels-photo-952629.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940", "My Amazing Test Title For Fashion Blog")

if res and res.get("local_path"):
    print(f"SUCCESS: Image saved at {res['local_path']}")
else:
    print("FAILED")
