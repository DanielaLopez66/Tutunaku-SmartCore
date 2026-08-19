"""
Tutunaku - Sistema CAPTCHA visual
Genera imágenes CAPTCHA con texto aleatorio y las almacena en memoria con expiración.
"""
import io
import random
import secrets
import string
import time
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ============================================
# CAPTCHA STORE (In-Memory con expiración)
# ============================================
_captcha_store: dict[str, Tuple[str, float]] = {}
CAPTCHA_EXPIRY_SECONDS = 300  # 5 minutos


def _cleanup_expired():
    """Elimina CAPTCHAs expirados del store."""
    now = time.time()
    expired_keys = [k for k, (_, t) in _captcha_store.items() if now - t > CAPTCHA_EXPIRY_SECONDS]
    for k in expired_keys:
        del _captcha_store[k]


def generate_captcha_text(length: int = 6) -> str:
    """Genera un texto CAPTCHA aleatorio (letras mayúsculas + dígitos, sin ambigüedad)."""
    # Excluir caracteres ambiguos: 0/O, 1/I/L
    chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    return "".join(random.choice(chars) for _ in range(length))


def generate_captcha_image(text: str, width: int = 280, height: int = 90) -> bytes:
    """
    Genera una imagen CAPTCHA con el texto dado.
    Incluye: fondo con gradiente, ruido, líneas de distracción, texto distorsionado.
    """
    # Crear imagen con fondo gradiente
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Fondo gradiente
    for y in range(height):
        r = int(30 + (y / height) * 40)
        g = int(20 + (y / height) * 30)
        b = int(50 + (y / height) * 60)
        for x in range(width):
            noise_r = random.randint(-15, 15)
            noise_g = random.randint(-15, 15)
            noise_b = random.randint(-15, 15)
            img.putpixel((x, y), (
                max(0, min(255, r + noise_r)),
                max(0, min(255, g + noise_g)),
                max(0, min(255, b + noise_b)),
            ))

    # Líneas de distracción (pocas y delgadas: deben dificultar el OCR
    # automático sin tapar el texto que una persona necesita leer)
    colors = [
        (255, 107, 107, 80),   # coral
        (78, 205, 196, 80),    # teal
        (162, 155, 254, 80),   # violet
        (253, 203, 110, 80),   # gold
    ]
    for _ in range(3):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = random.choice(colors)[:3]
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Puntos de ruido
    for _ in range(120):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )
        draw.point((x, y), fill=color)

    # Texto CAPTCHA
    try:
        font = ImageFont.truetype("arial.ttf", 38)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # Dibujar cada carácter con posición y color aleatorios
    text_colors = [
        (255, 107, 107),   # coral
        (78, 205, 196),    # teal
        (255, 255, 255),   # white
        (253, 203, 110),   # gold
        (162, 155, 254),   # violet
    ]

    char_width = width // (len(text) + 2)
    x_offset = char_width

    for i, char in enumerate(text):
        color = random.choice(text_colors)
        y_offset = random.randint(10, height - 55)

        # Crear imagen temporal para rotación
        char_img = Image.new("RGBA", (50, 60), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)

        # Sombra
        char_draw.text((3, 3), char, font=font, fill=(0, 0, 0, 120))
        # Texto
        char_draw.text((0, 0), char, font=font, fill=color + (255,))

        # Rotar ligeramente (poco: suficiente para dificultar el OCR
        # automático sin volver el carácter ambiguo para una persona)
        angle = random.randint(-12, 12)
        char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)

        # Pegar en la imagen principal
        img.paste(char_img, (x_offset, y_offset), char_img)
        x_offset += char_width

    # Convertir a bytes PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def create_captcha() -> Tuple[str, bytes]:
    """
    Genera un nuevo CAPTCHA y lo almacena en el store.
    Retorna (captcha_id, image_bytes).
    """
    _cleanup_expired()

    text = generate_captcha_text()
    captcha_id = secrets.token_urlsafe(16)
    image_bytes = generate_captcha_image(text)

    _captcha_store[captcha_id] = (text.upper(), time.time())

    return captcha_id, image_bytes


def verify_captcha(captcha_id: str, user_input: str) -> bool:
    """
    Verifica la respuesta del CAPTCHA.
    El CAPTCHA se consume después de un intento (válido o no).
    """
    _cleanup_expired()

    entry = _captcha_store.pop(captcha_id, None)
    if not entry:
        return False

    stored_text, created_at = entry
    if time.time() - created_at > CAPTCHA_EXPIRY_SECONDS:
        return False

    return user_input.upper().strip() == stored_text
