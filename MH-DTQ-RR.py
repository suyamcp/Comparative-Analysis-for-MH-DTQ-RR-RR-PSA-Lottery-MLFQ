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

# Standard RR time quantum (set before running)
RR_TQ = 4   # 

# PSA priorities per test case:
#   where each inner list contains 5 (unique) priorities for the corresponding test case.
# - If left None, deterministic default priorities [1..n] (by PID order) will be used for each case.
PSA_PRIORITIES_PER_CASE = [[1,2,3,4,5]] * 25


# Lottery: tickets are generated per test case in code (random). If you prefer fixed tickets,
# set LOTTERY_TICKETS_PER_CASE to a list of dicts (one dict per test case). Otherwise leave None.
LOTTERY_TICKETS_PER_CASE = None


# Test groups

#short AT, short BT
group_a = [
    [["P1",0,1], ["P2",1,2], ["P3",2,1], ["P4",3,3], ["P5",4,2]],   # TC1
    [["P1",0,2], ["P2",1,1], ["P3",2,3], ["P4",3,2], ["P5",4,1]],   # TC2
    [["P1",1,1], ["P2",2,2], ["P3",3,2], ["P4",4,1], ["P5",5,3]],   # TC3
    [["P1",0,3], ["P2",1,4], ["P3",2,2], ["P4",3,1], ["P5",4,2]],   # TC4
    [["P1",2,2], ["P2",3,1], ["P3",4,3], ["P4",5,2], ["P5",6,1]],   # TC5
    [["P1",0,4], ["P2",1,3], ["P3",2,2], ["P4",3,1], ["P5",4,5]],   # TC6
    [["P1",1,2], ["P2",2,1], ["P3",3,4], ["P4",4,3], ["P5",5,2]],   # TC7
    [["P1",0,5], ["P2",1,2], ["P3",2,1], ["P4",3,2], ["P5",4,3]],   # TC8
    [["P1",1,3], ["P2",2,2], ["P3",3,1], ["P4",4,4], ["P5",5,2]],   # TC9
    [["P1",0,2], ["P2",1,3], ["P3",2,2], ["P4",3,1], ["P5",4,4]],   # TC10
    [["P1",2,1], ["P2",3,2], ["P3",4,3], ["P4",5,1], ["P5",6,2]],   # TC11
    [["P1",0,1], ["P2",2,2], ["P3",3,1], ["P4",5,2], ["P5",7,3]],   # TC12
    [["P1",1,4], ["P2",2,3], ["P3",4,2], ["P4",6,1], ["P5",8,2]],   # TC13
    [["P1",0,2], ["P2",1,2], ["P3",3,1], ["P4",4,3], ["P5",5,2]],   # TC14
    [["P1",2,3], ["P2",3,1], ["P3",4,2], ["P4",5,1], ["P5",6,3]],   # TC15
    [["P1",0,3], ["P2",1,1], ["P3",2,2], ["P4",4,1], ["P5",5,2]],   # TC16
    [["P1",1,2], ["P2",2,3], ["P3",3,1], ["P4",4,2], ["P5",6,1]],   # TC17
    [["P1",0,1], ["P2",1,5], ["P3",2,2], ["P4",3,2], ["P5",4,1]],   # TC18
    [["P1",2,2], ["P2",3,3], ["P3",4,1], ["P4",5,2], ["P5",6,2]],   # TC19
    [["P1",0,4], ["P2",1,2], ["P3",3,1], ["P4",5,3], ["P5",7,2]],   # TC20
    [["P1",1,1], ["P2",2,2], ["P3",4,3], ["P4",6,1], ["P5",8,2]],   # TC21
    [["P1",0,2], ["P2",1,4], ["P3",2,1], ["P4",3,2], ["P5",4,1]],   # TC22
    [["P1",2,1], ["P2",3,2], ["P3",5,3], ["P4",7,1], ["P5",9,2]],   # TC23
    [["P1",0,3], ["P2",2,1], ["P3",4,2], ["P4",6,3], ["P5",8,1]],   # TC24
    [["P1",1,2], ["P2",2,1], ["P3",3,2], ["P4",4,3], ["P5",5,1]]    # TC25
]

#short AT, long BT
group_b = [
    [["P1",0,12], ["P2",1,14], ["P3",2,11], ["P4",3,16], ["P5",4,13]],
    [["P1",0,15], ["P2",1,11], ["P3",2,18], ["P4",3,12], ["P5",4,14]],
    [["P1",1,13], ["P2",2,16], ["P3",3,12], ["P4",4,19], ["P5",5,11]],
    [["P1",0,11], ["P2",1,12], ["P3",2,14], ["P4",3,15], ["P5",4,17]],
    [["P1",2,16], ["P2",3,13], ["P3",4,11], ["P4",5,14], ["P5",6,12]],
    [["P1",0,18], ["P2",1,13], ["P3",2,12], ["P4",3,11], ["P5",4,15]],
    [["P1",1,11], ["P2",2,19], ["P3",3,13], ["P4",4,12], ["P5",5,14]],
    [["P1",0,14], ["P2",1,11], ["P3",2,16], ["P4",3,18], ["P5",4,12]],
    [["P1",0,12], ["P2",1,15], ["P3",2,13], ["P4",3,11], ["P5",4,20]],
    [["P1",0,11], ["P2",1,17], ["P3",2,12], ["P4",3,14], ["P5",4,13]],
    [["P1",1,13], ["P2",2,11], ["P3",3,15], ["P4",4,16], ["P5",5,12]],
    [["P1",0,14], ["P2",2,12], ["P3",3,11], ["P4",5,18], ["P5",6,13]],
    [["P1",1,12], ["P2",2,13], ["P3",4,11], ["P4",6,15], ["P5",7,14]],
    [["P1",0,16], ["P2",1,11], ["P3",2,14], ["P4",3,12], ["P5",4,13]],
    [["P1",2,11], ["P2",3,19], ["P3",4,12], ["P4",5,13], ["P5",6,15]],
    [["P1",0,12], ["P2",1,15], ["P3",3,11], ["P4",4,14], ["P5",5,16]],
    [["P1",1,17], ["P2",2,12], ["P3",4,13], ["P4",5,11], ["P5",6,14]],
    [["P1",0,11], ["P2",1,13], ["P3",2,18], ["P4",3,12], ["P5",4,16]],
    [["P1",0,14], ["P2",1,11], ["P3",2,12], ["P4",3,19], ["P5",4,13]],
    [["P1",1,12], ["P2",2,15], ["P3",3,11], ["P4",4,17], ["P5",6,13]],
    [["P1",0,13], ["P2",1,12], ["P3",2,16], ["P4",3,14], ["P5",5,11]],
    [["P1",1,11], ["P2",2,14], ["P3",3,12], ["P4",4,13], ["P5",6,19]],
    [["P1",0,15], ["P2",2,11], ["P3",3,13], ["P4",5,12], ["P5",7,14]],
    [["P1",0,11], ["P2",1,12], ["P3",2,14], ["P4",3,20], ["P5",4,13]],
    [["P1",2,13], ["P2",3,11], ["P3",4,15], ["P4",5,12], ["P5",6,16]]
]

#long AT, short BT
group_c = [
    [["P1",11,1], ["P2",12,2], ["P3",13,1], ["P4",14,3], ["P5",15,2]],
    [["P1",11,2], ["P2",12,1], ["P3",14,3], ["P4",15,2], ["P5",16,1]],
    [["P1",12,1], ["P2",13,2], ["P3",14,2], ["P4",15,1], ["P5",17,3]],
    [["P1",11,3], ["P2",12,4], ["P3",13,2], ["P4",14,1], ["P5",15,2]],
    [["P1",12,2], ["P2",13,1], ["P3",14,3], ["P4",15,2], ["P5",16,1]],
    [["P1",11,4], ["P2",12,3], ["P3",13,2], ["P4",14,1], ["P5",15,5]],
    [["P1",12,2], ["P2",13,1], ["P3",14,4], ["P4",15,3], ["P5",16,2]],
    [["P1",11,5], ["P2",12,2], ["P3",13,1], ["P4",14,2], ["P5",15,3]],
    [["P1",12,3], ["P2",13,2], ["P3",14,1], ["P4",15,4], ["P5",16,2]],
    [["P1",11,2], ["P2",12,3], ["P3",13,2], ["P4",14,1], ["P5",15,4]],
    [["P1",12,1], ["P2",13,2], ["P3",14,3], ["P4",15,1], ["P5",16,2]],
    [["P1",11,1], ["P2",12,2], ["P3",13,1], ["P4",15,2], ["P5",17,3]],
    [["P1",12,4], ["P2",13,3], ["P3",15,2], ["P4",16,1], ["P5",18,2]],
    [["P1",11,2], ["P2",12,1], ["P3",13,3], ["P4",14,2], ["P5",15,4]],
    [["P1",12,3], ["P2",13,1], ["P3",14,2], ["P4",15,1], ["P5",16,3]],
    [["P1",11,1], ["P2",12,4], ["P3",13,2], ["P4",14,3], ["P5",15,1]],
    [["P1",12,2], ["P2",13,3], ["P3",14,1], ["P4",15,2], ["P5",16,2]],
    [["P1",11,1], ["P2",12,2], ["P3",13,3], ["P4",14,1], ["P5",15,2]],
    [["P1",12,2], ["P2",13,1], ["P3",14,4], ["P4",15,2], ["P5",16,3]],
    [["P1",11,3], ["P2",12,1], ["P3",13,2], ["P4",14,3], ["P5",15,1]],
    [["P1",12,2], ["P2",13,3], ["P3",14,1], ["P4",15,4], ["P5",16,2]],
    [["P1",11,1], ["P2",12,3], ["P3",13,2], ["P4",15,1], ["P5",17,2]],
    [["P1",12,4], ["P2",13,1], ["P3",14,3], ["P4",15,2], ["P5",16,1]],
    [["P1",11,2], ["P2",12,1], ["P3",14,2], ["P4",16,1], ["P5",18,3]],
    [["P1",12,3], ["P2",13,2], ["P3",14,1], ["P4",15,2], ["P5",16,1]]
]

#long AT, long BT
group_d = [
    [["P1",11,12], ["P2",12,13], ["P3",13,11], ["P4",14,15], ["P5",15,14]],
    [["P1",11,14], ["P2",12,11], ["P3",13,16], ["P4",14,12], ["P5",15,13]],
    [["P1",11,13], ["P2",12,16], ["P3",13,12], ["P4",14,17], ["P5",15,11]],
    [["P1",11,11], ["P2",12,12], ["P3",13,14], ["P4",14,13], ["P5",15,16]],
    [["P1",12,15], ["P2",13,13], ["P3",14,11], ["P4",15,14], ["P5",16,12]],
    [["P1",11,17], ["P2",12,13], ["P3",13,12], ["P4",14,11], ["P5",15,15]],
    [["P1",12,11], ["P2",13,18], ["P3",14,13], ["P4",15,12], ["P5",16,14]],
    [["P1",11,14], ["P2",12,11], ["P3",13,16], ["P4",14,18], ["P5",15,12]],
    [["P1",11,12], ["P2",12,15], ["P3",13,13], ["P4",14,11], ["P5",15,20]],
    [["P1",11,11], ["P2",12,17], ["P3",13,12], ["P4",14,14], ["P5",15,13]],
    [["P1",12,13], ["P2",13,11], ["P3",14,15], ["P4",15,16], ["P5",16,12]],
    [["P1",11,14], ["P2",13,12], ["P3",14,11], ["P4",16,18], ["P5",17,13]],
    [["P1",12,12], ["P2",13,13], ["P3",14,11], ["P4",16,15], ["P5",17,14]],
    [["P1",11,16], ["P2",12,11], ["P3",13,14], ["P4",14,12], ["P5",15,13]],
    [["P1",12,11], ["P2",13,19], ["P3",14,12], ["P4",15,13], ["P5",16,15]],
    [["P1",11,12], ["P2",12,15], ["P3",13,11], ["P4",14,14], ["P5",15,16]],
    [["P1",12,17], ["P2",13,12], ["P3",14,13], ["P4",15,11], ["P5",16,14]],
    [["P1",11,11], ["P2",12,13], ["P3",13,18], ["P4",14,12], ["P5",15,16]],
    [["P1",11,14], ["P2",12,11], ["P3",13,12], ["P4",14,19], ["P5",15,13]],
    [["P1",12,13], ["P2",13,15], ["P3",14,11], ["P4",15,17], ["P5",16,12]],
    [["P1",11,13], ["P2",12,12], ["P3",13,16], ["P4",14,14], ["P5",15,11]],
    [["P1",11,11], ["P2",12,14], ["P3",13,12], ["P4",14,13], ["P5",15,19]],
    [["P1",11,15], ["P2",13,11], ["P3",14,13], ["P4",15,12], ["P5",16,14]],
    [["P1",11,11], ["P2",12,12], ["P3",13,14], ["P4",14,20], ["P5",15,13]],
    [["P1",12,13], ["P2",13,11], ["P3",14,15], ["P4",15,12], ["P5",16,16]]
]

#random
group_e = [
    [["P1",2,11], ["P2",0,3], ["P3",7,17], ["P4",4,6], ["P5",9,2]],
    [["P1",1,5], ["P2",3,14], ["P3",8,4], ["P4",0,12], ["P5",6,9]],
    [["P1",0,7], ["P2",10,2], ["P3",5,13], ["P4",2,18], ["P5",9,6]],
    [["P1",4,8], ["P2",1,11], ["P3",12,3], ["P4",6,15], ["P5",0,9]],
    [["P1",3,16], ["P2",2,1], ["P3",7,10], ["P4",9,5], ["P5",11,4]],
    [["P1",0,20], ["P2",5,2], ["P3",8,7], ["P4",13,6], ["P5",4,12]],
    [["P1",2,9], ["P2",10,15], ["P3",1,3], ["P4",5,14], ["P5",7,2]],
    [["P1",6,11], ["P2",3,8], ["P3",9,4], ["P4",0,17], ["P5",12,1]],
    [["P1",1,6], ["P2",4,13], ["P3",2,5], ["P4",10,12], ["P5",8,2]],
    [["P1",0,9], ["P2",7,3], ["P3",11,16], ["P4",5,2], ["P5",13,10]],
    [["P1",3,2], ["P2",9,7], ["P3",6,14], ["P4",1,11], ["P5",4,5]],
    [["P1",2,10], ["P2",0,4], ["P3",8,15], ["P4",7,1], ["P5",12,9]],
    [["P1",5,6], ["P2",11,3], ["P3",0,13], ["P4",9,8], ["P5",2,12]],
    [["P1",4,14], ["P2",1,2], ["P3",10,9], ["P4",6,5], ["P5",8,11]],
    [["P1",7,16], ["P2",3,7], ["P3",0,4], ["P4",9,12], ["P5",2,1]],
    [["P1",2,8], ["P2",5,13], ["P3",11,2], ["P4",0,17], ["P5",6,10]],
    [["P1",1,9], ["P2",4,1], ["P3",8,19], ["P4",3,6], ["P5",10,5]],
    [["P1",0,11], ["P2",7,4], ["P3",2,12], ["P4",5,3], ["P5",9,14]],
    [["P1",6,2], ["P2",1,15], ["P3",4,8], ["P4",0,13], ["P5",11,7]],
    [["P1",3,10], ["P2",9,1], ["P3",5,16], ["P4",2,6], ["P5",8,12]],
    [["P1",0,5], ["P2",6,14], ["P3",3,2], ["P4",10,18], ["P5",4,9]],
    [["P1",2,7], ["P2",11,3], ["P3",0,13], ["P4",5,16], ["P5",8,1]],
    [["P1",4,12], ["P2",1,6], ["P3",7,9], ["P4",0,2], ["P5",10,18]],
    [["P1",3,14], ["P2",2,4], ["P3",9,11], ["P4",6,7], ["P5",0,5]],
    [["P1",1,8], ["P2",5,17], ["P3",0,3], ["P4",4,10], ["P5",12,2]]
]

# pick group
GROUPS = {"group_a": group_a, "group_b": group_b, "group_c": group_c, "group_d": group_d, "group_e": group_e}
group = GROUPS.get(GROUP_NAME)
if group is None:
    raise ValueError("Invalid GROUP_NAME - set to one of group_a..group_e")


#compute ATAT & AWT from completed list

def compute_metrics_from_completed(completed, processes):
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
    return total_turnaround/n, total_waiting/n


# 1) MH-DTQ-RR

def mh_dtq_rr(processes):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    time = 0
    i = 0
    n = len(proc_list)
    ready_heap = []
    completed = []
    last_exec_time = {p[0]: p[1] for p in proc_list}

    def compute_tq(heap_list):
        if not heap_list:
            return 0
        avg = sum(item[0] for item in heap_list)/len(heap_list)
        return math.ceil(avg)

    while i < n or ready_heap:
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


# 2) RR

def rr(processes, tq=RR_TQ):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    time = 0
    i = 0
    n = len(proc_list)
    ready_queue = []
    completed = []
    remaining = {p[0]: p[2] for p in proc_list}

    while i < n or ready_queue:
        while i < n and proc_list[i][1] <= time:
            ready_queue.append(proc_list[i][0])
            i += 1

        if ready_queue:
            pid = ready_queue.pop(0)
            exec_time = min(tq, remaining[pid])
            time += exec_time
            remaining[pid] -= exec_time
            if remaining[pid] > 0:
                ready_queue.append(pid)
            else:
                completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)


# 3) PSA

def psa(processes, priorities):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    if len(priorities) != len(proc_list):
        priorities_dict = {p[0]: idx+1 for idx, p in enumerate(proc_list)}
    else:
        priorities_dict = {proc_list[i][0]: priorities[i] for i in range(len(proc_list))}

    n = len(proc_list)
    completed = []
    time = 0
    remaining = {p[0]: p[2] for p in proc_list}

    while len(completed) < n:
        available = [p for p in proc_list if p[1]<=time and remaining[p[0]]>0]
        if available:
            chosen = min(available, key=lambda x: (priorities_dict[x[0]], x[0]))
            pid = chosen[0]
            time += remaining[pid]
            remaining[pid] = 0
            completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)


# 4) FCFS (First-Come, First-Served)

def fcfs(processes):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    time = 0
    completed = []

    for pid, arrival, burst in proc_list:
        if time < arrival:
            time = arrival
        time += burst
        completed.append([pid, time])

    return compute_metrics_from_completed(completed, processes)


# 5) SJF (Shortest Job First, Non-Preemptive)

def sjf(processes):
    proc_list = sorted([p[:] for p in processes], key=lambda x: (x[1], x[0]))
    time = 0
    completed = []
    remaining = {p[0]: p[2] for p in proc_list}
    n = len(proc_list)

    while len(completed) < n:
        available = [p for p in proc_list if p[1] <= time and remaining[p[0]] > 0]
        if available:
            chosen = min(available, key=lambda x: (remaining[x[0]], x[0]))
            pid = chosen[0]
            time += remaining[pid]
            remaining[pid] = 0
            completed.append([pid, time])
        else:
            time += 1

    return compute_metrics_from_completed(completed, processes)


# Run group and print table

def run_group(group):
    print(f"Running {GROUP_NAME} with RR_TQ={RR_TQ}")
    header = f"{'Test':<5}{'MH-DTQ-RR':<18}{'RR':<18}{'PSA':<18}{'FCFS':<18}{'SJF':<18}"
    print(header)
    print(f"{'':<5}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}{'ATAT/AWT':<18}")

    for idx, case in enumerate(group, 1):
        processes = deepcopy(case)
        psa_priorities = PSA_PRIORITIES_PER_CASE[idx-1] if PSA_PRIORITIES_PER_CASE else list(range(1,len(processes)+1))

        mh_at, mh_awt = mh_dtq_rr(processes)
        rr_at, rr_awt = rr(processes, tq=RR_TQ)
        psa_at, psa_awt = psa(processes, psa_priorities)
        fcfs_at, fcfs_awt = fcfs(processes)
        sjf_at, sjf_awt = sjf(processes)

        print(f"{idx:<5}{mh_at:.2f}/{mh_awt:.2f}     {rr_at:.2f}/{rr_awt:.2f}     "
              f"{psa_at:.2f}/{psa_awt:.2f}     {fcfs_at:.2f}/{fcfs_awt:.2f}     "
              f"{sjf_at:.2f}/{sjf_awt:.2f}")


if __name__ == "__main__":
    run_group(group)

