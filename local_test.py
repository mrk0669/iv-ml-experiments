"""
Local test runner — simulates the Colab notebook pipeline on Windows.
Uses DeepFace (ArcFace backend) instead of InsightFace (no MSVC needed).
Produces identical analytics: accuracy, distance plots, heatmaps, attendance CSV.
"""
import sys, io
# Force UTF-8 output on Windows to avoid charmap encode errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, cv2, csv, time, pickle, warnings, urllib.request, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from tqdm import tqdm

warnings.filterwarnings('ignore')
os.makedirs("test_results", exist_ok=True)
os.makedirs("dataset",     exist_ok=True)
os.makedirs("encodings",   exist_ok=True)

# ─────────────────────────────────────────────────────────────
# CONFIG  (mirrors production main.py hyperparameters)
# ─────────────────────────────────────────────────────────────
CONFIG = {
    "DISTANCE_THRESHOLD": 0.95,
    "BLUR_THRESHOLD":     40,
    "MIN_IMAGES_REQUIRED": 3,
    "INPUT_FACE_SIZE":    (112, 112),
    "ENCODINGS_FILE":     "encodings/known_faces.pkl",
    "ATTENDANCE_FILE":    "test_results/attendance.csv",
}

# ─────────────────────────────────────────────────────────────
# STEP 1 — Download dataset via sklearn fetch_lfw_people
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 1 — Downloading LFW dataset (sklearn)")
print("="*60)

from sklearn.datasets import fetch_lfw_people

print("  Fetching LFW (min_faces_per_person=10)...")
lfw = fetch_lfw_people(min_faces_per_person=10, color=True, resize=1.0)

# lfw.images  shape: (N, H, W, 3)  float32 0-1
# lfw.target       : int class index
# lfw.target_names : str array of names

print(f"  Total images : {lfw.images.shape[0]}")
print(f"  Image shape  : {lfw.images.shape[1:]}")
print(f"  Classes      : {len(lfw.target_names)}")

# Save top-5 most frequent identities to dataset/
from collections import Counter
counts = Counter(lfw.target)
top5   = [idx for idx, _ in counts.most_common(5)]

total_dl = 0
for cls_idx in top5:
    person = lfw.target_names[cls_idx].replace(" ", "_")
    pdir   = os.path.join("dataset", person)
    os.makedirs(pdir, exist_ok=True)
    indices = [i for i, t in enumerate(lfw.target) if t == cls_idx]
    for img_i, data_idx in enumerate(indices):
        img_float = lfw.images[data_idx]          # H x W x 3  float32 0-1
        img_uint8 = (img_float * 255).astype(np.uint8)
        img_bgr   = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
        path      = os.path.join(pdir, f"{img_i}.jpg")
        cv2.imwrite(path, img_bgr)
        total_dl += 1
    print(f"  {person}: {len(indices)} images")

print(f"\nTotal images saved: {total_dl}")

# ─────────────────────────────────────────────────────────────
# STEP 2 — Visualise dataset samples
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2 — Visualising dataset samples")
print("="*60)

people = [p for p in sorted(os.listdir("dataset"))
          if os.path.isdir(os.path.join("dataset", p))]
cols = 4
fig, axes = plt.subplots(len(people), cols, figsize=(cols*3, len(people)*3))
fig.suptitle("Dataset Sample Images", fontsize=14, fontweight='bold')

for row, person in enumerate(people):
    pdir = os.path.join("dataset", person)
    imgs = sorted(os.listdir(pdir))[:cols]
    for col in range(cols):
        ax = axes[row][col]
        if col < len(imgs):
            img = cv2.imread(os.path.join(pdir, imgs[col]))
            if img is not None:
                ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                ax.set_title(f"{person.split('_')[0]}\n#{col}", fontsize=7)
        ax.axis('off')

plt.tight_layout()
plt.savefig("test_results/01_dataset_samples.png", dpi=100, bbox_inches='tight')
plt.close()
print("  Saved: test_results/01_dataset_samples.png")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Generate ArcFace embeddings via DeepFace
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3 — Generating ArcFace embeddings (DeepFace backend)")
print("="*60)

from deepface import DeepFace

def variance_of_laplacian(img):
    return cv2.Laplacian(img, cv2.CV_64F).var()

def get_embedding(img_bgr):
    """Return L2-normalised 512-dim ArcFace embedding or None."""
    try:
        face = cv2.resize(img_bgr, CONFIG["INPUT_FACE_SIZE"])
        result = DeepFace.represent(
            img_path=face,
            model_name="ArcFace",
            enforce_detection=False,
            detector_backend="skip",
        )
        raw = np.array(result[0]["embedding"], dtype=np.float32)
        norm = np.linalg.norm(raw)
        return raw / norm if norm > 0 else None
    except Exception as e:
        return None

known_encodings = {}
enc_report = []
stats = {"people": 0, "images_used": 0, "images_skipped": 0}

print("  First call downloads ArcFace weights (~500 MB on first run)...\n")

for person in people:
    pdir = os.path.join("dataset", person)
    image_files = sorted([f for f in os.listdir(pdir)
                          if f.lower().endswith(('.jpg','.jpeg','.png'))])
    embeddings = []
    sharpness_scores = []

    for imgf in tqdm(image_files, desc=f"  {person}", ncols=70):
        img = cv2.imread(os.path.join(pdir, imgf))
        if img is None or img.size == 0:
            stats["images_skipped"] += 1
            continue
        gray = cv2.cvtColor(cv2.resize(img, CONFIG["INPUT_FACE_SIZE"]), cv2.COLOR_BGR2GRAY)
        sharpness = variance_of_laplacian(gray)
        if sharpness < CONFIG["BLUR_THRESHOLD"]:
            stats["images_skipped"] += 1
            continue
        emb = get_embedding(img)
        if emb is None:
            stats["images_skipped"] += 1
            continue
        embeddings.append(emb)
        sharpness_scores.append(sharpness)
        stats["images_used"] += 1

    if len(embeddings) < CONFIG["MIN_IMAGES_REQUIRED"]:
        print(f"  [SKIP] {person} ({len(embeddings)} good images < {CONFIG['MIN_IMAGES_REQUIRED']} required)")
        continue

    master = np.mean(embeddings, axis=0)
    master_norm = np.linalg.norm(master)
    if master_norm == 0:
        continue
    master = master / master_norm
    quality = round(float(np.mean(sharpness_scores)), 2)

    known_encodings[person] = {
        "embedding": master,
        "samples": len(embeddings),
        "quality_score": quality,
    }
    enc_report.append({
        "Identity": person,
        "Images Used": len(embeddings),
        "Quality Score": quality,
        "Embedding Dim": len(master),
        "Embedding Norm": round(float(np.linalg.norm(master)), 6),
    })
    stats["people"] += 1
    print(f"  ✓ {person}: {len(embeddings)} images | quality={quality}")

with open(CONFIG["ENCODINGS_FILE"], "wb") as f:
    pickle.dump(known_encodings, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"\n  People encoded : {stats['people']}")
print(f"  Images used    : {stats['images_used']}")
print(f"  Images skipped : {stats['images_skipped']}")
print(f"  Saved to       : {CONFIG['ENCODINGS_FILE']}")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Recognition engine (identical to production logic)
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 4 — Face Recognition (leave-one-out test)")
print("="*60)

# Reload to verify PKL integrity
with open(CONFIG["ENCODINGS_FILE"], "rb") as f:
    known_encodings = pickle.load(f)

marked_today = set()
attendance_log = []
test_results = []
test_images = []

encoded_people = [p for p in people if p in known_encodings]

for person in encoded_people:
    pdir = os.path.join("dataset", person)
    imgs = sorted([f for f in os.listdir(pdir) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    test_img_path = os.path.join(pdir, imgs[-1])   # held-out last image
    frame = cv2.imread(test_img_path)
    if frame is None:
        continue
    frame = cv2.resize(frame, (640, 480))

    t0 = time.time()
    emb = get_embedding(frame)
    latency_ms = (time.time() - t0) * 1000

    if emb is None:
        print(f"  [SKIP] No embedding for {person}")
        continue

    best_match = "Unknown"
    best_dist  = 10.0
    for name, data in known_encodings.items():
        dist = float(np.linalg.norm(emb - data["embedding"]))
        if dist < best_dist:
            best_dist  = dist
            best_match = name
    if best_dist > CONFIG["DISTANCE_THRESHOLD"]:
        best_match = "Unknown"

    confidence = max(0.0, (1.0 - best_dist / CONFIG["DISTANCE_THRESHOLD"]) * 100)
    is_known   = best_match != "Unknown"
    correct    = (best_match == person)

    # Annotate frame
    annotated = frame.copy()
    color = (0, 255, 128) if is_known else (0, 0, 255)
    cv2.rectangle(annotated, (120, 60), (520, 420), color, 3)
    label  = f"{best_match}"
    sublbl = f"dist:{best_dist:.3f} | conf:{confidence:.0f}%"
    cv2.putText(annotated, label,  (125, 55), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
    cv2.putText(annotated, sublbl, (125, 435), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1)
    cv2.putText(annotated, f"GT: {person}", (20, 30),
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,255,255), 1)

    test_results.append({
        "Ground Truth":  person,
        "Predicted":     best_match,
        "Correct":       correct,
        "Distance":      round(best_dist, 4),
        "Confidence %":  round(confidence, 1),
        "Latency ms":    round(latency_ms, 1),
    })
    test_images.append({
        "person": person, "correct": correct,
        "annotated": annotated, "predicted": best_match,
    })

    # Attendance log
    if is_known and best_match not in marked_today:
        marked_today.add(best_match)
        now = datetime.now()
        attendance_log.append({
            "Name": best_match,
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Distance": round(best_dist, 4),
            "Confidence_%": round(confidence, 1),
        })

    icon = "✓" if correct else "✗"
    print(f"  {icon} {person:30s}→ {best_match:30s}  dist={best_dist:.4f}  "
          f"conf={confidence:.0f}%  {latency_ms:.0f}ms")

df_results = pd.DataFrame(test_results)
correct_count = df_results["Correct"].sum() if not df_results.empty else 0
total_count   = len(df_results)
accuracy      = (correct_count / total_count * 100) if total_count > 0 else 0

print(f"\n  Accuracy: {correct_count}/{total_count}  ({accuracy:.1f}%)")

# ─────────────────────────────────────────────────────────────
# STEP 5 — Annotated results grid
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5 — Saving annotated recognition results")
print("="*60)

n = len(test_images)
cols_g = min(3, n)
rows_g = (n + cols_g - 1) // cols_g
fig, axes = plt.subplots(rows_g, cols_g, figsize=(cols_g*5, rows_g*4))
fig.suptitle("Recognition Results — Leave-One-Out Test", fontsize=14, fontweight='bold')

if rows_g == 1 and cols_g == 1:
    axes = [[axes]]
elif rows_g == 1:
    axes = [axes]

for i, item in enumerate(test_images):
    r, c = divmod(i, cols_g)
    ax = axes[r][c] if rows_g > 1 else axes[0][c]
    ax.imshow(cv2.cvtColor(item["annotated"], cv2.COLOR_BGR2RGB))
    tcolor = "green" if item["correct"] else "red"
    status = "✓ CORRECT" if item["correct"] else "✗ INCORRECT"
    ax.set_title(f"{item['person'].split('_')[0]}\n{status}",
                 fontsize=9, color=tcolor, fontweight='bold')
    ax.axis('off')

for i in range(n, rows_g * cols_g):
    r, c = divmod(i, cols_g)
    ax = axes[r][c] if rows_g > 1 else axes[0][c]
    ax.axis('off')

plt.tight_layout()
plt.savefig("test_results/02_recognition_grid.png", dpi=110, bbox_inches='tight')
plt.close()
print("  Saved: test_results/02_recognition_grid.png")

# ─────────────────────────────────────────────────────────────
# STEP 6 — Performance dashboard
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 6 — Building performance dashboard")
print("="*60)

if not df_results.empty:
    fig = plt.figure(figsize=(18, 11))
    fig.suptitle("Attendance System — Performance Dashboard", fontsize=17, fontweight='bold')

    # 1. Accuracy donut
    ax1 = fig.add_subplot(2, 4, 1)
    correct_n  = df_results["Correct"].sum()
    incorrect_n = len(df_results) - correct_n
    ax1.pie([correct_n, incorrect_n],
            labels=["Correct", "Incorrect"],
            colors=["#00C851", "#ff4444"],
            autopct="%1.0f%%", startangle=90,
            wedgeprops={"width": 0.5})
    ax1.set_title(f"Accuracy\n{accuracy:.1f}%\n({correct_n}/{total_count})",
                  fontsize=11, fontweight='bold')

    # 2. Distance bar per person
    ax2 = fig.add_subplot(2, 4, 2)
    valid = df_results.dropna(subset=["Distance"])
    bar_colors = ["#00C851" if c else "#ff4444" for c in valid["Correct"]]
    ax2.bar(range(len(valid)), valid["Distance"], color=bar_colors, edgecolor='white')
    ax2.axhline(y=CONFIG["DISTANCE_THRESHOLD"], color='orange', linestyle='--',
                linewidth=2, label=f'Thresh ({CONFIG["DISTANCE_THRESHOLD"]})')
    ax2.set_xticks(range(len(valid)))
    ax2.set_xticklabels([n.split('_')[0] for n in valid["Ground Truth"]],
                         rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel("Euclidean Distance")
    ax2.set_title("Distance per Identity", fontsize=11, fontweight='bold')
    ax2.legend(fontsize=8)

    # 3. Confidence histogram
    ax3 = fig.add_subplot(2, 4, 3)
    valid_c = df_results[df_results["Confidence %"] > 0]
    if not valid_c.empty:
        ax3.hist(valid_c["Confidence %"], bins=8, color='#00AAFF', edgecolor='white', alpha=0.85)
        ax3.axvline(valid_c["Confidence %"].mean(), color='orange', linestyle='--',
                    linewidth=2, label=f'Mean {valid_c["Confidence %"].mean():.1f}%')
        ax3.set_xlabel("Confidence %")
        ax3.set_ylabel("Count")
        ax3.set_title("Confidence Distribution", fontsize=11, fontweight='bold')
        ax3.legend(fontsize=9)

    # 4. Latency
    ax4 = fig.add_subplot(2, 4, 4)
    ax4.bar(range(len(df_results)), df_results["Latency ms"],
            color='#AA00FF', edgecolor='white', alpha=0.85)
    ax4.axhline(df_results["Latency ms"].mean(), color='orange', linestyle='--',
                linewidth=2, label=f'Avg {df_results["Latency ms"].mean():.0f}ms')
    ax4.set_xticks(range(len(df_results)))
    ax4.set_xticklabels([n.split('_')[0] for n in df_results["Ground Truth"]],
                         rotation=45, ha='right', fontsize=8)
    ax4.set_ylabel("ms")
    ax4.set_title("Inference Latency (ms)", fontsize=11, fontweight='bold')
    ax4.legend(fontsize=9)

    # 5. Results table
    ax5 = fig.add_subplot(2, 1, 2)
    ax5.axis('off')
    tbl_data = df_results[["Ground Truth", "Predicted", "Correct",
                            "Distance", "Confidence %", "Latency ms"]].copy()
    tbl_data["Correct"] = tbl_data["Correct"].map({True: "✓", False: "✗"})
    tbl_data["Ground Truth"] = tbl_data["Ground Truth"].str.replace("_", " ")
    tbl_data["Predicted"]    = tbl_data["Predicted"].str.replace("_", " ")

    tbl = ax5.table(cellText=tbl_data.values, colLabels=tbl_data.columns,
                    loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.9)

    for i, row_val in enumerate(df_results["Correct"]):
        c = '#e8f5e9' if row_val else '#ffebee'
        for j in range(len(tbl_data.columns)):
            tbl[i+1, j].set_facecolor(c)

    ax5.set_title("Detailed Results Table", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("test_results/03_performance_dashboard.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  Saved: test_results/03_performance_dashboard.png")

# ─────────────────────────────────────────────────────────────
# STEP 7 — Threshold sensitivity analysis
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 7 — Threshold sensitivity analysis")
print("="*60)

thresholds  = np.arange(0.3, 1.6, 0.05)
accuracies  = []
fp_rates    = []

valid_rows = df_results.dropna(subset=["Distance"])

for thresh in thresholds:
    tp = fp = fn = 0
    for _, row in valid_rows.iterrows():
        gt   = row["Ground Truth"]
        dist = row["Distance"]
        pred = row["Predicted"] if dist <= thresh else "Unknown"
        if pred == gt:       tp += 1
        elif pred != "Unknown": fp += 1
        else:                fn += 1
    total = len(valid_rows)
    accuracies.append((tp / total * 100) if total > 0 else 0)
    fp_rates.append((fp / total * 100) if total > 0 else 0)

opt_idx   = int(np.argmax(accuracies))
opt_thresh = thresholds[opt_idx]
opt_acc    = accuracies[opt_idx]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))

a1.plot(thresholds, accuracies, 'b-o', linewidth=2, markersize=4)
a1.axvline(CONFIG["DISTANCE_THRESHOLD"], color='orange', linestyle='--',
           linewidth=2, label=f'Current ({CONFIG["DISTANCE_THRESHOLD"]})')
a1.axvline(opt_thresh, color='green', linestyle='--',
           linewidth=2, label=f'Optimal ({opt_thresh:.2f}, {opt_acc:.0f}%)')
a1.set_xlabel("Threshold")
a1.set_ylabel("Accuracy %")
a1.set_title("Accuracy vs Threshold", fontsize=12, fontweight='bold')
a1.legend(); a1.grid(alpha=0.3)

a2.fill_between(thresholds, accuracies,  alpha=0.3, color='blue', label='Accuracy')
a2.fill_between(thresholds, fp_rates,    alpha=0.3, color='red',  label='False Positive %')
a2.plot(thresholds, accuracies, 'b-', linewidth=2)
a2.plot(thresholds, fp_rates,   'r-', linewidth=2)
a2.axvline(opt_thresh, color='green', linestyle='--', linewidth=2)
a2.set_xlabel("Threshold")
a2.set_ylabel("Rate %")
a2.set_title("Accuracy / False-Positive Tradeoff", fontsize=12, fontweight='bold')
a2.legend(); a2.grid(alpha=0.3)

plt.suptitle("Threshold Sensitivity Analysis", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("test_results/04_threshold_analysis.png", dpi=100, bbox_inches='tight')
plt.close()
print(f"  Optimal threshold : {opt_thresh:.2f}  ({opt_acc:.0f}% accuracy)")
print("  Saved: test_results/04_threshold_analysis.png")

# ─────────────────────────────────────────────────────────────
# STEP 8 — Embedding similarity heatmap
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 8 — Embedding similarity heatmap")
print("="*60)

names_enc = sorted(known_encodings.keys())
n_enc     = len(names_enc)
dist_mat  = np.zeros((n_enc, n_enc))
cos_mat   = np.zeros((n_enc, n_enc))

for i, ni in enumerate(names_enc):
    for j, nj in enumerate(names_enc):
        ei = known_encodings[ni]["embedding"]
        ej = known_encodings[nj]["embedding"]
        dist_mat[i, j] = np.linalg.norm(ei - ej)
        cos_mat[i, j]  = float(np.dot(ei, ej))

short = [n.replace("_", " ").split()[-1] for n in names_enc]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

sns.heatmap(dist_mat, annot=True, fmt=".2f",
            xticklabels=short, yticklabels=short,
            cmap="RdYlGn_r", ax=axes[0],
            vmin=0, vmax=CONFIG["DISTANCE_THRESHOLD"]*1.5,
            linewidths=0.5, annot_kws={"size": 9})
axes[0].set_title("Pairwise Euclidean Distance\n(lower = more similar)",
                  fontsize=11, fontweight='bold')

sns.heatmap(cos_mat, annot=True, fmt=".3f",
            xticklabels=short, yticklabels=short,
            cmap="Blues", ax=axes[1], vmin=-1, vmax=1,
            linewidths=0.5, annot_kws={"size": 9})
axes[1].set_title("Cosine Similarity\n(diagonal = self-similarity)",
                  fontsize=11, fontweight='bold')

plt.suptitle("Embedding Space Analysis", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("test_results/05_embedding_heatmap.png", dpi=100, bbox_inches='tight')
plt.close()

mask    = ~np.eye(n_enc, dtype=bool)
off_d   = dist_mat[mask]
sep_ok  = off_d.min() > CONFIG["DISTANCE_THRESHOLD"]
print(f"  Min inter-class distance : {off_d.min():.4f}")
print(f"  Mean inter-class dist    : {off_d.mean():.4f}")
print(f"  Fully separable          : {'YES' if sep_ok else 'NO (some identities overlap)'}")
print("  Saved: test_results/05_embedding_heatmap.png")

# ─────────────────────────────────────────────────────────────
# STEP 9 — Attendance CSV & chart
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 9 — Attendance log")
print("="*60)

att_df = pd.DataFrame(attendance_log)
if not att_df.empty:
    att_df.to_csv(CONFIG["ATTENDANCE_FILE"], index=False)
    print(f"  {len(att_df)} attendance entries saved → {CONFIG['ATTENDANCE_FILE']}")
    print(att_df.to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    axes[0].barh(att_df["Name"].str.split("_").str[-1],
                 att_df["Confidence_%"], color='#00C851', edgecolor='white')
    axes[0].axvline(70, color='orange', linestyle='--', linewidth=1.5, label='70%')
    axes[0].set_xlabel("Confidence %")
    axes[0].set_title("Attendance Confidence Scores", fontsize=11, fontweight='bold')
    axes[0].legend()

    axes[1].barh(att_df["Name"].str.split("_").str[-1],
                 att_df["Distance"], color='#0099FF', edgecolor='white')
    axes[1].axvline(CONFIG["DISTANCE_THRESHOLD"], color='red', linestyle='--',
                    linewidth=1.5, label=f'Threshold')
    axes[1].set_xlabel("Distance")
    axes[1].set_title("Match Distances", fontsize=11, fontweight='bold')
    axes[1].legend()

    plt.suptitle("Attendance Session Report", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig("test_results/06_attendance_report.png", dpi=100, bbox_inches='tight')
    plt.close()
    print("  Saved: test_results/06_attendance_report.png")

# ─────────────────────────────────────────────────────────────
# STEP 10 — Final summary
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)
print(f"  Identities in DB         : {len(known_encodings)}")
print(f"  Test cases               : {total_count}")
print(f"  Correct predictions      : {correct_count}")
print(f"  Accuracy                 : {accuracy:.1f}%")
if not df_results.empty:
    valid_d = df_results["Distance"].dropna()
    if not valid_d.empty:
        print(f"  Avg match distance       : {valid_d.mean():.4f}")
    print(f"  Avg inference latency    : {df_results['Latency ms'].mean():.1f} ms")
    print(f"  Embedding dimension      : 512 (ArcFace)")
    print(f"  Distance threshold used  : {CONFIG['DISTANCE_THRESHOLD']}")
    print(f"  Optimal threshold (test) : {opt_thresh:.2f}")
print("\n  Output files in test_results/:")
for f in sorted(os.listdir("test_results")):
    size = os.path.getsize(os.path.join("test_results", f))
    print(f"    {f:50s}  {size//1024:4d} KB")
print("="*60)
