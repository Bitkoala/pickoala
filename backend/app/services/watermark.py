from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from typing import Optional, Tuple
import logging
from app.models.user import User
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def get_font(size: int = 20) -> ImageFont.FreeTypeFont:
    """Try to find a suitable font on the system."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\msyh.ttc", # Microsoft YaHei
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                logger.warning(f"Failed to load font {path}: {e}")
    
    return ImageFont.load_default()


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_watermark(image_bytes: bytes, user: User, config: Optional[dict] = None) -> bytes:
    """
    Apply watermark to image bytes based on user settings or provided config.
    Config dictionary keys: type, text, image_path, opacity, position, color, size
    """
    # Determine settings (config overrides user settings)
    wm_type = config.get('type') if config and config.get('type') else user.watermark_type
    wm_text = config.get('text') if config and config.get('text') else user.watermark_text
    wm_image_path = config.get('image_path') if config and config.get('image_path') else user.watermark_image_path
    
    # Handle numeric values carefully (0 is a valid value)
    wm_opacity = config.get('opacity') if config and config.get('opacity') is not None else user.watermark_opacity
    wm_position = config.get('position') if config and config.get('position') else user.watermark_position
    
    # Extra config-only settings
    wm_color = config.get('color') if config else None
    wm_size = config.get('size') if config else None

    # If no config provided, respect user.watermark_enabled. 
    # If config provided, assume we want to apply it (ignore enabled flag)
    if not config and not user.watermark_enabled:
        return image_bytes
    
    try:
        img = Image.open(BytesIO(image_bytes))
        # Keep original format
        original_format = img.format or 'JPEG'
        
        # Convert to RGBA for drawing
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        width, height = img.size
        
        # Create a layer for the watermark
        watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        opacity = int(wm_opacity * 2.55) # 0-100 to 0-255
        
        if wm_type == 'text' and wm_text:
            # Dynamic font size based on image width or config
            if wm_size:
                font_size = int(wm_size)
            else:
                font_size = max(12, int(width / 20))
            
            font = get_font(font_size)
            
            text = wm_text
            # Get text size
            try:
                # Pillow 9.2.0+
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                # Older Pillow
                text_width, text_height = draw.textsize(text, font=font)
            
            # Position logic
            margin = 20
            if wm_position == 'top-left':
                pos = (margin, margin)
            elif wm_position == 'top-right':
                pos = (width - text_width - margin, margin)
            elif wm_position == 'bottom-left':
                pos = (margin, height - text_height - margin)
            elif wm_position == 'center':
                pos = ((width - text_width) // 2, (height - text_height) // 2)
            else: # bottom-right
                pos = (width - text_width - margin, height - text_height - margin)
            
            # Text color
            text_color = (255, 255, 255)
            if wm_color:
                try:
                    text_color = hex_to_rgb(wm_color)
                except:
                    pass
                
            draw.text(pos, text, font=font, fill=(*text_color, opacity))
            
        elif wm_type == 'image' and wm_image_path:
            # If using config image path, it might be a relative path from uploads or full path?
            # Assuming relative path from uploads folder standard
            full_path = os.path.join(settings.upload_path, wm_image_path)
            if os.path.exists(full_path):
                mark = Image.open(full_path).convert('RGBA')
                
                # Scale watermark
                mw, mh = mark.size
                scale = (width * 0.2) / mw # Watermark is 20% of image width
                mark = mark.resize((int(mw * scale), int(mh * scale)), Image.Resampling.LANCZOS)
                mw, mh = mark.size
                
                # Apply opacity
                alpha = mark.split()[3]
                alpha = alpha.point(lambda p: p * (wm_opacity / 100.0))
                mark.putalpha(alpha)
                
                margin = 20
                if wm_position == 'top-left':
                    pos = (margin, margin)
                elif wm_position == 'top-right':
                    pos = (width - mw - margin, margin)
                elif wm_position == 'bottom-left':
                    pos = (margin, height - mh - margin)
                elif wm_position == 'center':
                    pos = ((width - mw) // 2, (height - mh) // 2)
                else: # bottom-right
                    pos = (width - mw - margin, height - mh - margin)
                
                watermark_layer.paste(mark, pos, mark)
        
        # Merge layer
        out = Image.alpha_composite(img, watermark_layer)
        
        # Convert back if needed (e.g. if original was RGB)
        if original_format == 'JPEG':
            out = out.convert('RGB')
            
        output = BytesIO()
        out.save(output, format=original_format)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error applying watermark: {e}")
        return image_bytes
