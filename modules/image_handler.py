"""
Image Handler Module - AI Image Generator
Pollinations.ai (FREE, no API key) se AI-generated images banata hai
Blog post ke topic se directly related unique images!
Pinterest ke liye 1000x1500 portrait optimize karta hai, with VIRAL TikTok style text overlay.
"""

import json
import os
import requests
import base64
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime


class ImageHandler:
    def __init__(self, config: dict):
        self.config = config
        self.pollinations_url = "https://image.pollinations.ai/prompt"
        self.pexels_api_key = config.get("pexels_api_key", "")
        self.pexels_base_url = "https://api.pexels.com/v1"

    def fetch_image_for_topic(self, topic: str, title: str) -> dict:
        """Topic ke liye image fetch karo (Direct Pexels ya AI)"""
        print(f"\n🎨 Image dhoondh raha hoon: '{topic[:50]}'")
        return self._fetch_pexels_fallback(topic, title)

    def _generate_ai_image(self, topic: str, title: str) -> dict:
        try:
            image_prompt = self._build_image_prompt(topic, title)
            print(f"   🖌️ AI Prompt: {image_prompt[:80]}...")
            encoded_prompt = urllib.parse.quote(image_prompt)
            image_url = (
                f"{self.pollinations_url}/{encoded_prompt}"
                f"?width=1000&height=1500"
                f"&model=flux-realism"
                f"&seed={abs(hash(topic)) % 99999}"
                f"&nologo=true"
                f"&enhance=true"
            )
            print(f"   ⏳ AI image generate ho raha hai (15-30 sec)...")
            response = requests.get(image_url, timeout=60, stream=True)

            if response.status_code == 200 and len(response.content) > 10000:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img = img.resize((1000, 1500), Image.LANCZOS)
                
                os.makedirs("temp_images", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                local_path = f"temp_images/ai_post_{timestamp}.jpg"
                img.save(local_path, "JPEG", quality=90)
                
                with open(local_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode('utf-8')
                print(f"   ✅ AI Image ready! Size: {img.size} | Path: {local_path}")
                return {
                    "local_path": local_path, "url": image_url, "base64": img_base64,
                    "width": 1000, "height": 1500, "source": "pollinations_ai",
                    "photographer": "AI Generated", "prompt": image_prompt
                }
            else:
                return None
        except Exception as e:
            print(f"   ❌ AI image error: {e}")
            return None

    def _build_image_prompt(self, topic: str, title: str) -> str:
        """Food/Recipe optimized prompts"""
        topic_lower = topic.lower()
        prompt_templates = {
            "pasta": "Delicious creamy pasta dish, top down food photography, warm lighting, rustic table, 8k resolution, professional food styling",
            "chicken": "Juicy cooked chicken dish, garnished with herbs, restaurant quality food photography, macro lens, beautifully plated",
            "breakfast": "Healthy breakfast bowl or plate, fresh fruits, eggs, avocado, morning sunlight, bright and airy food photography",
            "dessert": "Mouth-watering decadent dessert, chocolate and berries, dramatic lighting, professional pastry photography",
            "dinner": "Comforting family dinner spread, hot and steamy food, cozy atmosphere, professional culinary photography",
            "air fryer": "Crispy golden air fryer food, perfectly cooked, highly textured, appetizing food photography",
            "soup": "Warm bowl of comforting soup, steam rising, rustic bread on side, moody food photography",
            "pizza": "Cheesy delicious pizza, wood fired crust, melting cheese pull, appetizing food photography, vibrant colors",
            "healthy": "Fresh vibrant healthy salad or bowl, colorful vegetables, bright lighting, clean food photography"
        }
        for key, prompt in prompt_templates.items():
            if key in topic_lower:
                return prompt
        return f"Appetizing and delicious {topic}, beautifully plated, professional food photography, restaurant quality, warm lighting, 8k"

    def _fetch_pexels_fallback(self, topic: str, title: str) -> dict:
        if not self.pexels_api_key or "YOUR_" in self.pexels_api_key:
            print("   ❌ Pexels API key nahi hai! Placeholder use karunga.")
            return self._create_placeholder_image(title)

        try:
            search_query = self._get_recipe_query(topic)
            url = f"{self.pexels_base_url}/search"
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": search_query, "per_page": 5, "orientation": "portrait"}
            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                photos = response.json().get("photos", [])
                if photos:
                    import random
                    photo = random.choice(photos[:3])
                    img_url = photo["src"]["large2x"]
                    optimized = self._download_and_optimize(img_url, title)
                    optimized.update({
                        "source": "pexels",
                        "photographer": photo.get("photographer", "Pexels")
                    })
                    return optimized
        except Exception as e:
            print(f"   ❌ Pexels error: {e}")
        return self._create_placeholder_image(title)

    def _get_recipe_query(self, topic: str) -> str:
        """Pexels search query for recipes"""
        topic_lower = topic.lower()
        mapping = {
            "pasta": "delicious pasta food",
            "chicken": "cooked chicken dinner",
            "breakfast": "healthy breakfast food",
            "dessert": "sweet dessert cake",
            "dinner": "dinner plate food",
            "soup": "bowl of soup",
            "healthy": "healthy salad food",
            "pizza": "pizza slice cheese",
        }
        for key, query in mapping.items():
            if key in topic_lower:
                return query
        return "delicious food cooking"

    def _draw_text_with_heavy_stroke(self, draw, x, y, text, font, text_color, stroke_color, stroke_width):
        """Draws text with a very thick outline (stroke) by drawing the text multiple times in a circle"""
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width: # Circle shape for smooth stroke
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        # Draw actual text
        draw.text((x, y), text, font=font, fill=text_color)

    def _add_text_overlay(self, img: Image.Image, title: str) -> Image.Image:
        """Viral TikTok Style Overlay: Full image, bold text at the top with heavy strokes"""
        try:
            # We will draw directly on the full 1000x1500 image
            canvas = img.copy()
            draw = ImageDraw.Draw(canvas)
            
            font_path = "Anton-Regular.ttf"
            if not os.path.exists(font_path):
                try:
                    import urllib.request
                    font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf"
                    urllib.request.urlretrieve(font_url, font_path)
                except Exception as e:
                    print(f"   ⚠️ Font download failed: {e}")
            
            try:
                # Top "VIRAL RECIPE" font
                font_top = ImageFont.truetype(font_path, 90)
                # Main Title font
                font_main = ImageFont.truetype(font_path, 140)
            except IOError:
                font_top = ImageFont.load_default()
                font_main = ImageFont.load_default()
                
            # Break title into max 3 lines
            import textwrap
            words = title.upper().split()
            
            # The top red text (e.g. "VIRAL RECIPE" or the first 2 words)
            top_text = "VIRAL RECIPE"
            if len(words) > 4:
                top_text = " ".join(words[:2])
                words = words[2:]
                
            main_lines = textwrap.wrap(" ".join(words), width=12)[:3] # Max 3 lines
            
            # Y position starts at the top
            current_y = 30
            stroke_width = 8
            
            # 1. Draw Top Text (Red with White Stroke)
            try:
                bbox = font_top.getbbox(top_text)
                w = bbox[2] - bbox[0]
            except AttributeError:
                w = len(top_text) * 45
            x = (1000 - w) // 2
            
            self._draw_text_with_heavy_stroke(
                draw, x, current_y, top_text, 
                font=font_top, text_color=(255, 0, 0), stroke_color=(255, 255, 255), stroke_width=stroke_width
            )
            
            try:
                current_y += (bbox[3] - bbox[1]) + 10
            except:
                current_y += 100
                
            # 2. Draw Main Title Lines (Black with White Stroke)
            for line in main_lines:
                try:
                    bbox = font_main.getbbox(line)
                    w = bbox[2] - bbox[0]
                except AttributeError:
                    w = len(line) * 70
                    
                x = (1000 - w) // 2
                
                self._draw_text_with_heavy_stroke(
                    draw, x, current_y, line, 
                    font=font_main, text_color=(10, 10, 10), stroke_color=(255, 255, 255), stroke_width=10
                )
                
                try:
                    current_y += (bbox[3] - bbox[1]) + 15 # Positive spacing to account for thick 10px strokes
                except:
                    current_y += 140
                    
            return canvas
        except Exception as e:
            print(f"   ❌ Viral Text overlay error: {e}")
            return img

    def _download_and_optimize(self, image_url: str, title: str) -> dict:
        try:
            response = requests.get(image_url, timeout=30)
            img = Image.open(BytesIO(response.content))
            
            # Crop to fill 1000x1500 precisely
            img_aspect = img.width / img.height
            target_aspect = 1000 / 1500
            
            if img_aspect > target_aspect:
                new_width = int(img.height * target_aspect)
                offset = (img.width - new_width) // 2
                img = img.crop((offset, 0, offset + new_width, img.height))
            else:
                new_height = int(img.width / target_aspect)
                offset = (img.height - new_height) // 2
                img = img.crop((0, offset, img.width, offset + new_height))

            img = img.resize((1000, 1500), Image.LANCZOS)
            if img.mode != 'RGB': img = img.convert('RGB')
                
            # VIRAL TEXT OVERLAY
            img = self._add_text_overlay(img, title)
            
            if img.mode == 'RGBA': img = img.convert('RGB')

            os.makedirs("temp_images", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"post_{timestamp}.jpg"
            local_path = f"temp_images/{filename}"
            img.save(local_path, "JPEG", quality=90)

            with open(local_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
                
            github_url = f"https://raw.githubusercontent.com/respieauto/recpie/main/temp_images/{filename}"

            return {"local_path": local_path, "base64": img_base64, "url": github_url, "width": 1000, "height": 1500}
        except Exception as e:
            print(f"   ❌ Download/optimize error: {e}")
            return {"local_path": None, "base64": None, "url": None}

    def _create_placeholder_image(self, title: str) -> dict:
        try:
            img = Image.new('RGB', (1000, 1500), color=(255, 240, 230))
            # Text will be added by _add_text_overlay
            img = self._add_text_overlay(img, title)

            os.makedirs("temp_images", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"temp_images/placeholder_{timestamp}.jpg"
            img.save(local_path, "JPEG", quality=90)

            with open(local_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')

            return {"local_path": local_path, "base64": img_base64, "url": None, "source": "placeholder", "photographer": "System Generated", "width": 1000, "height": 1500}
        except Exception as e:
            print(f"   ❌ Placeholder error: {e}")
            return {"local_path": None, "base64": None}

    def get_image_as_bytes(self, local_path: str) -> bytes:
        with open(local_path, "rb") as f: return f.read()

    def cleanup_temp_images(self, max_age_hours=24):
        import time
        if not os.path.exists("temp_images"): return
        now = time.time()
        for filename in os.listdir("temp_images"):
            filepath = os.path.join("temp_images", filename)
            if os.path.getmtime(filepath) < now - (max_age_hours * 3600):
                os.remove(filepath)

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    handler = ImageHandler(config)
    # Test text drawing
    img = Image.new('RGB', (1000, 1500), color=(255, 100, 100))
    img = handler._add_text_overlay(img, "Japanese Fluffy Cheesecake")
    img.save("test_viral_overlay.jpg")
    print("Test image saved to test_viral_overlay.jpg")
