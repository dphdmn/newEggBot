from PIL import Image, ImageDraw, ImageFont

def color(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def makeImage(w, h):
    img = Image.new("RGB", (w, h))
    return img, ImageDraw.Draw(img, 'RGBA')

def drawSquare(img, x, y, r, color):
    shape = [(x, y), (x+r, y+r)]
    img.rectangle(shape, fill=color)
    return img

def drawTile(im, draw, xP, yP, col, text):
    size = 100
    x = xP*size
    y = yP*size
    font = ImageFont.truetype("font.ttf", int(size/2))
    W = size
    H = size
    w, h = draw.textsize(text, font=font)
    if text != "0":
        drawSquare(draw, x, y, size, col)
        draw.text(((W-w)/2+x, (H-h)/2+y), text, fill="black", font=font)
    else:
        mask = Image.new('L', im.size, color=255)
        mask_d = ImageDraw.Draw(mask)
        drawSquare(mask_d, x, y, size, 0)
        im.putalpha(mask)

def draw_state(state):
    img, draw = makeImage(400, 400)

    tileColors = [color(255, 103, 103),
                  color(255, 163, 87),
                  color(255, 241, 83),
                  color(193, 255, 87),
                  color(123, 255, 97),
                  color(107, 255, 149),
                  color(121, 255, 222),
                  color(131, 230, 255),
                  color(139, 178, 255),
                  color(154, 141, 255),
                  color(207, 141, 255),
                  color(255, 133, 251)]
    colorCords = [[0, 0, 0, 0], [2, 4, 4, 4], [2, 6, 8, 8], [2, 6, 9, 10]]

    for y in range(state.height()):
        for x in range(state.width()):
            number = state.arr[y][x]
            cord = colorCords[y][x]
            mycolor = tileColors[cord]
            drawTile(img, draw, x, y, mycolor, str(number))

    return img
