import random
import numpy as np
import cv2
import argparse
import sys

directions = ((1, 0), (0, 1), (-1, 0), (0, -1))

def randomized_prim(w, h):
    maze = [[1-(x*y)%2 for x in range(2*w+1)] for y in range(2*h+1)]
    unvisited = {(x, y) for x in range(w) for y in range(h)}
    x, y = map(random.randrange, (w, h))
    unvisited.remove((x, y))
    front = [(x, y)] # visited cells that neighbors unvisited cells
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

def window_exist(name):
    # ウインドウが閉じられたかはバックエンドがQtの場合WND_PROP_VISIBLEで調べられるが
    # GTKの場合は判別出来ず-1.0が返る。その場合WND_PROP_AUTOSIZEで調べられる
    r = cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
    if r == -1.0:
        r = cv2.getWindowProperty(name, cv2.WND_PROP_AUTOSIZE)
    return r > 0

def main(w = 18, h = 9, vw = 1280, vh = 1024, make_maze = randomized_prim):
    def line(x0, y0, x1, y1):
        a = max(vw, vh)
        cv2.line(img, (int(vw/2+a*x0), int(vh/2+a*y0)),
                 (int(vw/2+a*x1), int(vh/2+a*y1)), 255)
    maze = make_maze(w, h)
    w, h = w*2+1, h*2+1
    vw = max(vw, w*16)

    x, y, dx, dy = 1, 1, 1, 0
    k = -1
    cv2.namedWindow(title := 'maze')
    while k != ord('q') and window_exist(title):
        if k == ord('w') and not maze[y+dy][x+dx]:
            x, y = x+dx, y+dy
        elif k == ord('s') and not maze[y-dy][x-dx]:
            x, y = x-dx, y-dy
        elif k == ord('a'):
            dx, dy = dy, -dx
        elif k == ord('d'):
            dx, dy = -dy, dx
            
        img = np.zeros((vh + h*16, vw), np.uint8)
        n = 0
        z0 = 1/2
        while maze[y+n*dy][x+n*dx] == 0:
            z1 = 1/(4+8*n)
            for lr in (-1, 1):
                for ud in (-1, 1):
                    if maze[y+n*dy+dx*lr][x+n*dx-dy*lr]:
                        line(z0*lr, z0*ud, z1*lr, z1*ud)
                    else:
                        line(z0*lr, z0*ud, z0*lr, 0)
                        line(z0*lr, z1*ud, z1*lr, z1*ud)
                    if maze[y+n*dy+dy][x+n*dx+dx] == maze[y+n*dy+dx*lr][x+n*dx-dy*lr]:
                        line(z1*lr, 0, z1*lr, z1*ud)
            z0 = z1
            n += 1
        for ud in (-1, 1):
            line(-z0, z0*ud, z0, z0*ud)

        x0, y0 = vw//2-w*8, vh
        for j in range(h):
            for i in range(w):
                cv2.rectangle(img, (x0+i*16, y0+j*16), (x0+i*16+16, y0+j*16+16),
                              255*maze[j][i], cv2.FILLED)
        cv2.arrowedLine(img, (x0+x*16+8-dx*6, y0+y*16+8-dy*6),
                        (x0+x*16+8+dx*5, y0+y*16+8+dy*5),
                        255, tipLength=0.5, thickness = 2)
        cv2.imshow(title, img)
        k = cv2.waitKey(50)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type = int, default = 18,
                        help = '迷路の横幅(既定値 18)')
    parser.add_argument('--height', type = int, default = 9,
                        help = '迷路の縦幅(既定値 9)')
    parser.add_argument('--vwidth', type = int, default = 1280,
                        help = '3D迷路表示部の横幅(既定値 1280)')
    parser.add_argument('--vheight', type = int, default = 1024,
                        help = '3D迷路表示部の縦幅(既定値 1024)')
    parser.add_argument('--gen', default = 'prim',
                        help = '迷路生成アルゴリズム(prim又はdfs)')
    args = parser.parse_args()

    gens = {'prim': randomized_prim, 'dfs': recursive_backtracker}
    if (args.width > 0 and args.height > 0 and args.vheight > 0 and
        args.gen in gens):
        main(args.width, args.height, args.vwidth, args.vheight, gens[args.gen])
    else:
        print('Invalid arguments:', vars(args))
        sys.exit(1)
