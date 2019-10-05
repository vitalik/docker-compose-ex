import argparse
import json
import os
import subprocess
import sys
import tempfile
import yaml

DEBUG = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="docker-compose.yml")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("composeargs", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True

    run(args.file, args.composeargs)


def run(compose_filename, compose_args):
    result_compose = deep_load(compose_filename)

    with tempfile.TemporaryDirectory() as tmp:
        cur_dir = os.getcwd()
        target = os.path.join(tmp, os.path.basename(cur_dir))
        os.mkdir(target)
        temp_compose_file = os.path.join(target, "docker-compose.yml")
        with open(temp_compose_file, "w") as f:
            json.dump(result_compose, f, indent=1)
            log(json.dumps(result_compose, indent=1))

        cmd = ["docker-compose", "-f", temp_compose_file]
        if "--project-directory=" not in compose_args:
            cmd += ["--project-directory=."]
        cmd += compose_args

        cmd = " ".join(cmd)
        log(cmd)

        subprocess.call(cmd, shell=True)


def deep_load(filename):
    spec = load_yaml(filename)
    if "extends" not in spec:
        return spec
    extends = spec.pop("extends")
    result = deep_load(extends)
    dict_merge(result, spec)
    return result


def dict_merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def load_yaml(filename):
    log("Loading", filename)
    with open(filename) as f:
        return yaml.safe_load(f)


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


if __name__ == "__main__":
    main()
