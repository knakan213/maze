import random
import numpy as np
import cv2
import argparse
import sys

title = 'maze'
directions = ((1, 0), (0, 1), (-1, 0), (0, -1))

def randomized_prim(w, h):
    maze = [[1-(x*y)%2 for x in range(2*w+1)] for y in range(2*h+1)]
    unvisited = {(x, y) for x in range(w) for y in range(h)}
    x, y = map(random.randrange, (w, h))
    unvisited.remove((x, y))
    front = [(x, y)] # visited cells that neighbor unvisited cells
    while unvisited:
        x, y = random.choice(front)
        dx, dy = random.choice([(dx, dy) for dx, dy in directions
                                if (x+dx, y+dy) in unvisited])
        maze[y*2+1+dy][x*2+1+dx] = 0
        x, y = x+dx, y+dy
        unvisited.remove((x, y))
        front.append((x, y))
        for x2, y2 in [(x+dx, y+dy) for dx, dy in ((0, 0), *directions)
                       if (x+dx, y+dy) in front]:
            if not ({(x2+dx, y2+dy) for dx, dy in directions} & unvisited):
                front.remove((x2, y2))
    return maze

def recursive_backtracker(w, h):
    maze = [[1-(x*y)%2 for x in range(2*w+1)] for y in range(2*h+1)]
    unvisited = {(x, y) for x in range(w) for y in range(h)}
    def rec(x, y):
        unvisited.remove((x, y))
        for dx, dy in random.sample(directions, 4):
            if (x+dx, y+dy) in unvisited:
                maze[y*2+1+dy][x*2+1+dx] = 0
                rec(x+dx, y+dy)
    rec(0, 0)
    return maze

def kabe(w, h):
    maze = [[1-(0 < x < 2*w and 0 < y < 2*h and (x%2 or y%2))
             for x in range(2*w+1)] for y in range(2*h+1)]
    # ここではセルではなくセルの頂点(壁の端点)に(0, 0)〜(w, h)の座標を振っている
    unvisited = {(x, y) for x in range(1, w) for y in range(1, h)}
    while unvisited:
        stack = [random.choice(list(unvisited))]
        while stack[-1] in unvisited:
            x, y = stack.pop()
            while all((x+dx, y+dy) in stack for dx, dy in directions):
                stack.insert(0, (x, y))
                x, y = stack.pop()
            dx, dy = random.choice([(dx, dy) for dx, dy in directions
                                    if (x+dx, y+dy) not in stack])
            stack.extend([(x, y), (x+dx, y+dy)])
            maze[y*2+dy][x*2+dx] = 1
        unvisited -= set(stack)
    return maze

def window_exist(name):
    # ウインドウが閉じられたかはWND_PROP_VISIBLEで調べるが、GTKバックエンドの場合は
    # このプロパティは無効で常に-1.0を返す。その場合WND_PROP_AUTOSIZEで調べられる。
    r = cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
    if r == -1.0:
        r = cv2.getWindowProperty(name, cv2.WND_PROP_AUTOSIZE)
    return r > 0

def main(w, h, vsize, make_maze):
    def line(x0, y0, x1, y1):
        # 3D表示部の左上を(-1/2, -1/2)、右下を(1/2, 1/2)とする座標で
        # 指定された線及びその線をx軸に対して対称移動した線を引く
        for ud in (-1, 1):
            cv2.line(img, (round(vw/2+vsize*x0), round(vsize/2+vsize*y0*ud)),
                     (round(vw/2+vsize*x1), round(vsize/2+vsize*y1*ud)), 255)

    maze = make_maze(w, h)
    w, h = w*2+1, h*2+1
    s = vsize//64 # 2D表示で各セルを表す正方形の一辺の長さ(ドット数)
    vw = max(vsize, w*s)

    x, y, dx, dy = 1, 1, 1, 0
    k = None
    cv2.namedWindow(title)
    while k != 'q' and window_exist(title):
        d = {'w': (x+dx, y+dy, dx, dy), 's': (x-dx, y-dy, dx, dy),
             'a': (x, y, dy, -dx), 'd': (x, y, -dy, dx), None: (x, y, dx, dy)}
        if k in d and not maze[d[k][1]][d[k][0]]:
            x, y, dx, dy = d[k]

            img = np.zeros((vsize + h*s, vw), np.uint8)

            # 3D描画。上下対称になるので、下側(y軸正方向)だけline()に指定する
            n = 0
            # 現在位置から視線の方向に壁に当るまで一歩づつ進めて考える
            while maze[y+n*dy][x+n*dx] == 0:
                for lr in (-1, 1): # 左側(-1)と右側(1)に分けて描画
                    # セルの(表示部分の)隅の座標。手前(x0, y0)と奥(x1, y1)
                    x0, y0, x1, y1 = (a/(4*z) for z in (max(n, 1/2), n+1)
                                      for a in (lr, 1))
                    if maze[y+n*dy+dx*lr][x+n*dx-dy*lr]: # 横が壁の場合
                        line(x0, y0, x1, y1) # 奥に伸びる線
                    else: # 横が道の場合
                        if n:
                            line(x0, y0, x0, 0) # 手前の縦線
                        line(x0, y1, x1, y1) # 奥の横線
                    if (maze[y+n*dy+dy][x+n*dx+dx] ==      # 横と一歩先のセルが
                        maze[y+n*dy+dx*lr][x+n*dx-dy*lr]): # 共に壁か共に道の場合
                        line(x1, 0, x1, y1) # 奥の縦線
                n += 1
            line(-x1, y1, x1, y1) # 最奥の横線

            # 2D描画
            x0, y0 = (vw-w*s)//2, vsize # 2D表示部左上の座標
            for i in range(w):
                for j in range(h):
                    cv2.rectangle(img, (x0+i*s, y0+j*s), (x0+i*s+s-1, y0+j*s+s-1),
                                  maze[j][i] * 255, cv2.FILLED)
            cv2.arrowedLine(img, (x0+x*s+(1-dx)*s//2, y0+y*s+(1-dy)*s//2),
                            (x0+x*s+(1+dx)*s//2, y0+y*s+(1+dy)*s//2),
                            255, tipLength=0.5, thickness = 2)
            cv2.imshow(title, img)
        k = chr(max(0, cv2.waitKey(50)))
    cv2.destroyAllWindows()

if __name__ == '__main__':
    gens = {'prim': randomized_prim, 'dfs': recursive_backtracker, 'kabe': kabe}
    parser = argparse.ArgumentParser()
    for name, v, desc in (('width', 18, '迷路の横幅(2以上)'),
                          ('height', 9, '迷路の縦幅(2以上)'),
                          ('vsize', 1024, '3D迷路表示部の一辺の長さ'),
                          ('gen', 'prim',
                           '迷路生成アルゴリズム(%s)' % ', '.join(gens.keys()))):
        parser.add_argument('--' + name, type = type(v), default = v,
                            help = desc + ' (既定値 %s)' % v)
    args = parser.parse_args()

    if (args.width > 1 and args.height > 1 and args.vsize > 0 and args.gen in gens):
        main(args.width, args.height, args.vsize, gens[args.gen])
    else:
        print('Invalid arguments:', vars(args))
        sys.exit(1)
