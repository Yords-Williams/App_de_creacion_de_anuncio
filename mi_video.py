from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.VideoClip import ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- Parámetros generales ---
W, H = 1280, 720
DUR = 6

# --- Fondo blanco ---
bg = ColorClip(size=(W, H), color=(255, 255, 255), duration=DUR)

# --- Precargar elementos ---
try:
    font_large = ImageFont.truetype("arial.ttf", 32)
    font_small = ImageFont.truetype("arial.ttf", 20)
    font_tienda = ImageFont.truetype("arial.ttf", 24)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_tienda = ImageFont.load_default()

# --- Cargar imagen ---
try:
    zapatilla_img = Image.open("imagen.png")
    if zapatilla_img.mode != 'RGBA':
        zapatilla_img = zapatilla_img.convert('RGBA')

    # Limpieza simple del fondo
    data = np.array(zapatilla_img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    white_threshold = 250
    background_mask = (r > white_threshold) & (g > white_threshold) & (b > white_threshold)
    data[background_mask] = [0, 0, 0, 0]

    zapatilla_limpia = Image.fromarray(data)
    IMAGE_LOADED = True
    print("✅ Imagen cargada correctamente")
except Exception as e:
    IMAGE_LOADED = False
    print(f"❌ Error cargando imagen: {e}")


# --- Función principal CORREGIDA: desaparece solo en el último segundo ---
def make_complete_frame(t):
    # Movimiento simple
    box_x = 100 + int(t * 50)
    if box_x + 900 > W:
        box_x = W - 900

    # Crear frame
    frame = np.ones((H, W, 3), dtype=np.uint8) * 255

    # Animaciones - SOLO DESAPARECE EN EL ÚLTIMO SEGUNDO
    scale = 1.0
    y_offset = 0
    opacity = 1.0

    if t < 1.0:
        # Entrada con salto
        progress = t / 1.0
        scale = 0.5 + 0.5 * progress
        y_offset = -80 * (1 - progress)

    elif t > DUR - 1.0:  # ✅ CORREGIDO: Solo desaparece en el último segundo
        progress = (t - (DUR - 1.0)) / 1.0
        opacity = 1.0 - progress
        scale = 1.0 - 0.3 * progress
        y_offset = 20 * progress

    # Cuadro amarillo
    box_width = int(900 * scale)
    box_height = int(350 * scale)
    box = np.ones((box_height, box_width, 3), dtype=np.uint8) * [255, 230, 0]

    box_y = H // 2 - box_height // 2 + int(y_offset)

    # Dibujar cuadro con opacidad
    if (0 <= box_x < W and 0 <= box_y < H and
            box_x + box_width <= W and box_y + box_height <= H and opacity > 0):

        if opacity < 1.0:
            background_area = frame[box_y:box_y + box_height, box_x:box_x + box_width].copy()
            blended_box = (background_area * (1 - opacity) + box * opacity).astype(np.uint8)
            frame[box_y:box_y + box_height, box_x:box_x + box_width] = blended_box
        else:
            frame[box_y:box_y + box_height, box_x:box_x + box_width] = box

        # --- TEXTO ---
        text1_content = "50% EN TODOS NUESTROS CALZADOS"
        text2_content = "Del 20/10/2025 al 25/10/2025"
        text3_content = "Solo en Tiendas Causa"

        # Calcular anchos necesarios
        temp_img = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        bbox1 = temp_draw.textbbox((0, 0), text1_content, font=font_large)
        text1_w = bbox1[2] - bbox1[0]

        bbox2 = temp_draw.textbbox((0, 0), text2_content, font=font_small)
        text2_w = bbox2[2] - bbox2[0]

        bbox3 = temp_draw.textbbox((0, 0), text3_content, font=font_tienda)
        text3_w = bbox3[2] - bbox3[0]

        # Ancho máximo para el texto
        max_text_width = max(text1_w, text2_w, text3_w) + 40

        # Texto principal - ALINEADO A LA IZQUIERDA
        text1_img = Image.new("RGBA", (max_text_width, 45), (255, 255, 255, 0))
        draw1 = ImageDraw.Draw(text1_img)
        draw1.text((0, 0), text1_content, font=font_large, fill=(0, 0, 0))
        text1_array = np.array(text1_img)

        # Texto secundario - ALINEADO A LA IZQUIERDA
        text2_img = Image.new("RGBA", (max_text_width, 35), (255, 255, 255, 0))
        draw2 = ImageDraw.Draw(text2_img)
        draw2.text((0, 0), text2_content, font=font_small, fill=(0, 0, 0))
        text2_array = np.array(text2_img)

        # Texto "Solo en Tiendas pepe" - ALINEADO A LA IZQUIERDA
        text3_img = Image.new("RGBA", (max_text_width, 40), (255, 255, 255, 0))
        draw3 = ImageDraw.Draw(text3_img)
        draw3.text((0, 0), text3_content, font=font_tienda, fill=(0, 0, 0))
        text3_array = np.array(text3_img)

        # Posiciones del texto (a la izquierda del cuadro)
        total_text_height = 45 + 35 + 40 + 20
        start_y = box_y + (box_height - total_text_height) // 2

        # Texto alineado a la izquierda con margen
        text_margin_left = 30
        text1_pos_x = box_x + text_margin_left
        text1_pos_y = start_y

        text2_pos_x = box_x + text_margin_left
        text2_pos_y = start_y + 50

        text3_pos_x = box_x + text_margin_left
        text3_pos_y = start_y + 100

        # Dibujar texto con opacidad
        if opacity > 0:
            # Texto 1
            if (0 <= text1_pos_y < H and 0 <= text1_pos_x < W and
                    text1_pos_y + 45 <= H and text1_pos_x + max_text_width <= W):

                if opacity < 1.0:
                    text_area = frame[text1_pos_y:text1_pos_y + 45, text1_pos_x:text1_pos_x + max_text_width]
                    text_mask = text1_array[:, :, 3:4] > 0
                    blended_text = np.where(
                        text_mask,
                        text1_array[:, :, :3] * opacity + text_area * (1 - opacity),
                        text_area
                    )
                    frame[text1_pos_y:text1_pos_y + 45, text1_pos_x:text1_pos_x + max_text_width] = blended_text.astype(np.uint8)
                else:
                    frame[text1_pos_y:text1_pos_y + 45, text1_pos_x:text1_pos_x + max_text_width] = np.where(
                        text1_array[:, :, 3:4] > 0,
                        text1_array[:, :, :3],
                        frame[text1_pos_y:text1_pos_y + 45, text1_pos_x:text1_pos_x + max_text_width]
                    )

            # Texto 2
            if (0 <= text2_pos_y < H and 0 <= text2_pos_x < W and
                    text2_pos_y + 35 <= H and text2_pos_x + max_text_width <= W):

                if opacity < 1.0:
                    text_area = frame[text2_pos_y:text2_pos_y + 35, text2_pos_x:text2_pos_x + max_text_width]
                    text_mask = text2_array[:, :, 3:4] > 0
                    blended_text = np.where(
                        text_mask,
                        text2_array[:, :, :3] * opacity + text_area * (1 - opacity),
                        text_area
                    )
                    frame[text2_pos_y:text2_pos_y + 35, text2_pos_x:text2_pos_x + max_text_width] = blended_text.astype(np.uint8)
                else:
                    frame[text2_pos_y:text2_pos_y + 35, text2_pos_x:text2_pos_x + max_text_width] = np.where(
                        text2_array[:, :, 3:4] > 0,
                        text2_array[:, :, :3],
                        frame[text2_pos_y:text2_pos_y + 35, text2_pos_x:text2_pos_x + max_text_width]
                    )

            # Texto 3
            if (0 <= text3_pos_y < H and 0 <= text3_pos_x < W and
                    text3_pos_y + 40 <= H and text3_pos_x + max_text_width <= W):

                if opacity < 1.0:
                    text_area = frame[text3_pos_y:text3_pos_y + 40, text3_pos_x:text3_pos_x + max_text_width]
                    text_mask = text3_array[:, :, 3:4] > 0
                    blended_text = np.where(
                        text_mask,
                        text3_array[:, :, :3] * opacity + text_area * (1 - opacity),
                        text_area
                    )
                    frame[text3_pos_y:text3_pos_y + 40, text3_pos_x:text3_pos_x + max_text_width] = blended_text.astype(np.uint8)
                else:
                    frame[text3_pos_y:text3_pos_y + 40, text3_pos_x:text3_pos_x + max_text_width] = np.where(
                        text3_array[:, :, 3:4] > 0,
                        text3_array[:, :, :3],
                        frame[text3_pos_y:text3_pos_y + 40, text3_pos_x:text3_pos_x + max_text_width]
                    )

        # --- IMAGEN A LA DERECHA (SEPARADA DEL TEXTO) ---
        if IMAGE_LOADED and opacity > 0:
            try:
                # Tamaño de la imagen
                imagen_size = 180
                zapatilla_resized = zapatilla_limpia.resize((imagen_size, imagen_size), Image.Resampling.LANCZOS)
                zapatilla_array = np.array(zapatilla_resized)

                # Posición de la imagen a la DERECHA con MÁRGEN del texto
                imagen_margin_left = max_text_width + 80  # Separación del texto
                imagen_pos_x = box_x + imagen_margin_left
                imagen_pos_y = box_y + (box_height - imagen_size) // 2

                # Animación de flotación suave
                float_offset = int(np.sin(t * 3) * 5)
                imagen_pos_y += float_offset

                # Asegurar que la imagen no se salga del cuadro
                if imagen_pos_x + imagen_size > box_x + box_width - 20:
                    imagen_pos_x = box_x + box_width - imagen_size - 20

                # Dibujar imagen
                if (0 <= imagen_pos_y < H and 0 <= imagen_pos_x < W and
                        imagen_pos_y + imagen_size <= H and imagen_pos_x + imagen_size <= W):

                    for y in range(imagen_size):
                        for x in range(imagen_size):
                            if zapatilla_array[y, x, 3] > 20:
                                target_y = imagen_pos_y + y
                                target_x = imagen_pos_x + x
                                if 0 <= target_y < H and 0 <= target_x < W:
                                    if opacity < 1.0:
                                        current_color = frame[target_y, target_x]
                                        new_color = zapatilla_array[y, x, :3]
                                        blended = current_color * (1 - opacity) + new_color * opacity
                                        frame[target_y, target_x] = blended.astype(np.uint8)
                                    else:
                                        frame[target_y, target_x] = zapatilla_array[y, x, :3]

            except Exception as e:
                print(f"⚠️ Error dibujando imagen: {e}")

    return frame


# --- Crear clip ---
complete_clip = VideoClip(make_complete_frame, duration=DUR)


# --- Fuego CORREGIDO: también desaparece solo en el último segundo ---
def fuego(t):
    frame = np.ones((H, W, 3), dtype=np.uint8) * 255

    fire_opacity = 1.0
    # ✅ CORREGIDO: El fuego también desaparece solo en el último segundo
    if t > DUR - 1.0:
        progress = (t - (DUR - 1.0)) / 1.0
        fire_opacity = 1.0 - progress

    if fire_opacity > 0:
        y = int(500 + 20 * np.sin(10 * t))

        for i in range(60):
            if y + i < H:
                color = [255, 100 + int(40 * np.sin(8 * t)), 0]
                if fire_opacity < 1.0:
                    existing_color = frame[y + i, 250:750]
                    fire_color = np.array([color] * 500)
                    blended = existing_color * (1 - fire_opacity) + fire_color * fire_opacity
                    frame[y + i, 250:750] = blended.astype(np.uint8)
                else:
                    frame[y + i, 250:750] = color

    return frame


fuego_clip = VideoClip(fuego, duration=DUR).with_opacity(0.4)

# --- Composición final ---
final = CompositeVideoClip([bg, fuego_clip, complete_clip])

# --- Exportar video ---
print("🎬 Generando video con duración completa...")
final.write_videofile("anuncio_completo.mp4", fps=24, threads=4, bitrate="2000k")
print("✅ ¡Video terminado! Todo se mantiene visible hasta el último segundo")