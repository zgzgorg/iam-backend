"""app module to run the application entrypoint"""
import sys
import zgiam.core


def main():
    """this is the real main"""
    zgiam.core.get_app().run()


def init():
    """this is init script that replace the origin `if __name__ == "__main__"`
    inspire by https://medium.com/opsops/how-to-test-if-name-main-1928367290cb

    We want to have error exit the program if error
    """
    if __name__ == "__main__":
        sys.exit(main())


init()
