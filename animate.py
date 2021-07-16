import copy
import cv2
import numpy as np
from draw_state import draw_state

def make_video(scramble, solution, tps):
    # opencv video writer
    size = (400, 400)
    writer = cv2.VideoWriter("movie.webm", cv2.VideoWriter_fourcc(*'VP90'), tps, size)

    # create a copy so we don't modify the original
    pos = copy.deepcopy(scramble)
    for i in range(solution.length()):
        move = solution.at(i)
        pos.move(move)

        # draw the state and send it to the video writer
        image = draw_state(pos)
        cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        writer.write(cv2_image)

    # finish the video
    writer.release()