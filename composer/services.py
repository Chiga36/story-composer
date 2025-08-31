import requests
import google.generativeai as genai
from django.conf import settings
import urllib.parse
import os
import uuid
import random
import logging
import hashlib
import time

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def enhance_description(self, description):
        """Use Google Gemini to enhance image descriptions"""
        try:
            if not hasattr(self, 'model'):
                return description
            
            prompt = f"""
            Enhance this image description for AI image generation. Make it more detailed and specific for better visual results:
            
            Original: {description}
            
            Enhanced description (keep it under 80 words, detailed but concise):
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else description
        except Exception as e:
            print(f"Error enhancing description: {e}")
            return description
    
    def generate_scene_prompt(self, background_desc, character_desc, position, action):
        """Create a comprehensive prompt for scene generation"""
        try:
            if not hasattr(self, 'model'):
                return self._fallback_scene_prompt(background_desc, character_desc, position, action)
            
            prompt = f"""
            Create a detailed image generation prompt that combines these elements:
            
            Background: {background_desc}
            Character: {character_desc}
            Character Position: {position} side of the image
            Action: {action}
            
            Generate a single, detailed prompt for AI image generation (under 100 words):
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else self._fallback_scene_prompt(background_desc, character_desc, position, action)
        except Exception as e:
            print(f"Error generating scene prompt: {e}")
            return self._fallback_scene_prompt(background_desc, character_desc, position, action)
    
    def _fallback_scene_prompt(self, background_desc, character_desc, position, action):
        """Fallback scene prompt generation without AI"""
        return f"{character_desc} positioned on the {position} side, {action}, in a scene with {background_desc}, high quality, detailed"

class ImageGenerationService:
    
    @staticmethod
    def _try_pollinations_with_retry(prompt, prefix, width=1024, height=768):
        """Try Pollinations with multiple retries and different models"""
        models = ['', 'flux', 'turbo']  # Try different models
        
        for model in models:
            try:
                simple_prompt = prompt[:150] if len(prompt) > 150 else prompt
                encoded_prompt = urllib.parse.quote(simple_prompt)
                
                if model:
                    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width={width}&height={height}&seed={random.randint(1, 10000)}"
                else:
                    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={random.randint(1, 10000)}"
                
                print(f"🎨 Trying Pollinations for {prefix} with model: {model or 'default'}...")
                response = requests.get(api_url, timeout=30)
                
                if response.status_code == 200 and len(response.content) > 1000:
                    filename = f"{prefix}_poll_{model or 'def'}_{uuid.uuid4().hex[:8]}.jpg"
                    media_dir = os.path.join(settings.MEDIA_ROOT, 'generated_images')
                    os.makedirs(media_dir, exist_ok=True)
                    filepath = os.path.join(media_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Pollinations {prefix} image saved: {filename}")
                    return f"{settings.MEDIA_URL}generated_images/{filename}"
                else:
                    print(f"Pollinations model {model} failed with status: {response.status_code}")
                    
            except Exception as e:
                print(f"Pollinations model {model} failed: {e}")
                continue
        
        return None
    
    @staticmethod
    def _create_enhanced_placeholder(prompt, prefix, width=1024, height=768):
        """Create a beautiful enhanced placeholder"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Enhanced color schemes based on prompt
            color_schemes = {
                'beach': [(135, 206, 235), (255, 218, 185), (255, 255, 255)],  # Blue, peach, white
                'sunset': [(255, 140, 0), (255, 165, 0), (255, 255, 255)],     # Orange theme
                'tropical': [(34, 139, 34), (255, 215, 0), (255, 255, 255)],   # Green/gold
                'mountain': [(119, 136, 153), (176, 196, 222), (255, 255, 255)], # Gray blue
                'forest': [(34, 139, 34), (144, 238, 144), (255, 255, 255)],   # Green theme
                'city': [(105, 105, 105), (169, 169, 169), (255, 255, 255)],   # Gray theme
                'sky': [(135, 206, 235), (176, 224, 230), (255, 255, 255)],    # Sky blue
                'ocean': [(25, 25, 112), (100, 149, 237), (255, 255, 255)],    # Deep blue
                'default': [(147, 112, 219), (221, 160, 221), (255, 255, 255)] # Purple theme
            }
            
            # Choose color scheme
            scheme_key = 'default'
            prompt_lower = prompt.lower()
            for key in color_schemes:
                if key in prompt_lower:
                    scheme_key = key
                    break
            
            colors = color_schemes[scheme_key]
            
            # Create gradient background
            img = Image.new('RGB', (width, height), colors[0])
            draw = ImageDraw.Draw(img)
            
            # Create gradient effect
            for i in range(height):
                ratio = i / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            # Add some texture based on theme
            if scheme_key == 'beach':
                # Add wave-like patterns
                for y in range(0, height, 40):
                    for x in range(0, width, 80):
                        draw.arc([x-20, y-10, x+20, y+10], 0, 180, fill=(255, 255, 255, 50))
            elif scheme_key == 'mountain':
                # Add triangle shapes for mountains
                for i in range(5):
                    x = i * (width // 5)
                    draw.polygon([(x, height), (x + width//10, height//2), (x + width//5, height)], 
                               fill=(colors[2][0], colors[2][1], colors[2][2], 80))
            
            # Try to use better fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw title with shadow
            title = f"🎨 {prefix.title()} Preview"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            
            # Shadow
            draw.text((title_x + 2, 42), title, fill=(0, 0, 0, 100), font=title_font)
            # Main text
            draw.text((title_x, 40), title, fill=(255, 255, 255), font=title_font)
            
            # Draw prompt text in a nice box
            box_padding = 50
            box_top = 140
            box_bottom = height - 140
            
            # Draw semi-transparent box
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([box_padding, box_top, width-box_padding, box_bottom], 
                                 fill=(255, 255, 255, 220))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Wrap and draw prompt text
            wrapped_text = textwrap.fill(prompt, width=65)
            lines = wrapped_text.split('\n')
            
            total_text_height = len(lines) * 22
            start_y = (height - total_text_height) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (width - line_width) // 2
                y = start_y + (i * 22)
                draw.text((x, y), line, fill=(60, 60, 60), font=font)
            
            # Add status message
            status_msg = "🔄 AI services busy - Themed placeholder generated"
            status_bbox = draw.textbbox((0, 0), status_msg, font=small_font)
            status_width = status_bbox[2] - status_bbox[0]
            status_x = (width - status_width) // 2
            draw.text((status_x, height - 80), status_msg, fill=(255, 255, 255), font=small_font)
            
            # Add footer
            footer = "Try again later • AI will generate your exact image"
            footer_bbox = draw.textbbox((0, 0), footer, font=small_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = (width - footer_width) // 2
            draw.text((footer_x, height - 50), footer, fill=(255, 255, 255), font=small_font)
            
            # Save image
            filename = f"{prefix}_themed_{uuid.uuid4().hex[:8]}.png"
            media_dir = os.path.join(settings.MEDIA_ROOT, 'generated_images')
            os.makedirs(media_dir, exist_ok=True)
            filepath = os.path.join(media_dir, filename)
            
            img.save(filepath, quality=95)
            print(f"✅ Themed placeholder for {prefix} created: {filename}")
            return f"{settings.MEDIA_URL}generated_images/{filename}"
            
        except Exception as e:
            print(f"Enhanced placeholder creation failed: {e}")
            return None
    
    @staticmethod
    def _create_character_placeholder(prompt, prefix, width=800, height=1024):
        """Create a character-specific placeholder with avatar-style design"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Character-themed color schemes
            character_schemes = {
                'knight': [(70, 70, 70), (150, 150, 150), (220, 220, 220)],      # Metallic gray
                'warrior': [(139, 69, 19), (160, 82, 45), (222, 184, 135)],      # Brown/bronze
                'wizard': [(75, 0, 130), (138, 43, 226), (221, 160, 221)],       # Purple/violet
                'mage': [(25, 25, 112), (65, 105, 225), (173, 216, 230)],        # Blue theme
                'archer': [(34, 139, 34), (107, 142, 35), (154, 205, 50)],       # Green theme
                'rogue': [(47, 79, 79), (105, 105, 105), (169, 169, 169)],       # Dark gray
                'paladin': [(255, 215, 0), (255, 255, 224), (255, 255, 255)],    # Gold/white
                'default': [(105, 105, 105), (169, 169, 169), (211, 211, 211)]   # Gray theme
            }
            
            # Choose color scheme based on character type
            scheme_key = 'default'
            prompt_lower = prompt.lower()
            for key in character_schemes:
                if key in prompt_lower:
                    scheme_key = key
                    break
            
            colors = character_schemes[scheme_key]
            
            # Create background with character silhouette effect
            img = Image.new('RGB', (width, height), colors[0])
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            for i in range(height):
                ratio = i / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)  
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            # Draw a character silhouette shape
            center_x = width // 2
            center_y = height // 2
            
            # Simple character silhouette (head, shoulders, body)
            # Head
            head_radius = 60
            draw.ellipse([center_x - head_radius, center_y - 200, 
                         center_x + head_radius, center_y - 80], 
                        fill=(colors[2][0], colors[2][1], colors[2][2], 100))
            
            # Shoulders/torso
            draw.rectangle([center_x - 80, center_y - 80, center_x + 80, center_y + 100], 
                          fill=(colors[2][0], colors[2][1], colors[2][2], 80))
            
            # Try to use better fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 28)
                font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw title
            title = "🛡️ Character Portrait"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            
            # Shadow
            draw.text((title_x + 2, 42), title, fill=(0, 0, 0, 100), font=title_font)
            # Main text
            draw.text((title_x, 40), title, fill=(255, 255, 255), font=title_font)
            
            # Draw character description in a nice box
            box_padding = 30
            box_top = center_y + 150
            box_bottom = height - 80
            
            # Draw semi-transparent box
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([box_padding, box_top, width-box_padding, box_bottom], 
                                 fill=(255, 255, 255, 220))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Wrap and draw character description
            wrapped_text = textwrap.fill(prompt, width=45)
            lines = wrapped_text.split('\n')
            
            y_offset = box_top + 20
            for line in lines[:4]:  # Limit to 4 lines
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (width - line_width) // 2
                draw.text((x, y_offset), line, fill=(60, 60, 60), font=font)
                y_offset += 20
            
            # Add status message
            status_msg = "🔄 AI Character Generator Busy - Themed Placeholder"
            status_bbox = draw.textbbox((0, 0), status_msg, font=small_font)
            status_width = status_bbox[2] - status_bbox[0]
            status_x = (width - status_width) // 2
            draw.text((status_x, height - 50), status_msg, fill=(255, 255, 255), font=small_font)
            
            # Add footer
            footer = "AI will generate your character art later"
            footer_bbox = draw.textbbox((0, 0), footer, font=small_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = (width - footer_width) // 2
            draw.text((footer_x, height - 25), footer, fill=(255, 255, 255), font=small_font)
            
            # Save image
            filename = f"{prefix}_character_themed_{uuid.uuid4().hex[:8]}.png"
            media_dir = os.path.join(settings.MEDIA_ROOT, 'generated_images')
            os.makedirs(media_dir, exist_ok=True)
            filepath = os.path.join(media_dir, filename)
            
            img.save(filepath, quality=95)
            print(f"✅ Character themed placeholder for {prefix} created: {filename}")
            return f"{settings.MEDIA_URL}generated_images/{filename}"
            
        except Exception as e:
            print(f"Character placeholder creation failed: {e}")
            return None
    
    @staticmethod
    def generate_image(prompt):
        """Generate scene image"""
        print(f"🚀 Starting scene image generation")
        print(f"📝 Scene prompt: {prompt}")
        
        # Try AI services first
        result = ImageGenerationService._try_pollinations_with_retry(prompt, "scene")
        if result:
            return result
        
        # Create enhanced placeholder (NO random photos!)
        print("⚠️ AI services unavailable - creating themed placeholder")
        result = ImageGenerationService._create_enhanced_placeholder(prompt, "scene")
        return result
    
    @staticmethod
    def generate_character_image(description):
        """Generate character image - NO random photos, character-specific fallbacks"""
        enhanced_prompt = f"portrait {description} character design fantasy art"
        
        print(f"🚀 Starting character-specific image generation")
        print(f"📝 Character prompt: {enhanced_prompt}")
        
        # Try AI services first
        result = ImageGenerationService._try_pollinations_with_retry(enhanced_prompt, "character", width=800, height=1024)
        if result:
            return result
        
        # Create character-specific placeholder (NOT random photos!)
        print("⚠️ AI services unavailable - creating character placeholder")
        result = ImageGenerationService._create_character_placeholder(enhanced_prompt, "character", width=800, height=1024)
        return result
    
    @staticmethod
    def generate_background_image(description):
        """Generate background image - NO random photos, themed placeholders"""
        enhanced_prompt = f"{description} landscape environment"
        
        print(f"🚀 Starting background image generation")
        print(f"📝 Background prompt: {enhanced_prompt}")
        
        # Try AI services first
        result = ImageGenerationService._try_pollinations_with_retry(enhanced_prompt, "background")
        if result:
            return result
        
        # Create themed placeholder (NO random photos!)
        print("⚠️ AI services unavailable - creating themed background placeholder")
        result = ImageGenerationService._create_enhanced_placeholder(enhanced_prompt, "background")
        return result
