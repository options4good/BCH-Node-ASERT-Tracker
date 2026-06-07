import os
import subprocess
import json
import time
import threading
from datetime import datetime
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table

# --- Configuration ---
APP_VERSION = "V1.2.7"
BCH_BIN_PATH = "/mnt/bch/bin/bitcoin-cli"  
BCH_DATA_DIR = "/mnt/bch/data/"             
RPC_PORT = "8349"                           
REFRESH_RATE = 4  

VISIBLE_HISTORY_COUNT = 30  

class StandaloneAsertTracker:
    def __init__(self):
        self.error_log = ""
        self.lock = threading.Lock()
        
        self.strike_height = None
        self.strike_triggered = False

        self.data = {
            "height": 0,
            "difficulty": "---",
            "avg_block_time": 600.0,
            "status": "INITIALIZING",
            "color": "white",
            "signal": "INITIALIZING",
            "history_rows": [],
            "current_block_time": 0
        }

    def _run_cli(self, cmd_args):
        """Runs the CLI using your node's specific custom port and data directory flags."""
        full_command = [BCH_BIN_PATH, f"-rpcport={RPC_PORT}", f"-datadir={BCH_DATA_DIR}"] + cmd_args
        try:
            result = subprocess.run(
                full_command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.error_log = ""  
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.error_log = f"CLI Error: {e.stderr.strip() or e.output.strip()}"
            return None
        except Exception as e:
            self.error_log = f"System Error: {str(e)}"
            return None

    def format_delta_time(self, seconds, live_clock_mode=False):
        """Formats raw seconds into a clean, human-readable mining duration string."""
        if seconds <= 0:
            return "0s"
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        
        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h {mins}m {secs}s"
        elif mins > 0:
            duration_str += f"{mins}m {secs}s"
        else:
            duration_str += f"{secs}s"
            
        if live_clock_mode:
            return duration_str
        return f"took {duration_str}"

    def update_metrics_loop(self):
        """Background thread loop to fetch node data without lagging the system clock."""
        while True:
            bc_info = self._run_cli(["getblockchaininfo"])
            
            if not bc_info:
                with self.lock:
                    self.data["status"] = "RPC CONNECTION FAILURE"
                    self.data["color"] = "red"
                    self.data["signal"] = f"CHECK NODE ( {self.error_log or 'Check port ' + RPC_PORT} )"
                time.sleep(5)
                continue

            current_height = bc_info.get("blocks", 0)
            raw_diff = bc_info.get("difficulty", 0)
            
            if raw_diff >= 1e12:
                formatted_diff = f"{raw_diff/1e12:.2f} T"
            elif raw_diff >= 1e9:
                formatted_diff = f"{raw_diff/1e9:.2f} G"
            else:
                formatted_diff = f"{raw_diff:.2f}"

            avg_time = 600.0
            history_rows = []
            current_block_time = 0
            
            try:
                pull_count = VISIBLE_HISTORY_COUNT + 2
                timestamps_dict = {}
                for h in range(current_height, current_height - pull_count, -1):
                    b_header = self._run_cli(["getblockheader", str(h)])
                    if b_header and "time" in b_header:
                        timestamps_dict[h] = b_header.get("time")

                if current_height in timestamps_dict:
                    current_block_time = timestamps_dict[current_height]

                asert_ts = [timestamps_dict[h] for h in range(current_height, current_height - 5, -1) if h in timestamps_dict]
                if len(asert_ts) == 5:
                    deltas = [asert_ts[i] - asert_ts[i+1] for i in range(len(asert_ts)-1)]
                    avg_time = sum(deltas) / len(deltas)

                for h in range(current_height, current_height - VISIBLE_HISTORY_COUNT, -1):
                    if h in timestamps_dict and (h - 1) in timestamps_dict:
                        elapsed = timestamps_dict[h] - timestamps_dict[h - 1]
                        readable_time = self.format_delta_time(elapsed, live_clock_mode=False)
                        history_rows.append({"height": h, "duration": readable_time})
            except:
                avg_time = 600.0
                history_rows = []

            # Evaluate strategy states
            if avg_time > 750:
                status = "DIFFICULTY DROPPING"
                color = "bright_red"
                if self.strike_height is None:
                    self.strike_height = current_height
                    self.strike_triggered = False
                    signal = f"READY - WAIT FOR BLOCK #{self.strike_height} TO CLEAR"
                elif current_height > self.strike_height:
                    self.strike_triggered = True
                    signal = f"STRIKE NOW! - INITIALIZE RIGS (BLOCK #{current_height} IS LIVE)"
                else:
                    signal = f"READY - WAIT FOR BLOCK #{self.strike_height} TO CLEAR"
            elif avg_time > 630:
                status = "DIFFICULTY EASING"
                color = "yellow"
                signal = "MONITOR CLOSELY - PREPARE ORDERS"
                self.strike_height = None
                self.strike_triggered = False
            elif avg_time < 450:
                status = "DIFFICULTY SPIKING"
                color = "cyan"
                signal = "HOLD - DO NOT RENT"
                self.strike_height = None
                self.strike_triggered = False
            else:
                status = "STABLE NETWORK"
                color = "green"
                signal = "HOLD - BASELINE OPERATION"
                self.strike_height = None
                self.strike_triggered = False

            with self.lock:
                self.data = {
                    "height": current_height,
                    "difficulty": formatted_diff,
                    "avg_block_time": avg_time,
                    "status": status,
                    "color": color,
                    "signal": signal,
                    "history_rows": history_rows,
                    "current_block_time": current_block_time
                }
            
            time.sleep(3)

    def generate_dashboard(self) -> Layout:
        layout = Layout()
        
        layout.split_column(
            Layout(name="header_strip", size=3),
            Layout(name="metrics", size=4),
            Layout(name="signal_box", size=4),
            Layout(name="history_box"), 
            Layout(name="footer_strip", size=3)  
        )

        # 1. Header Block
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_text = Text(f"ASERT Tracker | {APP_VERSION} | {current_time_str}", justify="center", style="bold bright_white")
        layout["header_strip"].update(Panel(header_text, border_style="bright_blue"))

        with self.lock:
            snapshot = self.data.copy()

        # 2. Metrics Block
        top_grid = Table.grid(expand=True)
        top_grid.add_column(ratio=1)
        top_grid.add_column(ratio=1)
        
        net_info = (f"[bold white]Current Block Height:[/] [yellow]{snapshot['height']}[/]\n"
                    f"[bold white]Network Difficulty:[/]   [magenta]{snapshot['difficulty']}[/]")
        
        asert_math = (f"[bold white]ASERT Trend Status:[/]  [{snapshot['color']}]{snapshot['status']}[/]\n"
                      f"[bold white]Recent Avg Pace:[/]     [bold]{snapshot['avg_block_time']:.1f}s[/] (Ideal: 600.0s)")
        
        top_grid.add_row(
            Panel(net_info, title="[bold cyan]Blockchain Summary[/]", border_style="cyan"),
            Panel(asert_math, title="[bold magenta]ASERT Calculations[/]", border_style="magenta")
        )
        layout["metrics"].update(top_grid)

        # 3. Action Center Block
        border_color = snapshot['color']
        text_style = f"bold {snapshot['color']}"
        
        if "STRIKE NOW!" in snapshot['signal']:
            border_color = "bright_green"
            text_style = "bold blink bright_green"

        signal_content = f"[bold white]ACTION REQUIRED:[/] [{text_style}]{snapshot['signal']}[/]"
        layout["signal_box"].update(
            Panel(signal_content, title="[bold bright_white]Action Center[/]", border_style=border_color)
        )

        # 4. History Block
        history_table = Table(show_header=True, header_style="bold bright_white", border_style="bright_black", expand=True)
        history_table.add_column("Block Height | Completion Duration", justify="left", ratio=1)
        history_table.add_column("Block Height | Completion Duration", justify="left", ratio=1)

        if snapshot["current_block_time"] > 0:
            time_delta = int(time.time() - snapshot["current_block_time"])
            if time_delta < 0:
                time_delta = 0
        else:
            time_delta = 0
            
        live_clock_str = self.format_delta_time(time_delta, live_clock_mode=True)
        
        active_block_height = snapshot["height"] + 1
        active_block_cell = f"[bright_cyan]Block #{active_block_height}[/] [cyan]{live_clock_str}[/]"

        raw_rows = snapshot["history_rows"]
        
        for i in range(15):
            left_cell = ""
            right_cell = ""

            # LEFT COLUMN: Newest Blocks (Row 0 is the live counter)
            if i == 0:
                left_cell = active_block_cell
            elif (i - 1) < len(raw_rows):
                l_data = raw_rows[i - 1]
                left_cell = f"[bright_yellow]Block #{l_data['height']}[/] [dim white]{l_data['duration']}[/]"

            # RIGHT COLUMN: Older Blocks
            right_index = i + 14
            if right_index < len(raw_rows):
                r_data = raw_rows[right_index]
                right_cell = f"[bright_yellow]Block #{r_data['height']}[/] [dim white]{r_data['duration']}[/]"

            history_table.add_row(left_cell, right_cell)

        layout["history_box"].update(
            # REVISED: Border changed to green for an elegant distinct finish
            Panel(history_table, title="[bold bright_white]Recent Block History[/]", border_style="green")
        )

        # 5. Footer Block
        footer_text = Text("Press Ctrl+C to Exit", justify="center", style="dim bright_white")
        layout["footer_strip"].update(Panel(footer_text, border_style="bright_black"))
        
        return layout

def main():
    tracker = StandaloneAsertTracker()
    
    data_thread = threading.Thread(target=tracker.update_metrics_loop, daemon=True)
    data_thread.start()
    
    with Live(tracker.generate_dashboard(), screen=True, refresh_per_second=4) as live:
        try:
            while True:
                live.update(tracker.generate_dashboard())
                time.sleep(0.25)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
