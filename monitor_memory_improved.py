#!/usr/bin/env python3
"""
monitor_memory_improved.py
- prints memory + cpu
- prints top N processes by RSS
- supports --interval, --threshold, --top, --log-file
"""
import argparse, time, psutil, logging
from datetime import datetime
from textwrap import shorten

def bytes_to_mib(b): return b/1024/1024

def top_procs(n=8):
    procs=[]
    for p in psutil.process_iter(['pid','name','cmdline','memory_info','cpu_percent']):
        try:
            mem = p.info['memory_info'].rss if p.info.get('memory_info') else 0
            cmd = " ".join(p.info.get('cmdline') or [])
            procs.append((mem, p.pid, p.info.get('name') or '', p.info.get('cpu_percent') or 0, cmd))
        except Exception:
            continue
    procs.sort(reverse=True, key=lambda x: x[0])
    return procs[:n]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interval", "-i", type=float, default=30.0)
    p.add_argument("--threshold", "-t", type=float, default=80.0)
    p.add_argument("--top", type=int, default=8)
    p.add_argument("--log-file", default=None)
    args=p.parse_args()
    logger=None
    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        logger=logging.getLogger()

    print(f"🔍 Memory Monitor Started (threshold: {args.threshold}%)")
    try:
        while True:
            mem=psutil.virtual_memory()
            cpu=psutil.cpu_percent(interval=0.5)
            status = "🔴" if mem.percent>=args.threshold else "🟢"
            print(f"{status} {datetime.now():%H:%M:%S} | Memory: {mem.percent:.1f}% ({mem.used//(1024**3)}GB/{mem.total//(1024**3)}GB) | CPU: {cpu:.1f}%")
            if mem.percent>=args.threshold:
                print("⚠️  WARNING: High memory usage detected!")
                procs=top_procs(args.top)
                print("Top processes by RSS:")
                print(f"{'PID':>6} {'RSS(MB)':>9} {'CPU%':>6} {'Name':<25} Cmdline")
                for mem, pid, name, cpu, cmd in procs:
                    print(f"{pid:>6} {bytes_to_mib(mem):9.1f} {cpu:6.1f} {shorten(name,25)} {shorten(cmd,120)}")
            if logger:
                logger.info({"mem_percent": mem.percent, "used": mem.used, "cpu": cpu})
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n✅ Monitor stopped")

if __name__=="__main__":
    main()
