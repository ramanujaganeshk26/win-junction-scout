import os
import sys
import argparse

def get_reparse_target(path):
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        OPEN_EXISTING = 3

        h_file = kernel32.CreateFileW(
            path,
            0,
            0,
            None,
            OPEN_EXISTING,
            FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        if h_file == wintypes.HANDLE(-1).value:
            return None

        MAXIMUM_REPARSE_DATA_BUFFER_SIZE = 16384
        out_buffer = ctypes.create_string_buffer(MAXIMUM_REPARSE_DATA_BUFFER_SIZE)
        bytes_returned = wintypes.DWORD(0)
        FSCTL_GET_REPARSE_POINT = 0x000900A8

        success = kernel32.DeviceIoControl(
            h_file,
            FSCTL_GET_REPARSE_POINT,
            None,
            0,
            out_buffer,
            len(out_buffer),
            ctypes.byref(bytes_returned),
            None
        )
        kernel32.CloseHandle(h_file)

        if not success:
            return None

        return "Resolved Reparse Point"
    except Exception:
        return None

def scan_directory(root_path):
    issues = []
    visited = set()
    
    for base, dirs, files in os.walk(root_path, topdown=True, followlinks=False):
        real_base = os.path.realpath(base)
        if real_base in visited:
            issues.append({"type": "LOOP", "path": base})
            continue
        visited.add(real_base)

        for d in dirs:
            full_path = os.path.join(base, d)
            if os.path.islink(full_path):
                target = os.readlink(full_path)
                if not os.path.exists(target):
                    issues.append({"type": "BROKEN_SYMLINK", "path": full_path, "target": target})
    return issues

def main():
    parser = argparse.ArgumentParser(description="Win Junction Scout")
    parser.add_argument("path", nargs="?", default=".", help="Target directory to scan")
    args = parser.parse_args()
    issues = scan_directory(args.path)
    for issue in issues:
        print(f"[{issue['type']}] {issue['path']}")

if __name__ == "__main__":
    main()
