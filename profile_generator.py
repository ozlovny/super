from PIL import Image, ImageDraw, ImageFont


def truncate_string(text, max_length):
    text = str(text)
    if len(text) > max_length:
        return text[:max_length-2] + ".."
    else:
        return text

def draw_profile(user_id, username, level, days, refs, total_got, till_new):
    try:
        username = truncate_string(username, 8)

        background = Image.open("background.jpg")

        font_path = "SF-Pro-Display-Bold.otf"
        font_large = ImageFont.truetype(font_path, 100)
        font_medium = ImageFont.truetype(font_path, 80)
        font_small = ImageFont.truetype(font_path, 50)
        font_level = ImageFont.truetype(font_path, 60)

        draw = ImageDraw.Draw(background)

        green = (34, 208, 77)

        def draw_text(text, font, position, text_color=(255, 255, 255)):
            draw.text(position, text, font=font, fill=text_color)

        days = str(days)
        days_int = int(days)

        if days_int == 1:
            draw_text(days, font_large, (175, 215), green)
        elif days_int < 10:
            draw_text(days, font_large, (170, 215), green)
        elif days_int > 99:
            draw_text("99+", font_large, (105, 215), green)
        elif days_int == 10:
            draw_text(days, font_large, (150, 215), green)
        else:
            draw_text(days, font_large, (145, 215), green)

        refs = str(refs)
        refs_int = int(refs)

        if refs_int == 1:
            draw_text(refs, font_large, (175, 475), green)
        elif refs_int < 10:
            draw_text(refs, font_large, (170, 475), green)
        elif refs_int > 99:
            draw_text("99+", font_large, (105, 475), green)
        elif refs_int == 10:
            draw_text(refs, font_large, (150, 475), green)
        else:
            draw_text(refs, font_large, (145, 475), green)

        draw_text(f"{username}", font_small, (969, 65))

        level = str(level)
        level_int = int(level)

        if level_int == 1:
            draw_text(f"{level}", font_level, (896, 60), green)
        else:
            draw_text(f"{level}", font_level, (890, 60), green)

        draw_text(f"{int(total_got)} $", font_medium, (630, 290), green)
        draw_text(f"{int(till_new)} $", font_medium, (630, 525), green)

        output_path_numbers_only = f"profiles/{user_id}_banner.png"
        background.save(output_path_numbers_only)
    except Exception as e:
        print(f"Error when generating image: {e}")


if __name__ == "__main__":
    draw_profile("123456789", 'vemorr', '1', '0', '0', '0', '150')
