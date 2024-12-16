import os
import re
import signal
import optparse
import subprocess
import pathlib

BASE_PATH = pathlib.Path(__file__).parent.resolve()
REITERATE_LIMIT = 2
out_files_base = os.path.join(BASE_PATH, "outfiles")
exec_num_file_path = os.path.join(BASE_PATH, "execNumberFile.txt")
run_xml_file = os.path.join(BASE_PATH, "run.xml")
stable_xml_file = os.path.join(BASE_PATH, "run_stable.xml")

ant_path = pathlib.Path.joinpath(BASE_PATH, pathlib.Path("lib"), pathlib.Path("ant-contrib.jar"))
pre_cmds = f"export ANT_HOME={ant_path} export JAVA_HOME={os.environ.get('JAVA_HOME')}"

def get_total_time(benchmark, analysis_name):
    out_path = os.path.join(out_files_base, benchmark, analysis_name)
    times = []
    for file in os.listdir(out_path):
        with open(os.path.join(out_path, file), "r") as f:
            content = f.read()
            result = re.findall("timer: (.*)", content)
            result = [r.split()[0] for r in result]
            times.extend(result)
    total_time = 0
    for t in times:
        minute = 0
        if ":" in t:
            minute = t.split(":")[0]
            t = t.split(":")[1]
        total_time += float(t) + int(minute) * 60
    return total_time


def run_analysis(analysis_name, bench_name, single_run_timeout, num_iter=None, total_timeout=None):
    if num_iter is not None:
        print("\nRunning {} with {} iterations.".format(analysis_name, num_iter))
        prepare_xml_file(analysis_name)
        create_out_folders(out_files_base, bench_name, analysis_name)

        cmd = "{}; ant -f run.xml {}".format(pre_cmds, bench_name)
        execute_cmd(cmd)

        for i in range(0, num_iter):
            print("\t iteration {}".format(i))
            out_file = os.path.join(out_files_base, bench_name, analysis_name, "log_{}.txt".format(i))
            cmd = "{}; ant -f run.xml {} > {}".format(pre_cmds, bench_name, out_file)
            execute_until_succeed(cmd, single_run_timeout)
    elif total_timeout is not None:
        print("\nRunning {} with {:.0f}s total analysis timeout.".format(analysis_name, total_timeout))
        prepare_xml_file(analysis_name)
        create_out_folders(out_files_base, bench_name, analysis_name)
        total_time = get_total_time(bench_name, analysis_name)

        cmd = "{}; ant -f run.xml {}".format(pre_cmds, bench_name)
        execute_cmd(cmd)

        if os.path.exists(exec_num_file_path):
            os.remove(exec_num_file_path)
        i = 0
        while total_time < total_timeout:
            print("\titeration {}".format(i))
            out_file = os.path.join(out_files_base, bench_name, analysis_name, "log_{}.txt".format(i))
            cmd = "{}; ant -f run.xml {} > {}".format(pre_cmds, bench_name, out_file)
            execute_until_succeed(cmd, single_run_timeout)
            total_time = get_total_time(bench_name, analysis_name)
            i += 1


def prepare_xml_file(analysis_name):
    cmd = "cp {} {}".format(stable_xml_file, run_xml_file)
    cmd += "; sed -i 's/target=\"analysis-run\"/target=\"analysis-run-{}\"/g' {}".format(analysis_name, run_xml_file)
    cmd += "; sed -i 's/target=\"instr-run\"/target=\"instr-run-{}\"/g' {}".format(analysis_name, run_xml_file)
    execute_cmd(cmd)


def execute_until_succeed(cmd, timeout, reiterate=True):
    succeeded = False
    reiterate_counter = 0
    while not succeeded and reiterate and reiterate_counter < REITERATE_LIMIT:
        reiterate_counter += 1
        succeeded = execute_cmd(cmd, timeout)


def execute_cmd(cmd, timeout=None):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        if timeout is None:
            p.communicate()
        else:
            p.communicate(timeout=timeout)
        p.wait()
        return True
    except BaseException as e:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        print(str(e))
        return False


def run(bench_name, single_run_timeout, num_iter):
    run_analysis("DeadlockFuzzer", bench_name, single_run_timeout, num_iter=num_iter)
    run_analysis("DeadlockFuzzer-I", bench_name, single_run_timeout, num_iter=num_iter)


def convert2std(input_filename, output_filename):
    output_lines = []
    with open(input_filename, 'r') as f:
        for line in f:
            if "startBefore" in line:
                word = "fork"
            elif "joinAfter" in line:
                word = "join"
            elif "readBefore" in line:
                word = "r"
            elif "writeBefore" in line:
                word = "w"
            elif "lockBefore" in line:
                word = "acq"
            elif "unlockAfter" in line:
                word = "rel"
            else:
                continue

            line = line.strip()
            l = line[line.find("(") + 1:-1]
            iid, thread, loc = l.split(",")

            if word == "acq":
                output = "T{}|{}({})|{}".format(thread, "req", loc, iid)
                output_lines.append(output)

            output = "T{}|{}({})|{}".format(thread, word, loc, iid)
            output_lines.append(output)

    with open(output_filename, "w") as f:
        for line in output_lines:
            f.write("{}\n".format(line))


def record_trace(bench_name):
    pre_cmds = f"export ANT_HOME={pathlib.Path.joinpath(pathlib.Path(BASE_PATH).parent, 'lib', 'ant-contrib.jar')};" \
               f"export JAVA_HOME={os.environ.get('JAVA_HOME')}"
    analysis_name = "PrintTrace"
    print("\nRecording traces.")
    prepare_xml_file(analysis_name)
    create_out_folders(out_files_base, bench_name, analysis_name)
    cmd = "{}; ant -f run.xml {}".format(pre_cmds, bench_name)
    execute_cmd(cmd)

    log_out_file = os.path.join(out_files_base, bench_name, analysis_name, "log.txt")
    cmd = "{}; ant -f run.xml {} > {}".format(pre_cmds, bench_name, log_out_file)
    execute_cmd(cmd)

    std_out_file = os.path.join(out_files_base, bench_name, analysis_name, "{}_dlf.std".format(bench_name))
    convert2std(log_out_file, std_out_file)



def create_out_folders(path, program_name, analysis_name):
    main_path = os.path.join(path, program_name, analysis_name)
    if not os.path.exists(os.path.join(main_path)):
        os.makedirs(os.path.join(main_path))


def get_benchmarks():
    return [
        ("deadlockfuzzer", 10),
    ]


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b", "--benchmarks", dest="benchmarks", default="all",
                      help="run the script on a selected group of benchmarks. " \
                           "Specify the names of the benchmarks and seperate them with a comma " \
                           "(e.g., control-flow,dekker,sigma) (Default: all).")
    parser.add_option("-i", "--iterations", dest="iterations", default=50, type="int",
                      help="number of iterations (Default: 50).")
    parser.add_option("-e", "--exclude", dest="exclude", default="None", type="string",
                      help="exclude the specified benchmarks (Default: None).")
    parser.add_option("-r", "--record", dest="record", default=False, action='store_true',
                      help="record trace (Default: False).")
    (options, args) = parser.parse_args()

    benchmarks = get_benchmarks()
    if options.benchmarks != "all":
        for x in options.benchmarks.split(","):
            if x not in [b[0] for b in benchmarks]:
                print("{} is not a valid benchmark name.".format(x))
        benchmarks = [b for b in benchmarks if b[0] in options.benchmarks.split(",")]
    if options.exclude is not None:
        benchmarks = [b for b in benchmarks if b[0] not in options.exclude.split(",")]

    if not os.path.exists(out_files_base):
        os.mkdir(out_files_base)

    for counter, (bench_name, timeout) in enumerate(benchmarks):
        print("Benchmark: {} ({}/{})".format(bench_name, counter + 1, len(benchmarks)))
        if options.record:
            record_trace(bench_name)
        else:
            run(bench_name, timeout, options.iterations)
        print("----------------------------------\n\n")
