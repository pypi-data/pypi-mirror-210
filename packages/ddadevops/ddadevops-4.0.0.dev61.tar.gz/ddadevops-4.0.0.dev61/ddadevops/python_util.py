from subprocess import check_output, Popen, PIPE
import deprecation


@deprecation.deprecated(deprecated_in="3.2", details="use ExecutionApi instead")
def execute(cmd, shell=False):
    output = check_output(cmd, encoding="UTF-8", shell=shell)
    return output.rstrip()


@deprecation.deprecated(deprecated_in="3.2", details="use ExecutionApi instead")
def execute_live(cmd):
    process = Popen(cmd, stdout=PIPE)
    for line in iter(process.stdout.readline, b""):
        print(line.decode("utf-8"), end="")
    process.stdout.close()
    process.wait()


@deprecation.deprecated(deprecated_in="3.2", details="use domain.filter_none instead")
def filter_none(list_to_filter):
    return [x for x in list_to_filter if x is not None]
