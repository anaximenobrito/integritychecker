# Author: Anaximeno Brito

import readinst
import hashlib
import os
from time import sleep
from alive_progress import alive_bar
from termcolor import colored


hashlist = {
    "md5": hashlib.md5(),
    "sha1": hashlib.sha1(),
    "sha224": hashlib.sha224(),
    "sha256": hashlib.sha256(),
    "sha384": hashlib.sha384(),
    "sha512": hashlib.sha512()
}

# don't change this number
BUF_SIZE = 32768


def gen_data(dt):
    if dt:
        yield dt


# read all sums
def all_sums(f_name):
    with alive_bar(len(hashlist), bar='blocks', spinner='dots') as bar:
        for s_type in hashlist:
            with open(f_name, 'rb') as f:
                while True:
                    try:
                        data = gen_data(f.read(BUF_SIZE))
                        hashlist[s_type].update(next(data))
                        sleep(0.00001)  # when lower is this value, faster will be the reading,
                        # but it will use more CPU
                    except StopIteration:
                        break
            bar()


# read and set the file's sum
def readata(f_name, s_type):

    def rep(s):
        t = 0
        while s > 0:
            s -= BUF_SIZE
            t += 1
            yield t

    size = os.path.getsize(f_name)
    times = 0
    for x in rep(size):
        times = x

    with alive_bar(times, bar='filling', spinner='dots') as bar:
        with open(f_name, 'rb') as f:
            while True:
                try:
                    data = gen_data(f.read(BUF_SIZE))
                    hashlist[s_type].update(next(data))
                    sleep(0.00001)  # when lower is this value, faster will be the reading,
                    # but it will use more CPU
                    bar()
                except StopIteration:
                    break


# check is the file's sum is equal to the given sum
def check(f_sum, s_type, f_name):
    x = int(f_sum, 16)
    h = hashlist[s_type].hexdigest()
    if int(h, 16) == x:
        print('')  # jump one line
        print('-' * 65)
        print(colored(f"  #SUCESS, the {s_type}sum did match!", "green"))
        print('-' * 65)
        print(f"\n-> '{f_name}' {s_type}sum: {h}")
        print(f"\n-> Match with the given sum: {f_sum}")
    else:
        print('')  # jump one line
        print('-' * 65)
        print(colored(f"  %FAIL, the {s_type}sum did not match!", "red"))
        print('-' * 65)
        print(f"\n-> '{f_name}' {s_type}sum: {h}")
        print(f"\n-> Don't Match with the given sum: {f_sum}")


# if we have the file's name and sum
def normal(s_type, f_name, f_sum):
    if readinst.analyze_file(f_name, f_sum):
        readata(f_name, s_type)
        check(f_sum, s_type, f_name)


# if the file's name and sum is in a sum.txt file
def text(txt):
    f_name, f_sum, s_type = readinst.analyze_text(txt)
    if f_name and f_sum and s_type:
        readata(f_name, s_type)
        check(f_sum, s_type, f_name)


# get all sums
def allsums(f_name):
    if readinst.exists(f_name):
        all_sums(f_name)
        output = ""
        for typo in hashlist:
            output += f" {typo}sum: {hashlist[typo].hexdigest()}\n"
        print(f"\nAll '{f_name}' sums below: ")
        print(output)
    else:
        print(f"checksum: error: '{f_name}' was not found in this directory!")


# if we want only show the sum and no to compare it
def only_sum(s_type, f_name):
    if readinst.exists(f_name):
        readata(f_name, s_type)
        print(f"'{f_name}' {s_type}sum is {hashlist[s_type].hexdigest()}")
    else:
        print(f"checksum: error: '{f_name}' was not found in this directory!")