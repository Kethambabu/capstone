import os, time
from datetime import datetime

_RESET   = "\033[0m"
_BOLD    = "\033[1m"
_GREEN   = "\033[92m"
_YELLOW  = "\033[93m"
_BLUE    = "\033[94m"
_MAGENTA = "\033[95m"
_CYAN    = "\033[96m"
_RED     = "\033[91m"
_WHITE   = "\033[97m"
_DIM     = "\033[2m"

def _trace_enabled():
    val = os.environ.get("DEBUG_EXECUTION_TRACE", "True").strip().lower()
    return val in ("1", "true", "yes", "on")

class TraceLogger:
    def _p(self, text):
        try:
            print(text, flush=True)
        except Exception:
            pass

    def _div(self, char="=", width=62, color=_MAGENTA):
        return f"{color}{char * width}{_RESET}"

    def _thin(self, char="-", width=50, color=_DIM):
        return f"{color}{char * width}{_RESET}"

    def _lbl(self, text):
        return f"{_BOLD}{_CYAN}{text}{_RESET}"

    def begin(self, query, role="Executive", session_id="", dataset_name="", mode="quota_saver", conversation_id=""):
        self._start_time = time.time()
        if not _trace_enabled():
            return self._start_time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._p("")
        self._p(self._div())
        self._p(f"{_BOLD}{_CYAN}  BOARDROOM AI - EXECUTION TRACE{_RESET}")
        self._p(f"{_DIM}  {now}{_RESET}")
        self._p(self._div())
        self._p(f"  {self._lbl('Query      :')} {_WHITE}{query}{_RESET}")
        self._p(f"  {self._lbl('Role       :')} {_WHITE}{role}{_RESET}")
        self._p(f"  {self._lbl('Session    :')} {_DIM}{session_id}{_RESET}")
        self._p(f"  {self._lbl('Dataset    :')} {_DIM}{dataset_name}{_RESET}")
        self._p(f"  {self._lbl('Mode       :')} {_DIM}{mode}{_RESET}")
        if conversation_id:
            self._p(f"  {self._lbl('Conv ID    :')} {_DIM}{conversation_id}{_RESET}")
        self._p(self._div())
        self._p("")
        return self._start_time

    def step_ok(self, step, title, details=None, elapsed=None):
        if not _trace_enabled():
            return
        suffix = f" {_DIM}[{elapsed:.2f}s]{_RESET}" if elapsed is not None else ""
        self._p(f"{_BOLD}{_BLUE}[{step:02d}]{_RESET} {_GREEN}OK{_RESET}  {_BOLD}{_WHITE}{title}{_RESET}{suffix}")
        if details:
            for k, v in details.items():
                self._p(f"     {_CYAN}{k:<14}{_RESET} {_WHITE}{v}{_RESET}")
        self._p("")

    def step_fail(self, step, title, reason="", message=""):
        self._p(f"{_BOLD}{_BLUE}[{step:02d}]{_RESET} {_RED}FAIL{_RESET}  {_BOLD}{_RED}{title}{_RESET}")
        if reason:
            self._p(f"     {_RED}Reason  : {reason}{_RESET}")
        if message:
            self._p(f"     {_RED}Message : {message}{_RESET}")
        self._p("")

    def step_info(self, step, title, details=None):
        if not _trace_enabled():
            return
        self._p(f"{_BOLD}{_BLUE}[{step:02d}]{_RESET} {_BLUE}INFO{_RESET}  {_BOLD}{_WHITE}{title}{_RESET}")
        if details:
            for k, v in details.items():
                self._p(f"     {_CYAN}{k:<14}{_RESET} {_WHITE}{v}{_RESET}")
        self._p("")

    def step_running(self, step, title):
        t = time.time()
        if not _trace_enabled():
            return t
        self._p(f"{_BOLD}{_BLUE}[{step:02d}]{_RESET} {_YELLOW}...{_RESET}  {_BOLD}{_WHITE}{title}{_RESET}")
        return t

    def security_checks(self, checks):
        if not _trace_enabled():
            return
        for name, passed, detail in checks:
            icon  = f"{_GREEN}+{_RESET}" if passed else f"{_RED}X{_RESET}"
            color = _GREEN if passed else _RED
            dtext = f"  {_DIM}{detail}{_RESET}" if detail else ""
            self._p(f"     {icon}  {color}{name:<30}{_RESET}{dtext}")
        self._p("")

    def agent_selection(self, selections):
        if not _trace_enabled():
            return
        sep = self._thin("-", 45)
        for name, selected, reason in selections:
            tag   = "Selected" if selected else "Bypassed"
            color = _GREEN if selected else _RED
            self._p(f"     {_BOLD}{_WHITE}{name:<22}{_RESET}  {color}{tag}{_RESET}")
            self._p(f"     {_DIM}Reason: {reason}{_RESET}")
            self._p(f"     {sep}")
        self._p("")

    def skills_loaded(self, agent, skills):
        if not _trace_enabled():
            return
        self._p(f"     {_BOLD}{_WHITE}{agent}{_RESET}")
        self._p(f"     {_DIM}Loading Skills...{_RESET}")
        for s in skills:
            self._p(f"       {_GREEN}OK{_RESET}  {_WHITE}{s}{_RESET}")
        self._p(f"     {_DIM}Completed{_RESET}")
        self._p("")

    def datasets_loaded(self, loaded, skipped):
        if not _trace_enabled():
            return
        self._p(f"     {_BOLD}{_WHITE}Datasets{_RESET}")
        for ds in loaded:
            self._p(f"       {_GREEN}+{_RESET}  {_WHITE}{ds}{_RESET}")
        for ds in skipped:
            self._p(f"       {_RED}-{_RESET}  {_DIM}{ds}  (Skipped){_RESET}")
        self._p("")

    def context_built(self, layers):
        if not _trace_enabled():
            return
        self._p(f"     {_DIM}Building Context...{_RESET}")
        for name, status in layers:
            self._p(f"       {_GREEN}OK{_RESET}  {_WHITE}{name:<22}{_RESET}  {_DIM}{status}{_RESET}")
        self._p(f"     {_DIM}Completed{_RESET}")
        self._p("")

    def agent_work(self, agent, steps, elapsed=None):
        if not _trace_enabled():
            return
        self._p(f"     {self._thin('-', 48)}")
        self._p(f"     {_BOLD}{_WHITE}{agent}{_RESET}")
        for s in steps:
            self._p(f"       >> {_WHITE}{s}{_RESET}  {_GREEN}OK{_RESET}")
        suffix = f"  {_DIM}[{elapsed:.2f}s]{_RESET}" if elapsed is not None else ""
        self._p(f"       {_GREEN}Completed{_RESET}{suffix}")
        self._p("")

    def agent_error(self, agent, error, fallback=""):
        if not _trace_enabled():
            return
        self._p(f"     {_BOLD}{_RED}{agent}{_RESET}")
        self._p(f"       {_RED}ERROR: {error}{_RESET}")
        if fallback:
            self._p(f"       {_YELLOW}Fallback: {fallback}{_RESET}")
        self._p("")

    def agent_collab(self, messages):
        if not _trace_enabled():
            return
        for i, (agent, msg) in enumerate(messages):
            self._p(f"     {_BOLD}{_CYAN}{agent}{_RESET}")
            self._p(f"       {_WHITE}{msg}{_RESET}")
            if i < len(messages) - 1:
                self._p(f"                   {_CYAN}|{_RESET}")
                self._p(f"                   {_CYAN}v{_RESET}")
        self._p("")

    def report_sections(self, sections, model="", elapsed=None):
        if not _trace_enabled():
            return
        self._p(f"     {_DIM}Generating Executive Report...{_RESET}")
        for s in sections:
            self._p(f"       {_GREEN}OK{_RESET}  {_WHITE}{s}{_RESET}")
        if model:
            self._p(f"       {_DIM}Model: {model}{_RESET}")
        suffix = f"  {_DIM}[{elapsed:.2f}s]{_RESET}" if elapsed is not None else ""
        self._p(f"       {_GREEN}Completed{_RESET}{suffix}")
        self._p("")

    def evaluation_result(self, accuracy, completeness, consistency, hallucination_risk, confidence):
        if not _trace_enabled():
            return
        def sc(v): return _GREEN if v >= 90 else (_YELLOW if v >= 70 else _RED)
        def rc(v): return _GREEN if v <= 10 else (_YELLOW if v <= 30 else _RED)
        self._p(f"     {_CYAN}{'Accuracy':<26}{_RESET}  {sc(accuracy)}{accuracy}/100{_RESET}")
        self._p(f"     {_CYAN}{'Completeness':<26}{_RESET}  {sc(completeness)}{completeness}/100{_RESET}")
        self._p(f"     {_CYAN}{'Consistency':<26}{_RESET}  {sc(consistency)}{consistency}/100{_RESET}")
        self._p(f"     {_CYAN}{'Hallucination Risk':<26}{_RESET}  {rc(hallucination_risk)}{hallucination_risk}/100{_RESET}")
        self._p(f"     {_BOLD}{_WHITE}{'Confidence Score':<26}{_RESET}  {sc(confidence)}{confidence}%{_RESET}")
        passed = confidence >= 80
        rc2 = _GREEN if passed else _RED
        self._p(f"     {_DIM}Result     :{_RESET}  {rc2}{'PASSED' if passed else 'BELOW THRESHOLD'}{_RESET}")
        self._p("")

    def response_sent(self, tokens_approx, elapsed, status="SUCCESS"):
        if not _trace_enabled():
            return
        color = _GREEN if status == "SUCCESS" else _RED
        self._p(f"     {_CYAN}{'Tokens Used':<22}{_RESET}  {_WHITE}~{tokens_approx:,}{_RESET}")
        self._p(f"     {_CYAN}{'Processing Time':<22}{_RESET}  {_WHITE}{elapsed:.2f}s{_RESET}")
        self._p(f"     {_BOLD}{_WHITE}{'Status':<22}{_RESET}  {color}{status}{_RESET}")
        self._p("")

    def end(self, success, intent="", agents_run=None, agents_skipped=None, datasets_used=None, skill_loaded="", elapsed=None):
        if not _trace_enabled():
            return
        total = elapsed if elapsed is not None else (time.time() - getattr(self, "_start_time", time.time()))
        status_text = f"{_GREEN}SUCCESS{_RESET}" if success else f"{_RED}FAILED{_RESET}"
        self._p(self._div())
        self._p(f"{_BOLD}{_MAGENTA}  EXECUTION SUMMARY{_RESET}")
        self._p(self._div())
        if intent:
            self._p(f"  {self._lbl('Intent       ')}  {_WHITE}{intent}{_RESET}")
        if agents_run:
            self._p(f"  {self._lbl('Agents Run   ')}  {_GREEN}{', '.join(agents_run)}{_RESET}")
        if agents_skipped:
            self._p(f"  {self._lbl('Agents Skip  ')}  {_DIM}{', '.join(agents_skipped)}{_RESET}")
        if datasets_used:
            self._p(f"  {self._lbl('Datasets     ')}  {_WHITE}{', '.join(datasets_used)}{_RESET}")
        if skill_loaded:
            self._p(f"  {self._lbl('Skill        ')}  {_WHITE}{skill_loaded}{_RESET}")
        self._p(f"  {self._lbl('Exec Time    ')}  {_WHITE}{total:.2f}s{_RESET}")
        self._p(f"  {self._lbl('Status       ')}  {status_text}")
        self._p(self._div())
        self._p("")

    @staticmethod
    def warn(message):
        try:
            print(f"{_YELLOW}[TRACE WARN] {message}{_RESET}", flush=True)
        except Exception:
            pass

    @staticmethod
    def error(message):
        try:
            print(f"{_RED}[TRACE ERROR] {message}{_RESET}", flush=True)
        except Exception:
            pass

trace = TraceLogger()
