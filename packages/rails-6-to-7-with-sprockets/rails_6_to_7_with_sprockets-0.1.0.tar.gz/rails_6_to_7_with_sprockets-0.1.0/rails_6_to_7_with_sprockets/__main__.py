from .cli import run_pipeline
import sys

def main():
    path = "."
    editor = "vim"
    acceptable_editors = set(["vim", "subl", "code", "nvim"])

    if len(sys.argv) > 1:
        path = sys.argv[1]

    if len(sys.argv) > 2 and editor in acceptable_editors:
        editor = sys.argv[2]

    run_pipeline(path, editor)

if __name__ == "__main__":  # pragma: no cover
    main()
