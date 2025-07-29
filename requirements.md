Pocketwatch — Formal Requirements
Version 0.1 ( “Lock-in” draft, 2025-07-26)

Internal document for project Codex.
Audience: contributors & reviewers.
License: MIT (all bundled artifacts must be MIT / CC-0 compatible).

⸻

1 — Product Vision

A drop-in stopwatch for any Python code block.
Creating a Pocketwatch instance starts a high-resolution timer; stopping it logs the elapsed time, pops up a desktop notification, optionally plays a chime, and—if requested—dumps a cProfile summary.
It always cleans up: even if the user forgets to stop it or an exception aborts the interpreter.

⸻

2 — Glossary

Term	Meaning
PW	Abbreviation for the Pocketwatch class.
Spellbook	Optional factory module (pocketwatch.spellbook) that returns PW instances pre-tuned to “Time-Mage” presets (haste(), slow(), meteor(), etc.). Hidden Easter-egg; never referenced in public docs.
Notifier	An object exposing send(title, message, sound_path=None). Default backend = notifypy.


⸻

3 — Primary Use-Cases

#	Actor	Scenario
U-1	Data-scientist	Time a Pandas transformation in a notebook; see a log line and pop-up instantly.
U-2	Backend dev	Wrap a CLI script; if it exceeds 60 s the PC dings so they can context-switch.
U-3	Perf tuner	Turn on profile=True to locate hotspots without extra imports.
U-4	CI job	Run benchmarks with notify=False to keep logs clean.
U-5	Ops	Long maintenance task with periodic mark() checkpoints; short phases stay silent.


⸻

4 — Functional Requirements

4.1 Timer Lifecycle
	•	Start at construction (time.perf_counter()).
	•	Stop on end() or context-manager exit.
	•	Auto-stop via atexit if neither called; log … interrupted by interpreter shutdown …, set flag unexpected_exit=True.

4.2 Logging
	•	Modes chosen via log_mode: "print"│"log"│"both"│"custom".
	•	Default logger = logging.getLogger("Pocketwatch"), default level INFO.
	•	Message templates
	•	Normal: "[Pocketwatch] {msg} completed in {elapsed:.3f}s"
	•	Auto-stop: "[Pocketwatch] {msg} interrupted by interpreter shutdown after {elapsed:.3f}s"

4.3 Notifications
	•	Parameter set:

Arg	Default	Behaviour
notify	True	Enable pop-up.
notify_after	0.0 s	Minimum elapsed time before pop-up.
notifier	None	If None, use builtin notifypy backend.


	•	Pop-up fires when notify==True and elapsed ≥ notify_after.
	•	Incremental filter suppresses pop-up when incremental==True & elapsed < increment_cutoff.

4.4 Sound
	•	Parameters: sound: bool = False, sound_after: float = 60.0, sound_file (default = bundled ding.wav).
        •       Sound playback uses notifypy's built-in audio support.
	•	Fires when sound==True and elapsed ≥ sound_after.

4.5 Incremental Mode

Arg	Default	Effect
incremental	False	Enable small-run suppression.
increment_cutoff	0.5 s	Threshold.

If active and elapsed < cut-off, suppress mark() log lines, pop-up, and sound. end() always logs (may still mute pop-up/sound by rules above).

4.6 Profiling
	•	profile=True wraps the block in cProfile.Profile.
	•	end(return_stats=True) returns pstats.Stats.
	•	profile_output_path dumps raw stats if supplied.

4.7 Error Handling
	•	__exit__ stops timer and applies normal notification rules even when an exception is propagating, then re-raises.
	•	Auto-stop must never swallow unrelated exceptions.

⸻

5 — Public API

class Pocketwatch:
    def __init__(self,
                 msg: str | None = None,
                 *,
                 # notifications
                 notify: bool = True,
                 notify_after: float = 0.0,
                 notifier: NotifierProtocol | None = None,
                 # sound
                 sound: bool = False,
                 sound_after: float = 60.0,
                 sound_file: str | Path | None = None,
                 # incremental
                 incremental: bool = False,
                 increment_cutoff: float = 0.5,
                 # profiling
                 profile: bool = False,
                 profile_output_path: str | Path | None = None,
                 # logging
                 log_mode: str = "log",  # print | log | both | custom
                 logger: logging.Logger | None = None,
                 log_level: int = logging.INFO,
                 # internals
                 _disable_atexit: bool = False):
        ...

    def mark(self, note: str) -> None
    def end(self, *, return_stats: bool = False) -> pstats.Stats | None
    @property
    def elapsed(self) -> float

Constructor Defaults (quick table)

Param	Default
notify	True
notify_after	0 s
sound	False
sound_after	60 s
incremental	False
increment_cutoff	0.5 s
profile	False


⸻

6 — Easter-Egg Spellbook (internal, optional)

File pocketwatch/spellbook.py exposes a factory spellbook with methods:

Spell	Tweaks (applied before user kwargs)
haste()	increment_cutoff=0.25, notify_after=0, sound_after=30
slow()	increment_cutoff=1.0, notify_after=60, sound_after=120
stop()	Alias to Pocketwatch; theatrical .stop() method may be used.
meteor()	profile=True, sound=True, sound_after=0, sound_file="meteor.wav"
float()	_disable_atexit=True

meteor.wav (≤ 20 kB) is bundled in pocketwatch/data/.

Spellbook is not documented in README; discoverable via dir(pocketwatch).

⸻

7 — Non-Functional Requirements

Category	Requirement
Python	3.9 +
Dependencies    Hard: stdlib and notifypy.
Wheel size	< 50 kB including WAVs
Perf	Start + stop overhead ≤ 0.05 ms on 2 GHz CPU (no profiling).
Platforms	Win / macOS / Linux; degrade silently if D-Bus, etc., absent.
License	MIT. Bundled audio must be CC-0 or MIT.
Testing	Pytest ≥ 90 % cov; mock time & fake notifier.
CI	GitHub Actions: ruff, mypy, pytest on 3.9-3.12 (with [notify,sound] extras).


⸻

8 — Packaging & Layout

pocketwatch/
├── __init__.py        (exports Pocketwatch, lazy spellbook import)
├── core.py            (PW implementation)
├── spellbook.py       (optional factory)
├── data/
│   ├── ding.wav
│   └── meteor.wav
└── tests/
    └── ...

MANIFEST.in

recursive-include pocketwatch/data *.wav

pyproject.toml excerpt

[project]
dependencies = ["notifypy>=1.4"]



⸻

9 — Roadmap Milestones
	1.	0.0.0 stub → Test PyPI (name reservation).
	2.	0.1.0 — core timer, log-modes, notify, sound, profiling.
	3.	0.1.x — polish; Spellbook merged.
	4.	1.0.0 — stable API, first outside feedback cycle closed.

⸻

End of requirements.
