#               R    G    B
white = (255, 255, 255)
gray = (185, 185, 185)
black = (0, 0, 0)
red = (155, 0, 0)
light_red = (175, 20, 20)
green = (0, 155, 0)
light_green = (20, 175, 20)
blue = (0, 0, 155)
light_blue = (20, 20, 175)
yellow = (155, 155, 0)
light_yellow = (175, 175, 20)

colors = (blue, green, red, yellow)
light_colors = (light_blue, light_green, light_red, light_yellow)

assert len(colors) == len(light_colors)  # each color must have light color
