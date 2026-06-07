<h1>ASERT-Tracker</h1>
ASERT Tracker is a specialized tool/monitoring script used by blockchain node operators to track and analyze the network's Difficulty Adjustment Algorithm.<br>
<h3>The Solo Miner’s ASERT Operational Matrix</h3>
<b>STABLE NETWORK (Green)</b>

<b>The Blueprint:</b> Recent block averages are holding steady between <b>9.5 and 10.5 minutes</b> (570s−630s). The network hashrate is perfectly balanced with the current target difficulty.

<b>The Action:</b> Keep your regular baseline local rigs humming along smoothly. Do not purchase any extra rental power or spin up extra hardware; market efficiency is at a baseline equilibrium.

<b>DIFFICULTY SPIKING (Cyan)</b>

<b>The Blueprint:</b> Whales or massive multi-chain mining pools have flooded the network, causing block times to plummet to <b>less than 7.5 minutes</b> (<450s). The ASERT algorithm responds by scaling difficulty upward exponentially.

<b>The Action: HOLD.</b> Do not route rented hashpower or activate backup hardware here. Mining into a rising difficulty curve compresses your margins—let the automated pools trigger the network's difficulty defense mechanism while you save your capital.

<b>DIFFICULTY EASING (Yellow)</b>

<b>The Blueprint:</b> The block pace has slowed down, stretching averages out past <b>10.5 minutes</b> (>630s). The large pools have rotated their hashpower elsewhere, and the ASERT engine is initiating a downward slide on the network's difficulty.

<b>The Action: MONITOR CLOSELY.</b> Open up your rig dashboards, check your pool connection sheets, and prep your market order forms. The network is entering a prime window for a solo mining strike.

<b>STRIKE NOW / READY (Red / Blinking Green)</b>

<b>The Blueprint:</b> The last 4 blocks have an average block time exceeding <b>12.5 minutes</b> (750s+ ). ASERT is dramatically melting the difficulty threshold down. Your terminal's live clock on the current block is ticking high into deep green margins.

<b>The Action: ACTIVATE ALL AUXILIARY HARDWARE.</b> Because you are a solo miner, the suppressed difficulty significantly amplifies your payout probability per Terahash compared to normal network baselines. Immediately dump your local backup rigs and your market rental orders into the pool before the block pace aggressively snaps back.

<img width="971" height="762" alt="ASERT-Tracker-Baseline" src="https://github.com/user-attachments/assets/55873494-c63b-4443-af68-b123c39a573e" /><br>

<img width="972" height="766" alt="ASERT-Tracker-Strike" src="https://github.com/user-attachments/assets/10d53d7c-a259-4606-8aea-64ca6bfa5d03" /><br>


<h3>File path and cofigurations to change:</h3>
# --- Configuration ---<br>
BCH_BIN_PATH = "/mnt/bch/bin/bitcoin-cli"<br>
BCH_DATA_DIR = "/mnt/bch/data/"<br>         
RPC_PORT = "8349"<br>                    
REFRESH_RATE = 4<br>
VISIBLE_HISTORY_COUNT = 30  
