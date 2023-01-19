import sys

from meerkatpm.flow import RouterDispatcher
from meerkatpm.routers import project, build

dispatcher = RouterDispatcher()
dispatcher.add_router(project.router)
dispatcher.add_router(build.router)

def main() -> None:
    if len(sys.argv) < 2:
        print("No command given")
        return
    dispatcher.run_program(sys.argv)

if __name__ == '__main__':
    main()