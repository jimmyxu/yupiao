#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import operator
import os
import subprocess
import sys
from PIL import Image
from template import template, charmap

class OCRError(Exception):
    pass

class OCR:
    def __init__(self, filename):
        img = self._convert(filename)
        pixels = [False if p else True for p in list(img.getdata())]
        self.width, self.height = img.size
        self.pixels = [pixels[i * self.width:(i + 1) * self.width] for i in xrange(self.height)]

    def _convert(self, filename):
        target = filename.replace('.jpg', '.png')
        subprocess.call(['convert', filename, '-monochrome', target])
        try:
            img = Image.open(target)
            os.unlink(target)
        except IOError:
            raise OCRError # 验证码图片获取失败
        return img

    def _print(self):
        for row in self.pixels:
            for col in row:
                if col:
                    print 'x',
                else:
                    print '.',
        print

    def _map(self, x, y, t):
        for row in xrange(len(template[t])):
            if (x + row) >= self.height:
                continue
            #try:
            orig = self.pixels[x + row][y:min(self.width - 1, y + len(template[t][row]))]
            #except IndexError:
            #    return False
            for l in xrange(len(orig)):
                if orig[l] < template[t][row][l]:
                    return False
        return True

    def ocr(self):
        found = []
        for row in xrange(self.height - 8):
            for col in xrange(self.width - 5):
                for temp in template:
                    if self._map(row, col, temp):
                        found.append((row, col, temp))

        result = ''
        for f in sorted(found, key=operator.itemgetter(1)):
            result += str(charmap[f[2]])

        result = result.replace('==', '=')

        try:
            lhs, q = result.split('+')
            q, rhs = q.split('=')
        except ValueError:
            raise OCRError # 未识别操作符

        if not lhs or q != '?' or not rhs:
            raise OCRError # 表达式缺少参数

        result = int(rhs) - int(lhs)
        return result

if __name__ == '__main__':
    i = OCR(sys.argv[1])
    i._print()
    print i.ocr()
