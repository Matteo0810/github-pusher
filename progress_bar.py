import time, sys

progress_time = 0
total_task = 4

def progress(task):
    global progress_time

    time.sleep(0.5)
    progress_time += 1
    sys.stdout.write("\r" + task + " " + str(progress_time) + "% " + '█'*progress_time + ' '*(total_task-progress_time) + ('\n' if progress_time == total_task else ''))