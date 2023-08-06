import sys, argparse, os
from .platform import YAMLPlatformFile

def run(arguments):
    parser = argparse.ArgumentParser(description='Run a simulation')
    parser.add_argument("platform", help="Run a simulation using a specific platform file")
    args = parser.parse_args(arguments[1:])
    if args.platform:
        simulation=YAMLPlatformFile(args.platform)
        # Allow importlib (in simulator.run()) to import file from the platform.yaml directory
        sys.path.insert(0, simulation.location)
        simulation.run()
    else:
        parser.print_help()

def main():
    ##### Parse arguments
    parser = argparse.ArgumentParser(
        description='ESDS simulator command line interface. Run simulations and perform various simulation tasks.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command", help="Execute the specified command.\nAvailable commands are: run", nargs=argparse.REMAINDER)
    parser.add_argument("--version", help="Show esds version", action="store_true")
    args = parser.parse_args()

    ##### Run commands
    if args.command:
        if args.command[0] == "run":
            run(args.command)
    elif args.version:
        print("ESDS v"+__version__)
    else:
        parser.print_help()
