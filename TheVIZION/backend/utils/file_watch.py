# utils/file_watch.py
from __future__ import annotations
import os, time, threading, json, hashlib
from fnmatch import fnmatch
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import httpx

class _Handler(FileSystemEventHandler):
    def __init__(self, post_url: str, ignore_globs: list[str], debounce_ms: int):
        self.post_url = post_url
        self.ignore = ignore_globs or []
        self.debounce_ms = debounce_ms
        self._last: dict[str, float] = {}

    def _ignored(self, path: str) -> bool:
        p = path.replace("\\", "/")
        for pat in self.ignore:
            if fnmatch(p, pat) or f"/{pat}/" in p or p.endswith("/" + pat):
                return True
        return False

    def _debounced(self, key: str) -> bool:
        now = time.time() * 1000
        last = self._last.get(key, 0)
        if now - last < self.debounce_ms:
            return True
        self._last[key] = now
        return False

    def _emit(self, kind: str, src: str, dest: str | None = None):
        if self._ignored(src) or (dest and self._ignored(dest)):
            return
        key = f"{kind}:{src}:{dest or ''}"
        if self._debounced(key):
            return
        size = None
        mtime = None
        sha1 = None
        try:
            if os.path.isfile(src):
                st = os.stat(src)
                size = st.st_size
                mtime = int(st.st_mtime)
                if size is not None and size <= 1024 * 1024:
                    h = hashlib.sha1()
                    with open(src, "rb") as f:
                        h.update(f.read())
                    sha1 = h.hexdigest()
        except Exception:
            pass
        meta = {"kind": kind, "path": src, "dest": dest, "size": size, "mtime": mtime, "sha1": sha1}
        try:
            with httpx.Client(timeout=1.5) as c:
                c.post(self.post_url, json={"event": "file.change", "message": kind, "meta": meta})
        except Exception:
            pass

    def on_created(self, e): self._emit("created", e.src_path)
    def on_modified(self, e): self._emit("modified", e.src_path)
    def on_deleted(self, e): self._emit("deleted", e.src_path)
    def on_moved(self, e):    self._emit("moved", e.src_path, getattr(e, "dest_path", None))

class Watcher:
    def __init__(self, paths: list[str], post_url: str, ignore_globs: list[str], debounce_ms: int):
        self.paths = [p for p in (paths or []) if p and os.path.exists(p)]
        self.post_url = post_url
        self.ignore = ignore_globs
        self.debounce_ms = debounce_ms
        self.observer = PollingObserver()
        self.thread: threading.Thread | None = None

    def start(self):
        handler = _Handler(self.post_url, self.ignore, self.debounce_ms)
        for p in self.paths:
            self.observer.schedule(handler, p, recursive=True)
        self.observer.start()
        # keep a thread alive to rethrow exceptions if any
        self.thread = threading.Thread(target=self.observer.join, kwargs={"timeout": None}, daemon=True)
        self.thread.start()

    def stop(self):
        try:
            self.observer.stop()
            self.observer.join(timeout=2.0)
        except Exception:
            pass

def start_file_watcher(paths: list[str], post_url: str, ignore_globs: list[str], debounce_ms: int) -> Watcher | None:
    if not paths:
        return None
    w = Watcher(paths, post_url, ignore_globs, debounce_ms)
    w.start()
    return w
