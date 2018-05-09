#!/usr/bin/env python
# encoding: utf-8

################################################################
# File Name: test_net.py
# Author: gaoyu
# Mail: 1400012705@pku.edu.cn
# Created Time: 2018-03-04 15:37:26
################################################################

import os, sys
import argparse
import numpy as np
caffe_path = "/home/linzehui/illu/caffe_illu/python/"
sys.path.append(caffe_path)
import caffe
import lmdb
import skimage.io

#src_dir = '/data3/lzh/10000x672x672_torus_diff/'
src_dir = '/data3/lzh/10000x672x672_box_diff/'
#src_dir = '/data3/lzh/10000x672x672_Diamond_diff'
filelist = os.path.join(src_dir, 'filelist.txt')
img_count = 10

def GetNet(net, weights, gpu):
    caffe.set_device(gpu)
    caffe.set_mode_gpu()
    net = caffe.Net(net, weights, caffe.TEST)
    return net

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--gpu", type = int, default = 0)
    p.add_argument("--net", default = "/home/gaoyu/illu_train/test_resnet_auto.prototxt")
    p.add_argument("model")

    args = p.parse_args()
    net = GetNet(args.net,
                 args.model,
                 gpu = args.gpu)
    cnt = -1
    for line in open(filelist):
        cnt = cnt + 1
        if (cnt >= 10):
            break
        label_filename = line[:-1]

        # process label
        label_img = caffe.io.load_image(os.path.join(src_dir, label_filename))
        shape = label_img.shape
        label = label_img.transpose(2, 0, 1)

        # process data
        base_filename = label_filename[:-9]
        imgs = []
        for i in xrange(1, img_count + 1):
            filename = base_filename + '_' + str(i) + '.png'
            imgs.append(caffe.io.load_image(os.path.join(src_dir, filename)))
        data = np.array(0)
        for img in imgs:
            if data.size == 1:
                data = img.transpose(2, 0, 1)
            else:
                data = np.append(data, img.transpose(2, 0, 1), axis = 0)

        net.blobs['Input1'].data[...] = np.append(label, data, axis = 0)
        net.forward()
        output = net.blobs['Convolution22'].data[0]
        label = net.blobs['Slice1'].data[0]
        loss = net.blobs['Loss'].data
        print loss

        output = np.maximum(0, output)
        output = np.minimum(1, output)
        print output.shape
        pic = np.transpose(output, (1, 2, 0))
        pic2 = np.transpose(label, (1, 2, 0))
        res = np.concatenate((pic, pic2), axis = 1)
        skimage.io.imsave("res" + str(cnt) + ".png", res)

        for key in ["Convolution1", "Eltwise3", "Eltwise6", "Eltwise9", "Deconvolution1", "Deconvolution2", "Deconvolution3"]:
            im = net.blobs[key].data[0][:3, ...]
            im = np.maximum(0, np.minimum(1, im))
            print im.shape
            im = np.transpose(im, (1, 2, 0))
            skimage.io.imsave("%s-%d.png" % (key, cnt), im)
