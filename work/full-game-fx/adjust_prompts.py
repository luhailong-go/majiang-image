from pathlib import Path
R=Path(r'D:\work\majiang-image')
for s in ['player-ring','hu-burst','victory-confetti','reward-stars']:
 p=R/f'prompts/full-game/fx/{s}.txt';t=p.read_text(encoding='utf-8')
 t=t.replace('at least 15% transparent margin','at least 25% transparent margin').replace('central70%','central50%').replace('65%','50%').replace('52%','40%')
 t+=' IMPORTANT: each effect must be small within its cell, at most HALF the cell width and HALF the cell height; do not expand effects to fill the quadrant. Keep a WIDE empty transparent cross-shaped gutter between all4cells. For the2x2square atlas the4centers are at25%/25%,75%/25%,25%/75%,75%/75% of whole canvas. All effects stop well before the quadrant boundary.'
 p.write_text(t,encoding='utf-8')
