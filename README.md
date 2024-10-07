# Maze
[randomized Prim's](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Iterative_randomized_Prim's_algorithm_(without_stack,_without_sets))や[recursive backtracker](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Randomized_depth-first_search)といった迷路生成アルゴリズムによって生成した迷路をの中を、[Maze War](https://en.wikipedia.org/wiki/Maze_(1973_video_game))風の一人称視点で歩き回ることの出来るシミュレーションです。歩き回ることが出来るだけでゲーム性はありません。

## 必要環境
- Python3
- OpenCV

## インストール
例えば以下のようにして、このリポジトリの内容をディレクトリに展開し、そのディレクトリに移動して下さい。
```
git clone https://github.com/knakan213/maze.git
cd maze
```

## 使い方
> Linux or Mac
```
python3 maze.py
```
> Windows
```
python maze.py
```
とすると迷路がランダムに生成され、上部に大きく3D表示、下部に小さく2D表示されます。2D表示の中の矢印はプレイヤーの視点の位置と向きを表わしており、開始時には迷路の一番左上のマスに右向きで置かれています。

![screenshot](screenshot.png)

### 操作方法
| キー | 動作                       |
|------|----------------------------|
| w    | 前方に進む                 |
| s    | 後方に下る                 |
| a    | 視点を左に90度回転する     |
| d    | 視点を右に90度回転する     |
| q    | シミュレーションを終了する |

### コマンドラインオプション
以下の通り、コマンドラインオプションにより迷路や3D表示部の大きさ、迷路の生成アルゴリズムを指定することが出来ます。
```
usage: maze.py [-h] [--width WIDTH] [--height HEIGHT] [--vwidth VWIDTH]
               [--vheight VHEIGHT] [--gen GEN]

options:
  -h, --help         show this help message and exit
  --width WIDTH      迷路の横幅(既定値 18)
  --height HEIGHT    迷路の縦幅(既定値 9)
  --vwidth VWIDTH    3D迷路表示部の横幅(既定値 1280)
  --vheight VHEIGHT  3D迷路表示部の縦幅(既定値 1024)
  --gen GEN          迷路生成アルゴリズム(prim又はdfs)
```
