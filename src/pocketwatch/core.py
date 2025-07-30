from __future__ import annotations

import atexit
import cProfile
import logging
import pstats
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, Type, Literal
from types import TracebackType
from notifypy import Notify


class NotifierProtocol(Protocol):
    def send(self, title: str, message: str, sound_path: str | None = None) -> None:
        ...




def _default_notifier() -> NotifierProtocol:

    class _Notifier:
        def send(self, title: str, message: str, sound_path: str | None = None) -> None:
            n = Notify()
            n.title = title
            n.message = message
            if sound_path:
                n.audio = str(sound_path)
            n.send()

    return _Notifier()


def _find_data_file(name: str) -> Path:
    return Path(__file__).with_name("data").joinpath(name)


@dataclass
class _Mark:
    note: str
    elapsed: float


class Pocketwatch:
    def __init__(self,
                 msg: str | None = None,
                 *,
                 notify: bool = True,
                 notify_after: float = 0.0,
                 notifier: NotifierProtocol | None = None,
                 sound: bool = False,
                 sound_after: float = 60.0,
                 sound_file: str | Path | None = None,
                 incremental: bool = False,
                 increment_cutoff: float = 0.5,
                 profile: bool = False,
                 profile_output_path: str | Path | None = None,
                 log_mode: str = "both",
                 logger: logging.Logger | None = None,
                 log_level: int = logging.INFO,
                 _disable_atexit: bool = False) -> None:
        self.msg = msg or "block"
        self.notify = notify
        self.notify_after = notify_after
        self.sound = sound
        self.sound_after = sound_after
        self.sound_file = (
            Path(sound_file) if sound_file else _find_data_file("ding.wav")
        )
        self.notifier = (
            notifier if notifier is not None else _default_notifier()
        )
        self.incremental = incremental
        self.increment_cutoff = increment_cutoff
        self.profile = profile
        self.profile_output_path = (
            Path(profile_output_path) if profile_output_path else None
        )
        self.log_mode = log_mode
        self.logger = logger or logging.getLogger("Pocketwatch")
        self.log_level = log_level
        self._disable_atexit = _disable_atexit

        self._start = time.perf_counter()
        self._ended = False
        self._marks: list[_Mark] = []
        self._prof: Optional[cProfile.Profile] = None
        self.unexpected_exit = False

        if self.profile:
            self._prof = cProfile.Profile()
            self._prof.enable()

        if not self._disable_atexit:
            atexit.register(self._atexit_stop)

    # ------------------------------------------------------------------
    def _now(self) -> float:
        return time.perf_counter()

    # ------------------------------------------------------------------
    @property
    def elapsed(self) -> float:
        return self._now() - self._start

    # ------------------------------------------------------------------
    def mark(self, note: str) -> None:
        el = self.elapsed
        self._marks.append(_Mark(note=note, elapsed=el))
        if self.incremental and el < self.increment_cutoff:
            return
        self._log(f"{note} at {el:.3f}s")

    # ------------------------------------------------------------------
    def end(self, *, return_stats: bool = False) -> Optional[pstats.Stats]:
        if self._ended:
            return self._stats() if return_stats else None
        self._ended = True
        elapsed = self.elapsed
        if self._prof:
            self._prof.disable()
        if self.profile and self.profile_output_path:
            self._prof.dump_stats(self.profile_output_path)  # type: ignore

        if self.unexpected_exit:
            msg = (
                f"[Pocketwatch] {self.msg} interrupted by interpreter shutdown"
                f" after {elapsed:.3f}s"
            )
        else:
            msg = f"[Pocketwatch] {self.msg} completed in {elapsed:.3f}s"
        self._log(msg)

        if self.profile and return_stats:
            return pstats.Stats(self._prof) if self._prof else None
        if self.notifier:
            notify_ok = (
                self.notify
                and elapsed >= self.notify_after
                and not (self.incremental and elapsed < self.increment_cutoff)
            )
            sound_ok = (
                self.sound
                and elapsed >= self.sound_after
                and not (self.incremental and elapsed < self.increment_cutoff)
            )
            if notify_ok or sound_ok:
                self.notifier.send(
                    "Pocketwatch",
                    msg if notify_ok else "",
                    str(self.sound_file) if sound_ok else None,
                )
        return self._stats() if return_stats else None

    # ------------------------------------------------------------------
    def _stats(self) -> Optional[pstats.Stats]:
        if self.profile and self._prof:
            return pstats.Stats(self._prof)
        return None

    # ------------------------------------------------------------------
    def _log(self, message: str) -> None:
        if self.log_mode in {"log", "both", "custom"}:
            self.logger.log(self.log_level, message)
        if self.log_mode in {"print", "both"}:
            print(message)

    # ------------------------------------------------------------------
    def _atexit_stop(self) -> None:
        if not self._ended:
            self.unexpected_exit = True
            self.end()

    # ------------------------------------------------------------------
    def __enter__(self) -> "Pocketwatch":
        return self

    # ------------------------------------------------------------------
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Literal[False]:
        self.end()
        return False