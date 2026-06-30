import numpy as np
import re
from io import StringIO
import matplotlib.pyplot as plt


# =========================
# Extract numeric block
# =========================
def extract_matrix_block(text, key):
    pattern = rf"{key}\s*:\s*(\[[\s\S]*?\])"

    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not find {key}")

    block = match.group(1)

    print(block)

    # Remove outer brackets only
    block = block.strip()
    block = block.replace("[", "").replace("]", "")

    # IMPORTANT: preserve row structure by ensuring line breaks remain
    block = block.replace("nan", "nan")

    return block


def load_matrix(text, key):
    block = extract_matrix_block(text, key)

    print(block)

    # Convert multiple spaces into consistent spacing
    # BUT keep line breaks intact
    lines = []
    for line in block.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    cleaned = "\n".join(lines)

    print(cleaned)

    arr = np.loadtxt(StringIO(cleaned))

    # Ensure 2D shape
    return np.atleast_2d(arr)


def extract_numeric_block(text, key):
    """
    Extracts the array after a key like 'S1:' or 'S2:'.
    Returns a cleaned string suitable for np.loadtxt.
    """

    pattern = rf"{key}\s*:\s*(\[[\s\S]*?\])"
    match = re.search(pattern, text)

    if not match:
        raise ValueError(f"Could not find {key}")

    block = match.group(1)

    # Convert numpy-style spacing to CSV-like spacing
    block = block.replace("[", "").replace("]", "")
    block = block.replace("nan", "nan")

    return block


def load_vector(text, key):
    block = extract_numeric_block(text, key)
    return np.loadtxt(StringIO(block))


def load_names(text):
    match = re.search(r"'names'\s*:\s*\[(.*?)\]", text, re.S)
    if not match:
        raise ValueError("Could not find names")

    raw = "[" + match.group(1) + "]"
    return eval(raw)


# =========================
# Load file
# =========================
with open("src/sobol_results.txt", "r") as f:
    text = f.read()

names = load_names(text)
names_dict = {
    "n_police": r"$N_{\text{police}}$",
    "fine": r"$F$",
    "loot": r"$L$",
    "police_attentiveness": r"$P_{\text{att}}$",
    "police_vision_radius": r"$r_{\text{police}}$",
    "thief_vision_radius": r"$r_{\text{thief}}$",
}
name_labels = [names_dict[key] for key in names]

S1 = load_vector(text, "S1")
S1_conf = load_vector(text, "S1_conf")

ST = load_vector(text, "ST")
ST_conf = load_vector(text, "ST_conf")


# =========================
# Plot
# =========================
fig = plt.figure(figsize=(8, 10))
x = np.arange(len(names))

# ---- S1 ----
ax1 = plt.subplot(2, 1, 1)
ax1.bar(x, S1, yerr=S1_conf, capsize=5)
ax1.set_xticks(x)
ax1.set_xticklabels(name_labels, rotation=45, ha="right")
ax1.set_ylabel("First-order Sobol indices")
ax1.set_title("First-order Sobol indices for different parameters on successful thefts")

# ---- ST ----
ax2 = plt.subplot(2, 1, 2)
ax2.bar(x, ST, yerr=ST_conf, capsize=5, color="orange")
ax2.set_xticks(x)
ax2.set_xticklabels(name_labels, rotation=45, ha="right")
ax2.set_ylabel("Total-order Sobol indices")
ax2.set_title("Total-order Sobol indices for different parameters on successful thefts")


plt.tight_layout()
plt.savefig("sensitivity_plots.png")
plt.show()

