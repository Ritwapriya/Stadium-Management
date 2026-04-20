import asyncio
import subprocess
import sys

def run_script(script_name):
    # Runs the script in a separate process
    return subprocess.Popen([sys.executable, f"backend/simulators/{script_name}"])

async def main():
    print("Starting all simulators...")
    
    processes = []
    processes.append(run_script("crowd_sim.py"))
    processes.append(run_script("queue_sim.py"))
    processes.append(run_script("event_sim.py"))
    
    try:
        # Keep the main process alive
        while True:
            await asyncio.sleep(1)
            # Check if any process died
            for i, p in enumerate(processes):
                 if p.poll() is not None:
                     print(f"Simulator process {i} died with return code {p.returncode}")
                     # Restart? For now just exit
                     sys.exit(1)
                     
    except KeyboardInterrupt:
        print("Stopping simulators...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    asyncio.run(main())
