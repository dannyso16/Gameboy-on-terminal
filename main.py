import sys
import cv2
import time
import numpy as np

from pyboy import PyBoy, WindowEvent

# メモ：実行のとき10回くらい [ctrl -]を押すといい感じ
# Check if the ROM is given through argv
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python mario_boiler_plate.py [ROM file]")
    exit(1)

headless = True
pyboy = PyBoy(
    gamerom_file=filename,
    window_type="headless" if headless else "SDL2",
    debug=False
)
pyboy.set_emulation_speed(0)

height = 160
perf_times = []
for frame in range(1000):
    start_time = time.perf_counter()
    pyboy.tick()
    # observation: 画面のRGB値(144, 160, 3)
    observation = np.asarray(pyboy.botsupport_manager(
    ).screen().screen_ndarray(), dtype=np.uint8)

    # グレースケールに (144, 160)
    observation = cv2.cvtColor(observation, cv2.COLOR_BGR2GRAY)

    screen = ""
    for row in observation:
        tmp = ""
        for c in row:
            if c == 255:
                tmp += "⬜"
            elif c == 153:
                tmp += "🟨"
            elif c == 85:
                tmp += "🟧"
            elif c == 0:
                tmp += "🟥"
            else:
                raise ValueError("画素の値がおかしい: {}".format(c))
        screen += tmp + "\n"
    sys.stdout.write(screen)
    sys.stdout.write("\033[{}A".format(height))
    sys.stdout.flush()

    end_time = time.perf_counter()
    perf_times.append(end_time - start_time)

sys.stdout.write("\033[{}B".format(height))

print("Mean performance time: ", sep="")
print((lambda l: sum(l)/len(l))(perf_times))
