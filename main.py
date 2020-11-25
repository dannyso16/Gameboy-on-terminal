import sys
import cv2
import time
import numpy as np

from pyboy import PyBoy, WindowEvent

# TODO: 入力を受け付けるようにする

# 🟥🟧🟨🟩🟦🟪🟫⬛⬜
# dotにすると明らかにFPSが高い（2倍近く速い）
color_parrets = {"hot": ["⬛", "🟨", "🟧", "🟫"],
                 "cool": ["🟨", "🟨", "🟪", "🟦"],
                 "mono": ["⬛", "⬛", "⬜", "⬜"],
                 "dot": ["  ", "⠒⠒", "⠛⣤", "⣿⣿"]}
parret = color_parrets["cool"]
# pythonでは配列アクセスが関数呼び出し並みに遅いのであらかじめ変数にしておく
white, light_gray, dark_gray, black = parret

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
pyboy.set_emulation_speed(1)  # 実機と同じ速度
# 全フレームのうち描画をする割合、{1//skip_rate}に一回程度描画
# skip_rate=1/7.5 で30fps程度
skip_rate = 1/7.5

height = 160
perf_times = []
for frame in range(1000):
    start_time = time.perf_counter()
    pyboy.tick()
    if frame % (1//skip_rate):
        continue
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
                tmp += white
            elif c == 153:
                tmp += light_gray
            elif c == 85:
                tmp += dark_gray
            elif c == 0:
                tmp += black
            else:
                raise ValueError("画素の値がおかしい: {}".format(c))
        screen += tmp + "\n"
    sys.stdout.write(screen)
    sys.stdout.write("\033[{}A".format(height))
    sys.stdout.flush()

    end_time = time.perf_counter()
    if frame < 100:  # exclude pyboy's title logo from performance time
        continue
    perf_times.append(end_time - start_time)

sys.stdout.write("\033[{}B".format(height))

mean_perf_time = (lambda l: sum(l)/len(l))(perf_times)

with open("log.txt", "w") as f:
    f.write("Mean performance time: {}\n".format(mean_perf_time))
    f.write("Mean FPS: {:.1f}".format(1/mean_perf_time * 1//skip_rate))
