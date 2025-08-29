#!/usr/bin/env python3
"""
Simple status checker for running Denario pipelines.
"""

import os
import subprocess
import sys
from datetime import datetime

def check_running_processes():
    """Check for running Denario processes."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        denario_processes = []
        for line in lines:
            if 'restart_denario' in line and 'grep' not in line:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    cmd = parts[10]
                    denario_processes.append({
                        'pid': pid,
                        'cpu': cpu,
                        'mem': mem,
                        'cmd': cmd
                    })
        
        return denario_processes
    except Exception as e:
        print(f"Error checking processes: {e}")
        return []

def check_log_file():
    """Check the log file for recent activity."""
    log_path = "/tmp/denario_output.log"
    if os.path.exists(log_path):
        try:
            # Get file modification time
            mod_time = os.path.getmtime(log_path)
            mod_datetime = datetime.fromtimestamp(mod_time)
            
            # Get file size
            size = os.path.getsize(log_path)
            
            # Get last few lines
            with open(log_path, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) >= 5 else lines
            
            return {
                'exists': True,
                'last_modified': mod_datetime,
                'size_kb': size // 1024,
                'last_lines': [line.strip() for line in last_lines]
            }
        except Exception as e:
            return {'exists': True, 'error': str(e)}
    else:
        return {'exists': False}

def check_output_files():
    """Check for recent output files."""
    project_dir = "/workspaces/Denario/project_gemini"
    if os.path.exists(project_dir):
        try:
            # Find recently modified files
            result = subprocess.run([
                'find', project_dir, '-type', 'f', '-mmin', '-30'
            ], capture_output=True, text=True)
            
            recent_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return recent_files
        except Exception as e:
            return []
    return []

def main():
    """Main status check function."""
    print("🔍 Denario Pipeline Status Check")
    print("=" * 50)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check running processes
    print("🔄 Running Processes:")
    processes = check_running_processes()
    if processes:
        for proc in processes:
            print(f"  📍 PID {proc['pid']} - CPU: {proc['cpu']}% - Memory: {proc['mem']}%")
            print(f"     Command: {proc['cmd'][:80]}...")
    else:
        print("  ❌ No Denario processes currently running")
    print()
    
    # Check log file
    print("📄 Log File Status:")
    log_info = check_log_file()
    if log_info['exists']:
        if 'error' in log_info:
            print(f"  ⚠️  Error reading log: {log_info['error']}")
        else:
            print(f"  📝 Last modified: {log_info['last_modified']}")
            print(f"  📊 Size: {log_info['size_kb']} KB")
            print("  📋 Recent output:")
            for line in log_info['last_lines']:
                print(f"     {line}")
    else:
        print("  ❌ No log file found at /tmp/denario_output.log")
    print()
    
    # Check output files
    print("📁 Recent Output Files:")
    recent_files = check_output_files()
    if recent_files:
        print(f"  ✅ {len(recent_files)} files modified in last 30 minutes:")
        for f in recent_files[-5:]:  # Show last 5
            print(f"     {f}")
        if len(recent_files) > 5:
            print(f"     ... and {len(recent_files) - 5} more")
    else:
        print("  ❌ No recent output files found")
    print()
    
    # Quick commands help
    print("💡 Useful Commands:")
    print("  📺 Watch live log: tail -f /tmp/denario_output.log")
    print("  🔍 Check processes: ps aux | grep restart_denario")
    print("  📁 List outputs: find project_gemini -type f -mmin -60")
    print("  ⏹️  Stop process: kill -TERM <PID>")

if __name__ == "__main__":
    main()
