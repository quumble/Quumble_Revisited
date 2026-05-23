import csv
from collections import defaultdict
base="/home/claude/Quumble_Revisited-main/quumble_revisited_1/"
FEATS=["round_body","soft_texture","lavender_purple","six_legs","humming_vocal",
 "bioluminescence","large_eyes","spiral_tail","object_collecting","mood_color",
 "waddle_gait","shy_gentle","curious","name_from_sound"]
LOW={"shy_gentle","curious","name_from_sound"}

key={r["blind_id"]:r for r in csv.DictReader(open(base+"blinded_coding_KEY.csv"))}
human={r["blind_id"]:r for r in csv.DictReader(open("human_codes.csv"))}
# deterministic matrix is keyed by (dataset, trial)
det={}
for r in csv.DictReader(open(base+"feature_matrix_deterministic.csv")):
    det[(r["dataset"], r["trial"])]=r

# map blind_id -> deterministic row via key
pairs=[]  # (feat, human, script)
missing=0
for bid,k in key.items():
    drow=det.get((k["dataset"], k["original_trial"]))
    if drow is None:
        missing+=1; continue
    h=human[bid]
    for f in FEATS:
        pairs.append((f,int(h[f]),int(drow[f])))
print("unmatched key rows (no det trial):", missing)

def kappa(rows):
    n=len(rows); 
    if n==0: return None
    agree=sum(1 for _,a,b in rows if a==b)/n
    pa=agree
    # marginal probs
    a1=sum(a for _,a,_ in rows)/n; b1=sum(b for _,_,b in rows)/n
    pe=a1*b1+(1-a1)*(1-b1)
    return agree, (pa-pe)/(1-pe) if pe!=1 else 1.0

ov=kappa(pairs)
print(f"\nWHOLE-CORPUS human-vs-script: cells={len(pairs)}  agreement={ov[0]*100:.1f}%  kappa={ov[1]:.3f}")
hi=[p for p in pairs if p[0] not in LOW]; lo=[p for p in pairs if p[0] in LOW]
print(f"  high-conf only: agreement={kappa(hi)[0]*100:.1f}%  kappa={kappa(hi)[1]:.3f}  (n={len(hi)})")
print(f"  low-conf only : agreement={kappa(lo)[0]*100:.1f}%  kappa={kappa(lo)[1]:.3f}  (n={len(lo)})")

print("\nPer-feature (agreement / human_total / script_total):")
print(f"{'feature':18}{'agree%':>8}{'kappa':>8}{'human':>7}{'script':>7}{'delta':>7}")
for f in FEATS:
    fr=[p for p in pairs if p[0]==f]
    a,kp=kappa(fr)
    ht=sum(h for _,h,_ in fr); st=sum(s for _,_,s in fr)
    tag=" *LOW" if f in LOW else ""
    print(f"{f:18}{a*100:7.1f}{kp:8.2f}{ht:7d}{st:7d}{ht-st:+7d}{tag}")
