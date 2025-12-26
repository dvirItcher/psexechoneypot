This script is a classic example of a **Named Pipe Impersonation** tool. It mimics a legitimate service (like PsExec) to capture the security token of an incoming connection and spawn a command shell using those credentials.

Here is a structured `README.md` file for your project.

---

# Windows Named Pipe Honeypot & Token Impersonation

This project is a Python-based security tool designed to demonstrate **Named Pipe Impersonation**. It creates a listener on a specific pipe (defaulting to `\.\pipe\PSEXESVC`) and waits for a client (such as a remote administrator or a script) to connect. Upon connection, the script steals the client's access token and spawns an interactive command shell (`cmd.exe`) running under the client's identity.

## 🚀 Features

* **Named Pipe Creation:** Sets up a duplex server pipe using `win32pipe`.
* **Identity Impersonation:** Uses `ImpersonateNamedPipeClient` to assume the security context of the connecting user.
* **Token Elevation:** Duplicates the impersonated token to a primary token to allow the creation of a new process.
* **Interactive Shell:** Provides a full-duplex communication loop between your local console and the spawned `cmd.exe`.
* **Inherited I/O:** Uses anonymous pipes to redirect standard input, output, and error from the child process.

---

## 🛠️ Prerequisites

* **Operating System:** Windows (requires Windows APIs).
* **Language:** Python 3.x.
* **Libraries:** `pywin32`.

To install the required library, run:

```bash
pip install pywin32

```

---

## 📖 How It Works

1. **Listen:** The script creates a named pipe at `\\.\pipe\PSEXESVC`. This is the same pipe name used by Sysinternals **PsExec**, making it an effective honeypot for lateral movement.
2. **Wait:** The script pauses at `ConnectNamedPipe` until a client connects.
3. **Capture:** Once a client connects, the script calls `ImpersonateNamedPipeClient`.
4. **Spawn:** It extracts the user's token and uses `CreateProcessAsUser` to launch `cmd.exe`.
5. **Control:** You can now type commands in your script's window, and they will execute as the captured user.

---

## 💻 Usage

> **Note:** This script requires **Administrative privileges** to successfully create pipes and impersonate other users' tokens.

1. Open a terminal as **Administrator**.
2. Run the script:
```bash
python honeypot.py

```


3. From a different machine (or the same machine), attempt to connect to the pipe. For example, using PsExec:
```bash
psexec \\127.0.0.1 cmd.exe

```


4. Observe the honeypot console to see the captured credentials and the active shell.

---

## ⚠️ Ethical & Legal Warning

This tool is for **educational and authorized security testing purposes only**. Unauthorized access to computer systems is illegal. The author is not responsible for any misuse of this software. Always obtain written permission before testing on systems you do not own.

---

## 🛡️ Mitigation

To protect against this type of attack:

* **Restrict Permissions:** Do not run services or scripts as Domain Admin unless necessary.
* **Pipe Permissions:** Use specific Discretionary Access Control Lists (DACLs) on pipes to restrict who can connect.
* **Monitoring:** Monitor for the creation of suspicious pipes and the use of `ImpersonateNamedPipeClient` in non-standard applications.

---

**Would you like me to add a section on how to modify the script to log all captured commands to a hidden file?**
