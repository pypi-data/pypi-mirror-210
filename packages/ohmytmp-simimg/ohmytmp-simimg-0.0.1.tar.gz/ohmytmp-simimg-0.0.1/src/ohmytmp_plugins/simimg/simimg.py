import cv2
import numpy as np

from ohmytmp import PluginAfter, Info, TYPE


def ahash64(pth: str) -> int:
    try:
        img = cv2.imread(pth, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, (8, 8), cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        return -1

    avg = np.mean(img)
    ans = 0
    for i in img:
        for j in i:
            ans = (ans << 1) | (0 if j < avg else 1)
    return ans


def dhash64(pth: str) -> int:
    try:
        img = cv2.imread(pth, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, (9, 8), cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        return -1

    ans = 0
    for i in img:
        l = None
        flg = True
        for j in i:
            if flg:
                l = j
                flg = False
                continue
            ans = (ans << 1) | (0 if j < l else 1)
            l = j
    return ans


def phash64(pth: str) -> int:
    try:
        img = cv2.imread(pth, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, (32, 32), cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        return -1

    img = cv2.dct(np.float64(img))[0:8, 0:8]
    avg = np.mean(img)
    ans = 0
    for i in img:
        for j in i:
            ans = (ans << 1) | (0 if j < avg else 1)
    return ans


def hamming_distance(h1: int, h2: int) -> int:
    d = h1 ^ h2
    ans = 0
    while d:
        ans += 1
        d &= d-1
    return ans


class SimImg(PluginAfter):
    def __init__(self) -> None:
        self.data = dict()

        def __func(info: Info):
            if info.TYPE != TYPE.IMAGE:
                return
            self.add(info.SRC)

        super().__init__(__func)

    def findsim(self, x: int, d: int) -> list:
        return [i for i in self.data if hamming_distance(self.data[i], x) <= d]

    def add(self, pth: str) -> None:
        self.data[pth] = phash64(pth)


LSHBIT = 64


class SimImgPlus(PluginAfter):
    def __init__(self, distance: int = 8) -> None:
        if distance < 0 or distance >= LSHBIT:
            raise ValueError(distance)
        self.distance = distance
        self.m = max(distance+1, 4)
        # 4 5 [13 13 13 13 12]
        self.split = list(range(self.m)) * (LSHBIT//self.m + 1)
        self.block = dict()
        self.data = dict()

        def __func(info: Info):
            if info.TYPE != TYPE.IMAGE:
                return
            self.add(info.SRC)

        super().__init__(__func)

    def phash(self, pth: str) -> tuple:
        try:
            img = cv2.imread(pth, cv2.IMREAD_UNCHANGED)
            img = cv2.resize(img, (32, 32), cv2.INTER_AREA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            return -1

        img = cv2.dct(np.float64(img))[0:8, 0:8].flatten()
        avg = np.mean(img)
        ansl = [0] * self.m
        for i, j in enumerate(img):
            w = 0 if j < avg else 1
            ans = ans << 1 | w
            ansl[i % self.m] = (ansl[i % self.m] << 1) | w
        for i, j in enumerate(ansl):
            ansl[i] = ansl[i]*self.m + i
        return ans, ansl

    def findsim(self, x: int, d: int) -> list:
        return [i[1] for i in self.block if hamming_distance(i[0], x) <= d]

    def add(self, pth: str) -> None:
        ans, ansl = self.phash(pth)
        for i in ansl:
            self.block.setdefault(i, list())
            self.block[i].append(pth)
        self.data[pth] = ans
