"""app module to run the application entrypoint"""
import sys
import zgiam.core
import zgiam.api
import zgiam.database
import zgiam.auth


def main():
    """this is the real main"""
    app = zgiam.core.get_app()
    zgiam.database.get_db()
    zgiam.api.register_blueprint()
    zgiam.auth.config_auth_apps()
    app.run()


def init():
    """this is init script that replace the origin `if __name__ == "__main__"`
    inspire by https://medium.com/opsops/how-to-test-if-name-main-1928367290cb

    We want to have error exit the program if error
    """
    if __name__ == "__main__":
        sys.exit(main())


init()
