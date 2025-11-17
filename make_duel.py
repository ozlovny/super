from PIL import Image, ImageDraw, ImageFont

def generate_duels(dice1, dice2, duel):
    image_path = f"dice/duel{duel}.png"
    img = Image.open(image_path).convert('RGBA')
    img2 = Image.open(f'dice/dice{dice1}.png').convert('RGBA')
    img3 = Image.open(f'dice/dice{dice2}.png').convert('RGBA')

    draw = ImageDraw.Draw(img)

    ImageDraw.Draw(img2)

    font_path = "dice/black.otf"
    font_size = 150
    font = ImageFont.truetype(font_path, font_size)

    text = f"{dice1} : {dice2}"

    if dice1 == 1 and dice2 == 1:
        text_x = 515
        text_y = 80
    elif dice1 < 2 or dice2 < 2:
        text_x = 490
        text_y = 80
    else:
        text_x = 495
        text_y = 80

    draw.text((text_x, text_y), text, font=font, fill=(143, 117, 255))

    img2 = img2.resize((550, 400))
    img3 = img3.resize((550, 400))
    img.paste(img2, (165, 260), img2)
    img.paste(img3, (665, 260), img3)

    img.save(f"duels/{dice1}_{dice2}_{duel}.png")

if __name__ == "__main__":
    generate_duels(3, 3, 3)