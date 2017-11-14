import sys, os
from PIL import Image
from skimage import color, transform, exposure
from MiniSnake import game

game_engine = game()

from config import num_of_cols, num_of_rows

for i in range(9999999):
    _, test, _ = game_engine.play(0)
    if i>200:
        gray = color.rgb2gray(test)
        resized_gray = transform.resize(gray,(num_of_cols,num_of_rows))
        result = Image.fromarray(test, 'RGB')
        result.show()
        result.save('screenshots/screenshot.png')

        #We have the details of all pixels on a screen on this frame. next step is convert it to grayscale and resize it to 80x80

        result = Image.fromarray(gray*255)
        result.show()
        result.convert('RGB').save('screenshots/grayscale.png')
        result = transform.resize(result,(num_of_cols,num_of_rows))
        result.show()
        result.convert('RGB').save('screenshots/downsized.png')


        sys.exit()
