# scheduling_all_groups.py
import heapq
import math
import random
from copy import deepcopy

# -----------------------------
# CONFIG (edit these for each group run)
# -----------------------------
# Choose group to run: group_a, group_b, group_c, group_d, group_e
GROUP_NAME = "group_a"   # set to "group_a"|"group_b"|"group_c"|"group_d"|"group_e"

# Standard RR time quantum (you set this before running)
RR_TQ = 4   # <-- change here per group run (e.g., 2 for Group A, 4 for Group B, 4 for Group C, 6 for Group D, 4 for Group E)

# PSA priorities per test case:
#   where each inner list contains 5 (unique) priorities for the corresponding test case.
# - If left None, deterministic default priorities [1..n] (by PID order) will be used for each case.
PSA_PRIORITIES_PER_CASE = [[1,2,3,4,5]] * 25


# Lottery: tickets are generated per test case in code (random). If you prefer fixed tickets,
# set LOTTERY_TICKETS_PER_CASE to a list of dicts (one dict per test case). Otherwise leave None.
LOTTERY_TICKETS_PER_CASE = None

# -----------------------------
# Test groups (copied / created earlier)
# -----------------------------
group_a = [
    [["P1",0,3],["P2",1,2],["P3",2,4],["P4",1,1],["P5",0,2]],
    [["P1",0,4],["P2",1,2],["P3",2,3],["P4",0,5],["P5",3,1]],
    [["P1",1,2],["P2",0,3],["P3",2,4],["P4",1,1],["P5",0,2]],
    [["P1",0,5],["P2",2,1],["P3",3,3],["P4",1,2],["P5",0,4]],
    [["P1",1,3],["P2",0,2],["P3",2,5],["P4",0,1],["P5",3,2]],
    [["P1",0,2],["P2",1,4],["P3",2,1],["P4",1,3],["P5",0,5]],
    [["P1",1,4],["P2",0,2],["P3",3,3],["P4",2,1],["P5",0,2]],
    [["P1",0,3],["P2",1,1],["P3",2,5],["P4",0,2],["P5",3,4]],
    [["P1",0,4],["P2",1,2],["P3",2,3],["P4",1,5],["P5",0,1]],
    [["P1",0,2],["P2",1,3],["P3",2,1],["P4",3,4],["P5",0,2]],
    [["P1",1,3],["P2",0,2],["P3",2,4],["P4",1,1],["P5",0,3]],
    [["P1",0,5],["P2",1,2],["P3",3,3],["P4",2,1],["P5",0,4]],
    [["P1",1,2],["P2",0,3],["P3",2,1],["P4",1,4],["P5",0,2]],
    [["P1",0,3],["P2",1,4],["P3",2,2],["P4",1,5],["P5",0,1]],
    [["P1",0,2],["P2",1,3],["P3",2,1],["P4",0,4],["P5",3,2]],
    [["P1",1,4],["P2",0,2],["P3",3,3],["P4",2,1],["P5",0,5]],
    [["P1",0,3],["P2",1,1],["P3",2,4],["P4",0,2],["P5",3,3]],
    [["P1",0,5],["P2",1,2],["P3",2,3],["P4",1,1],["P5",0,4]],
    [["P1",1,2],["P2",0,3],["P3",2,5],["P4",1,1],["P5",0,2]],
    [["P1",0,3],["P2",1,2],["P3",2,4],["P4",0,1],["P5",3,2]],
    [["P1",0,2],["P2",1,3],["P3",2,1],["P4",0,4],["P5",1,5]],
    [["P1",1,3],["P2",0,2],["P3",2,4],["P4",1,1],["P5",0,3]],
    [["P1",0,5],["P2",1,2],["P3",3,1],["P4",2,3],["P5",0,4]],
    [["P1",1,2],["P2",0,3],["P3",2,4],["P4",1,1],["P5",0,2]],
    [["P1",0,3],["P2",1,4],["P3",2,1],["P4",0,5],["P5",3,2]]
]

group_b = [
    [["P1",0,8],["P2",1,10],["P3",0,7],["P4",2,12],["P5",1,9]],
    [["P1",0,9],["P2",1,6],["P3",2,11],["P4",0,7],["P5",3,8]],
    [["P1",1,12],["P2",0,9],["P3",2,8],["P4",1,10],["P5",0,7]],
    [["P1",0,11],["P2",1,8],["P3",2,12],["P4",0,6],["P5",3,9]],
    [["P1",1,7],["P2",0,10],["P3",2,9],["P4",1,12],["P5",0,8]],
    [["P1",0,10],["P2",1,6],["P3",2,11],["P4",0,8],["P5",3,9]],
    [["P1",1,12],["P2",0,7],["P3",2,10],["P4",1,9],["P5",0,8]],
    [["P1",0,6],["P2",1,11],["P3",2,12],["P4",0,9],["P5",3,7]],
    [["P1",0,8],["P2",1,12],["P3",2,9],["P4",1,10],["P5",0,11]],
    [["P1",0,7],["P2",1,8],["P3",2,12],["P4",0,10],["P5",3,6]],
    [["P1",1,9],["P2",0,12],["P3",2,6],["P4",1,11],["P5",0,8]],
    [["P1",0,10],["P2",1,7],["P3",3,9],["P4",2,12],["P5",0,6]],
    [["P1",1,11],["P2",0,8],["P3",2,10],["P4",1,12],["P5",0,9]],
    [["P1",0,7],["P2",1,12],["P3",2,6],["P4",1,11],["P5",0,8]],
    [["P1",0,12],["P2",1,7],["P3",2,10],["P4",0,8],["P5",3,9]],
    [["P1",1,8],["P2",0,11],["P3",3,9],["P4",2,12],["P5",0,6]],
    [["P1",0,10],["P2",1,9],["P3",2,12],["P4",0,6],["P5",3,7]],
    [["P1",0,11],["P2",1,8],["P3",2,10],["P4",1,12],["P5",0,9]],
    [["P1",1,9],["P2",0,12],["P3",2,6],["P4",1,10],["P5",0,7]],
    [["P1",0,8],["P2",1,11],["P3",2,12],["P4",0,9],["P5",3,10]],
    [["P1",0,7],["P2",1,10],["P3",2,9],["P4",0,12],["P5",1,8]],
    [["P1",1,12],["P2",0,7],["P3",2,11],["P4",1,8],["P5",0,9]],
    [["P1",0,6],["P2",1,12],["P3",3,9],["P4",2,10],["P5",0,11]],
    [["P1",1,11],["P2",0,8],["P3",2,12],["P4",1,9],["P5",0,10]],
    [["P1",0,10],["P2",1,7],["P3",2,12],["P4",0,9],["P5",3,8]]
]

group_c = [
    [["P1",0,3],["P2",2,2],["P3",5,1],["P4",7,4],["P5",10,3]],
    [["P1",1,2],["P2",4,3],["P3",6,1],["P4",8,2],["P5",10,5]],
    [["P1",0,1],["P2",3,4],["P3",5,2],["P4",7,3],["P5",9,1]],
    [["P1",2,2],["P2",5,1],["P3",6,3],["P4",8,2],["P5",10,4]],
    [["P1",0,3],["P2",2,2],["P3",4,1],["P4",6,3],["P5",9,2]],
    [["P1",1,4],["P2",3,2],["P3",5,3],["P4",7,1],["P5",10,2]],
    [["P1",0,2],["P2",4,1],["P3",5,3],["P4",7,2],["P5",10,4]],
    [["P1",1,3],["P2",3,2],["P3",6,1],["P4",8,4],["P5",9,2]],
    [["P1",0,2],["P2",2,1],["P3",5,2],["P4",7,3],["P5",10,1]],
    [["P1",1,4],["P2",4,3],["P3",6,2],["P4",8,1],["P5",9,2]],
    [["P1",0,3],["P2",3,2],["P3",5,1],["P4",7,3],["P5",10,4]],
    [["P1",1,2],["P2",4,1],["P3",6,2],["P4",8,3],["P5",9,1]],
    [["P1",0,1],["P2",2,2],["P3",5,3],["P4",7,1],["P5",10,2]],
    [["P1",1,3],["P2",3,2],["P3",6,1],["P4",8,4],["P5",9,2]],
    [["P1",0,2],["P2",4,1],["P3",5,3],["P4",7,2],["P5",10,1]],
    [["P1",1,4],["P2",3,2],["P3",6,2],["P4",8,1],["P5",9,3]],
    [["P1",0,3],["P2",2,2],["P3",5,1],["P4",7,3],["P5",10,2]],
    [["P1",1,2],["P2",4,3],["P3",6,1],["P4",8,2],["P5",9,4]],
    [["P1",0,1],["P2",3,2],["P3",5,3],["P4",7,1],["P5",10,2]],
    [["P1",1,3],["P2",2,1],["P3",6,2],["P4",8,3],["P5",9,1]],
    [["P1",0,2],["P2",3,1],["P3",5,2],["P4",7,4],["P5",10,3]],
    [["P1",1,3],["P2",4,2],["P3",6,1],["P4",8,3],["P5",9,2]],
    [["P1",0,1],["P2",2,3],["P3",5,2],["P4",7,1],["P5",10,2]],
    [["P1",1,4],["P2",3,2],["P3",6,3],["P4",8,1],["P5",9,2]],
    [["P1",0,2],["P2",2,1],["P3",5,3],["P4",7,2],["P5",10,1]]
]

group_d = [
    [["P1",0,6],["P2",2,5],["P3",4,7],["P4",6,8],["P5",8,9]],
    [["P1",1,7],["P2",3,6],["P3",5,8],["P4",7,5],["P5",9,7]],
    [["P1",0,5],["P2",2,9],["P3",4,6],["P4",6,7],["P5",8,8]],
    [["P1",1,8],["P2",3,5],["P3",5,7],["P4",7,9],["P5",10,6]],
    [["P1",0,7],["P2",2,6],["P3",4,8],["P4",6,5],["P5",9,7]],
    [["P1",1,5],["P2",3,7],["P3",5,6],["P4",7,8],["P5",10,9]],
    [["P1",0,6],["P2",2,5],["P3",4,9],["P4",6,7],["P5",8,6]],
    [["P1",1,8],["P2",3,6],["P3",5,7],["P4",7,5],["P5",10,8]],
    [["P1",0,5],["P2",2,7],["P3",4,6],["P4",6,8],["P5",9,7]],
    [["P1",1,6],["P2",3,8],["P3",5,5],["P4",7,9],["P5",10,6]],
    [["P1",0,7],["P2",2,5],["P3",4,6],["P4",6,8],["P5",8,9]],
    [["P1",1,5],["P2",3,7],["P3",5,8],["P4",7,6],["P5",10,7]],
    [["P1",0,6],["P2",2,9],["P3",4,7],["P4",6,5],["P5",9,8]],
    [["P1",1,8],["P2",3,6],["P3",5,9],["P4",7,7],["P5",10,5]],
    [["P1",0,7],["P2",2,8],["P3",4,6],["P4",6,5],["P5",9,9]],
    [["P1",1,5],["P2",3,7],["P3",5,8],["P4",7,6],["P5",10,7]],
    [["P1",0,6],["P2",2,5],["P3",4,9],["P4",6,7],["P5",8,8]],
    [["P1",1,8],["P2",3,6],["P3",5,7],["P4",7,9],["P5",10,6]],
    [["P1",0,5],["P2",2,7],["P3",4,6],["P4",6,8],["P5",9,7]],
    [["P1",1,6],["P2",3,8],["P3",5,5],["P4",7,9],["P5",10,6]],
    [["P1",0,7],["P2",2,5],["P3",4,6],["P4",6,8],["P5",8,9]],
    [["P1",1,5],["P2",3,7],["P3",5,8],["P4",7,6],["P5",10,7]],
    [["P1",0,6],["P2",2,9],["P3",4,7],["P4",6,5],["P5",9,8]],
    [["P1",1,8],["P2",3,6],["P3",5,9],["P4",7,7],["P5",10,5]],
    [["P1",0,7],["P2",2,8],["P3",4,6],["P4",6,5],["P5",9,9]]
]

# static random-like group (example) for group_e (so results repeat unless you change it)
group_e = [
    [["P1",1,7],["P2",4,3],["P3",2,9],["P4",0,5],["P5",3,6]],
    [["P1",2,4],["P2",1,8],["P3",3,5],["P4",5,2],["P5",0,7]],
    [["P1",0,6],["P2",2,7],["P3",4,3],["P4",1,9],["P5",3,5]],
    [["P1",1,8],["P2",0,4],["P3",2,6],["P4",3,7],["P5",5,2]],
    [["P1",3,5],["P2",1,7],["P3",0,6],["P4",4,8],["P5",2,3]],
    [["P1",0,9],["P2",3,2],["P3",1,5],["P4",4,6],["P5",2,8]],
    [["P1",2,6],["P2",0,4],["P3",3,7],["P4",1,9],["P5",5,5]],
    [["P1",1,3],["P2",4,8],["P3",0,6],["P4",2,7],["P5",3,5]],
    [["P1",0,7],["P2",2,5],["P3",1,9],["P4",3,4],["P5",5,6]],
    [["P1",3,6],["P2",0,8],["P3",1,5],["P4",2,7],["P5",4,3]],
    [["P1",1,5],["P2",2,6],["P3",0,8],["P4",3,4],["P5",5,7]],
    [["P1",2,7],["P2",0,3],["P3",1,5],["P4",4,9],["P5",3,6]],
    [["P1",0,4],["P2",1,8],["P3",3,5],["P4",2,6],["P5",5,7]],
    [["P1",1,9],["P2",3,2],["P3",0,7],["P4",2,5],["P5",4,6]],
    [["P1",2,6],["P2",0,5],["P3",1,8],["P4",3,7],["P5",5,4]],
    [["P1",0,8],["P2",2,3],["P3",1,6],["P4",4,9],["P5",3,5]],
    [["P1",1,7],["P2",0,4],["P3",2,5],["P4",3,8],["P5",5,6]],
    [["P1",0,5],["P2",2,9],["P3",1,6],["P4",3,4],["P5",4,7]],
    [["P1",1,8],["P2",3,5],["P3",0,6],["P4",2,7],["P5",4,3]],
    [["P1",2,6],["P2",0,9],["P3",1,5],["P4",3,7],["P5",5,4]],
    [["P1",0,7],["P2",1,3],["P3",2,6],["P4",4,8],["P5",3,5]],
    [["P1",1,6],["P2",0,8],["P3",2,4],["P4",3,9],["P5",5,7]],
    [["P1",0,5],["P2",2,7],["P3",1,9],["P4",3,6],["P5",4,8]],
    [["P1",1,9],["P2",3,5],["P3",0,7],["P4",2,6],["P5",4,4]],
    [["P1",0,6],["P2",1,8],["P3",2,5],["P4",3,7],["P5",4,9]]
]

# pick group
GROUPS = {"group_a": group_a, "group_b": group_b, "group_c": group_c, "group_d": group_d, "group_e": group_e}
group = GROUPS.get(GROUP_NAME)
if group is None:
    raise ValueError("Invalid GROUP_NAME - set to one of group_a..group_e")

# -----------------------------
# Utility: compute ATAT & AWT from completed list
# -----------------------------
def compute_metrics_from_completed(completed, processes):
    """completed: list of [pid, completion_time]"""
    n = len(processes)
    total_turnaround = 0
    total_waiting = 0
    for pid, comp_time in completed:
        arrival = next(p[1] for p in processes if p[0] == pid)
        burst = next(p[2] for p in processes if p[0] == pid)
        turnaround = comp_time - arrival
        waiting = turnaround - burst
        total_turnaround += turnaround
        total_waiting += waiting
    ATAT = total_turnaround / n
    AWT = total_waiting / n
    return ATAT, AWT

# -----------------------------
# 1) MH-DTQ-RR
# deterministic (no randomness)
# -----------------------------
def mh_dtq_rr(processes):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))  # stable order by arrival then PID
    time = 0
    i = 0
    n = len(proc_list)
    ready_heap = []  # heap entries: (remaining_burst, pid, arrival_time)
    completed = []
    last_exec_time = {p[0]: p[1] for p in proc_list}

    def compute_tq(heap_list):
        # heap_list contains heap items [rem, pid, arrival]
        if not heap_list:
            return 0
        avg = sum(item[0] for item in heap_list) / len(heap_list)
        return math.ceil(avg)  # round up ALWAYS

    while i < n or ready_heap:
        # enqueue all that arrived at current time, in deterministic PID order if same arrival
        while i < n and proc_list[i][1] <= time:
            rem = proc_list[i][2]
            pid = proc_list[i][0]
            arr = proc_list[i][1]
            heapq.heappush(ready_heap, [rem, pid, arr])
            i += 1

        if ready_heap:
            tq = compute_tq(ready_heap)
            rem, pid, arr = heapq.heappop(ready_heap)
            exec_time = min(tq, rem)
            time += exec_time
            rem -= exec_time
            last_exec_time[pid] = time
            if rem > 0:
                heapq.heappush(ready_heap, [rem, pid, time])
            else:
                completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)

# -----------------------------
# 2) Standard RR (deterministic)
# RR_TQ at top
# -----------------------------
def rr(processes, tq=RR_TQ):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    time = 0
    i = 0
    n = len(proc_list)
    ready_queue = []  # deterministic queue, append in PID order for simultaneous arrivals
    completed = []
    remaining = {p[0]: p[2] for p in proc_list}
    last_exec_time = {p[0]: p[1] for p in proc_list}

    while i < n or ready_queue:
        # add arrived processes (if multiple arrived at same time, add in PID sorted order)
        while i < n and proc_list[i][1] <= time:
            ready_queue.append(proc_list[i][0])
            i += 1

        if ready_queue:
            pid = ready_queue.pop(0)
            exec_time = min(tq, remaining[pid])
            # deterministic update
            time += exec_time
            remaining[pid] -= exec_time
            last_exec_time[pid] = time
            if remaining[pid] > 0:
                ready_queue.append(pid)
            else:
                completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)

# -----------------------------
# 3) PSA (Priority Scheduling Algorithm) - non-preemptive here
# PSA_PRIORITIES_PER_CASE controls priorities (deterministic)
# priorities: lower number => higher priority
# -----------------------------
def psa(processes, priorities):
    # priorities: list of ints in same order as processes sorted by arrival then PID
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    if len(priorities) != len(proc_list):
        # fallback: deterministic default 1..n by PID order (stable)
        priorities_dict = {p[0]: idx+1 for idx, p in enumerate(proc_list)}
    else:
        priorities_dict = {proc_list[i][0]: priorities[i] for i in range(len(proc_list))}

    n = len(proc_list)
    completed = []
    time = 0
    remaining = {p[0]: p[2] for p in proc_list}

    # non-preemptive: pick available at current time with highest priority (lowest number)
    while len(completed) < n:
        available = [p for p in proc_list if p[1] <= time and remaining[p[0]] > 0]
        if available:
            # choose by priority then PID (deterministic)
            chosen = min(available, key=lambda x: (priorities_dict[x[0]], x[0]))
            pid = chosen[0]
            time += remaining[pid]
            remaining[pid] = 0
            completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)

# -----------------------------
# 4) Lottery Scheduling (randomized)
# tickets are provided per test case or generated randomly here
# -----------------------------
def lottery(processes, tickets):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    n = len(proc_list)
    completed = []
    time = 0
    remaining = {p[0]: p[2] for p in proc_list}

    while len(completed) < n:
        available = [p for p in proc_list if p[1] <= time and remaining[p[0]] > 0]
        if available:
            pool = []
            for p in available:
                pool.extend([p[0]] * tickets[p[0]])
            # random draw (no seed) - result will vary each run
            pid = random.choice(pool)
            # run 1 unit (typical lottery step)
            time += 1
            remaining[pid] -= 1
            if remaining[pid] == 0:
                completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)

# -----------------------------
# 5) MLFQ (deterministic)
# Strict ordering: tie-break by PID; no randomness
# 3 levels, quantums can be changed here if desired
# -----------------------------
def mlfq(processes, quantums=(4,8,12)):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    n = len(proc_list)
    time = 0
    i = 0
    queues = [[] for _ in quantums]  # queues store PIDs
    remaining = {p[0]: p[2] for p in proc_list}
    completed = []
    # Strict deterministic rules:
    # - When multiple processes arrive at same time, insert them into top queue in PID order
    # - When demoting, append to tail (FIFO)
    # - No random tie-breaking

    while len(completed) < n:
        # add newly arrived in deterministic order
        while i < n and proc_list[i][1] <= time:
            queues[0].append(proc_list[i][0])
            i += 1

        executed = False
        for lvl, tq in enumerate(quantums):
            if queues[lvl]:
                pid = queues[lvl].pop(0)
                exec_time = min(tq, remaining[pid])
                time += exec_time
                remaining[pid] -= exec_time
                if remaining[pid] > 0:
                    # demote to next queue if exists, otherwise stay
                    if lvl + 1 < len(quantums):
                        queues[lvl+1].append(pid)
                    else:
                        queues[lvl].append(pid)
                else:
                    completed.append([pid, time])
                executed = True
                break
        if not executed:
            time += 1

    return compute_metrics_from_completed(completed, processes)

# -----------------------------
# Run chosen group and print compact table (ATAT / AWT)
# -----------------------------
def run_group(group):
    print(f"Running {GROUP_NAME} with RR_TQ={RR_TQ}")
    header = f"{'Test':<5}{'MH-DTQ-RR':<18}{'RR':<18}{'PSA':<18}{'Lottery':<18}{'MLFQ':<18}"
    print(header)
    print(f"{'':<5}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}")

    for idx, case in enumerate(group, 1):
        processes = deepcopy(case)  # avoid mutation
        # PSA priorities: use provided per-case list if PSA_PRIORITIES_PER_CASE given
        if PSA_PRIORITIES_PER_CASE and len(PSA_PRIORITIES_PER_CASE) >= idx:
            psa_priorities = PSA_PRIORITIES_PER_CASE[idx-1]
        else:
            # deterministic default: priorities 1..n by PID order in arrival-sorted list
            sorted_proc = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
            psa_priorities = list(range(1, len(sorted_proc)+1))

        # Lottery tickets: use provided per case or generate random ones now (random each run)
        if LOTTERY_TICKETS_PER_CASE and len(LOTTERY_TICKETS_PER_CASE) >= idx:
            lottery_tickets = LOTTERY_TICKETS_PER_CASE[idx-1]
        else:
            # random generate tickets between 1 and 5 per process for this test case
            lottery_tickets = {p[0]: random.randint(1,5) for p in processes}

        mh_at, mh_awt = mh_dtq_rr(processes)
        rr_at, rr_awt = rr(processes, tq=RR_TQ)
        psa_at, psa_awt = psa(processes, psa_priorities)
        lot_at, lot_awt = lottery(processes, lottery_tickets)
        mlfq_at, mlfq_awt = mlfq(processes)

        print(f"{idx:<5}{mh_at:.2f}/{mh_awt:.2f}     {rr_at:.2f}/{rr_awt:.2f}     "
              f"{psa_at:.2f}/{psa_awt:.2f}     {lot_at:.2f}/{lot_awt:.2f}     {mlfq_at:.2f}/{mlfq_awt:.2f}")

# run
if __name__ == "__main__":
    run_group(group)