import sys

from meerkatpm.routers.router import RouterDispatcher
from meerkatpm.routers import project

dispatcher = RouterDispatcher()
dispatcher.add_router(project.router)

def main() -> None:
    if len(sys.argv) < 2:
        print("No command given")
        return
    dispatcher.dispatch(sys.argv[1], sys.argv[2:])

if __name__ == '__main__':
    main()