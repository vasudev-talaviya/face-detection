import argparse


parser = argparse.ArgumentParser(description="Face Detection Test")


def cmd():
    parser.add_argument("--test", type=int, choices=[1, 2], help="1 = web camera, 2 = image test")
    parser.add_argument("--image", type=str, help="Image path for image test")

    args = parser.parse_args()
    return args.test, args.image
