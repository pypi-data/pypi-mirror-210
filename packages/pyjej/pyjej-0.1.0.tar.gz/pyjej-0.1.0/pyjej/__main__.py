from invoke import Program
from .tasks import namespace


def main():
    program = Program(namespace=namespace)
    program.run()


if __name__ == "__main__":
    main()
