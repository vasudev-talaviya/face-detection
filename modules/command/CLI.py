import argparse


parser = argparse.ArgumentParser(description="Face Detection Test")

def cmd():

    parser.add_argument('--test',type=int,choices=[1,2],help='1 = Webcamera open\n 2 = Image Test',)

    parser.add_argument('--image',type=str,help='Image Path for Image Test')

    args = parser.parse_args()

    DEFAULT_TEST = args.test
    IMAGE_PATH = args.image


    return DEFAULT_TEST , IMAGE_PATH