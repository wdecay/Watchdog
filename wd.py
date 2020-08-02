import subprocess, time, signal, sys, os, sys, psutil
import logging

max_memory_per_process = 300 # Mb

commands = [
    ["test.py", "1"],
    ["test.py", "2"]
]

sigint_dict = {}
output = [None] * len(commands)

processes = [None] * len(commands)
    
def respawn_dead():
    python = sys.executable
    for i, command in enumerate(commands):
        if processes[i] is None:
            logging.info("Starting process #{}".format(i))

            if output[i] is not None:
                output[i].close()
            output[i] = open("stdout_{}.txt".format(i), "a")
            processes[i] = subprocess.Popen([python] + command,
                                            stdout=output[i])
        elif processes[i] is False:
            pass # finished
        else:
            retval = processes[i].poll()
            if retval is None:
                pass # running
            elif retval == 0:
                logging.info("Process #{} finished successfully.".format(i))
                processes[i] = False
            else:
                logging.warning("Process #{} ended with retval={} and will be restarted".format(i, retval))
                if processes[i] in sigint_dict:
                    del sigint_dict[processes[i]]
                processes[i] = None

def monitor_memory_usage():
    for i, p in enumerate(processes):
        if p and p.poll() is None:
            rss = 0
            try:
                proc = psutil.Process(p.pid)
                mem_info = proc.memory_info()
                rss = mem_info.rss
            except NoSuchProcess:
                pass
            usage_mb = rss // (1024 ** 2)
            if usage_mb > max_memory_per_process and p not in sigint_dict:
                logging.warning("Process #{} is using {} Mb. Sending SIGINT.".format(i, usage_mb))
                p.send_signal(signal.SIGINT)
                sigint_dict[p] = time.time()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while True:
        respawn_dead()
        time.sleep(3)
        monitor_memory_usage()

        if all(p is False for p in processes):
            logging.info("All child processes completed successfully. Exiting.")
            break
