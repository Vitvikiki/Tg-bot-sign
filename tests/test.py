from PIL import Image, ImageDraw, ImageFont
image = Image.new("RGB", (200, 80))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(r"C:\Users\taima\PycharmProjects\WaterMarkTg\core\font\Comic Sans MS.ttf", 30)

draw.text((20, 20), "Hello World", font=font)
bbox = draw.textbbox((20, 20), "Hello World", font=font)
draw.rectangle(bbox, outline="red")
print(bbox)
# (20, 26, 175, 48)

image.show()