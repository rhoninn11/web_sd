from PIL import Image, ImageDraw

def mask_image(img):
    width, height = img.size
    
    mask_image = Image.new('RGB', (width, height), color='black')
    mask_draw_proxy = ImageDraw.Draw(mask_image)

    size = int(width/3)
    x0 = int(width/2) - size
    x1 = int(width/2) + size
    y0 = int(height/2) - size
    y1 = int(height/2) + size
    c_shape = (x0, y0, x1, y1)
    mask_draw_proxy.ellipse(c_shape, fill='white')

    return mask_image

def prepare_img():
    init_img = Image.open('fs/in/img.png').convert('RGB')
    return init_img

def save_img(img):
    img.save(f"fs/out/test.png")

img = prepare_img()
result = mask_image(img)
save_img(result)


