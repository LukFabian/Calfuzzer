#!/bin/python
import re
import os
from pprint import pprint
import pathlib

BASE_PATH = pathlib.Path(__file__).parent.resolve()

decreased_time = {}
benchmark_bugs = {}


def get_time_results(main_path):
    files = os.listdir(main_path)
    times = []

    if len(files) == 0:
        return 0
    for file in files:
        with open(os.path.join(main_path, file), "r") as f:
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
    avg_time = total_time / len(files)
    return avg_time


def get_deadlockfuzzer_time_results(main_path):
    files = os.listdir(main_path)
    analysis_times = []
    igoodlock_times = []
    for file in sorted(files):
        with open(os.path.join(main_path, file), "r") as f:
            content = f.read()
            result = re.findall("timer: (.*)", content)
            result = [r.split()[0] for r in result]
            if len(result) == 0:
                continue
            analysis_times.extend(result[1:])
            igoodlock_times.append(result[0])

    analysis_total_time = 0
    for t in analysis_times:
        minute = 0
        if ":" in t:
            minute = t.split(":")[0]
            t = t.split(":")[1]
        analysis_total_time += float(t) + int(minute) * 60

    igoodlock_total_time = 0
    for t in igoodlock_times:
        minute = 0
        if ":" in t:
            minute = t.split(":")[0]
            t = t.split(":")[1]
        igoodlock_total_time += float(t) + int(minute) * 60

    avg_time = ((analysis_total_time / len(files)) / 3) + (igoodlock_total_time / len(files))

    return avg_time


def get_deadlockfuzzer_bug_results(benchmark, main_path):
    iter_files = os.listdir(main_path)

    bugs_found = {}
    decreased_time[benchmark] = 0

    for i in iter_files:
        print("\n\niteration {}".format(i))

        bugs_current_iter = {}
        with open(os.path.join(main_path, i), "r") as f:
            content = f.read()
            result = []
            times = []

            if "Printing deadlock" in content:
                result.append(re.findall("Lock .*", content)[0])

            time_result = re.findall("timer: (.*)", content)
            if len(time_result) == 0:
                continue
            initial_run_time = [r.split()[0] for r in time_result][0]
            times.append(initial_run_time)

            current_cycle = None
            deadlock_cycles = []
            last_timer = 0
            for line in content.split("\n"):
                if "cycle" in line:
                    current_cycle = re.findall("cycle (.*)", line)[0]
                    if current_cycle in deadlock_cycles:
                        current_cycle = None
                elif "analysis-once:" in line or "BUILD SUCCESSFUL" in line:
                    if current_cycle is not None:
                        times.append(last_timer)
                    current_cycle = None
                elif "timer" in line:
                    time_result = re.findall("timer: (.*)", line)
                    last_timer = [r.split()[0] for r in time_result][0]
                elif current_cycle is not None and "locations: " in line and current_cycle not in deadlock_cycles:
                    deadlock_cycles.append(current_cycle)
                    result.append(re.findall("locations: (.*)", line)[0])


            # DeadlockFuzzer continues to try to realize a bug even if it was found
            # in one of the previous iterations. We subtract the time it spend
            # on realizing the bugs it has already found before, and allocate the
            # resulting amount of time to SPDOnline.
            for time in times:
                minute = 0
                if ":" in str(time):
                    minute = time.split(":")[0]
                    time = time.split(":")[1]
                decreased_time[benchmark] += float(time) + int(minute) * 60

            for r in result:
                if len(tuple(sorted(r[:-1].split(',')))) > 2 and r.count(',') >= 3:
                    r = tuple((sorted([r[:-1].split(',')[0], r[:-1].split(',')[2]])))
                else:
                    r = tuple(sorted(r[:-1].split(',')))
                if r not in bugs_current_iter:
                    bugs_current_iter[r] = 1
                else:
                    bugs_current_iter[r] += 1

        for r in bugs_current_iter:
            benchmark_bugs[benchmark].add(r)
            if r in bugs_found:
                bugs_found[r] += bugs_current_iter[r]
            else:
                bugs_found[r] = bugs_current_iter[r]

    return bugs_found


def export_result(results):
    tools = ["DeadlockFuzzer"]
    overhead_analysis = ["DeadlockFuzzer-I", "DeadlockFuzzer"]

    num_max_unique_bugs = 0
    for k, _ in results.items():
        if (len(benchmark_bugs[k]) > num_max_unique_bugs):
            num_max_unique_bugs = len(benchmark_bugs[k])

    with open(os.path.join(BASE_PATH, "out.csv"), "w") as f:
        f.write("benchmark,")
        for m in tools:
            f.write("{} Bug Hits,".format(m))
        for m in tools:
            f.write("{} Unique Bugs,".format(m))
        f.write("All Unique Bugs,")

        for i in range(1, num_max_unique_bugs + 1):
            for m in tools:
                f.write("{} Bug{},".format(m, i))
        for m in overhead_analysis:
            f.write("{} Runtime Overhead,".format(m))
        f.write("\n")

        bug_hits = {}
        unique_bug_hits = {}
        for b in benchmarks:
            if b in results:
                print("processing benchmark {}".format(b))
                f.write("{},".format(b))

                bug_hits[b] = {}
                for m in tools:
                    bug_count = 0
                    for x in results[b][m][0]:
                        bug_count += results[b][m][0][x]
                    bug_hits[b][m] = bug_count
                    f.write("{},".format(bug_count))

                unique_bug_hits[b] = {}
                for m in tools:
                    f.write("{},".format(len(results[b][m][0])))
                    unique_bug_hits[b][m] = len(results[b][m][0])
                f.write("{},".format(len(benchmark_bugs[b])))
                unique_bug_hits[b]["all"] = len(benchmark_bugs[b])

                for x in benchmark_bugs[b]:
                    for m in tools:
                        if x in results[b][m][0]:
                            f.write("{},".format(results[b][m][0][x]))
                        else:
                            f.write("0,")

                for i in range(len(benchmark_bugs[b]), num_max_unique_bugs):
                    for _ in tools:
                        f.write("-,")

                for m in overhead_analysis:
                    try:
                        f.write("{},".format(round(results[b][m][1] / results[b]["Native"][1], None)))
                    except:
                        f.write("-,")
                f.write("\n")
        deadlockfuzzer_total_bug_hits = sum([v["DeadlockFuzzer"] for k, v in bug_hits.items()])
        deadlockfuzzer_total_unique_bugs = sum([v["DeadlockFuzzer"] for k, v in unique_bug_hits.items()])
        all_total_unique_bugs = sum([v["all"] for k, v in unique_bug_hits.items()])

        f.write("Totals,{},{},{}\n".format(deadlockfuzzer_total_bug_hits,
                                           deadlockfuzzer_total_unique_bugs,
                                           all_total_unique_bugs))


if __name__ == "__main__":
    outfiles_path = os.path.join(BASE_PATH, "outfiles")
    benchmarks = os.listdir(outfiles_path)

    stats = {}
    results = {}
    for b in benchmarks:
        print("processing {}".format(b))
        benchmark_bugs[b] = set()
        results[b] = {}
        for tool in ["DeadlockFuzzer", "DeadlockFuzzer-I"]:
            main_path = os.path.join(outfiles_path, b, tool)
            if os.path.exists(main_path):
                if tool == "DeadlockFuzzer":
                    results[b][tool] = (get_deadlockfuzzer_bug_results(b, main_path),
                                        get_deadlockfuzzer_time_results(main_path))
                else:
                    results[b][tool] = ("-", get_time_results(main_path))
            else:
                results[b][tool] = ("-", "-")

    pprint(results)
    export_result(results)
