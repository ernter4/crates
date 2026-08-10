import pulp
import pandas as pd

# ==========================================
# 1. BEISPIELDATEN (Input Data)
# ==========================================

# Kundenliste
customers = ["Kunde_A", "Kunde_B", "Kunde_C"]

# Verfügbare Kisten
boxes = [ i for i in range(1, 5)]  # 5 Kisten

# Initialzustand am Morgen (U_0): Welche Karte klebt morgens auf welcher Kiste?
# Kiste 1 & 2 -> Kunde A, Kiste 3 & 4 -> Kunde B, Kiste 5 -> Kunde C
initial_state = {
    1: "Kunde_A",
    2: "Kunde_A",
    3: "Kunde_B",
    4: "Kunde_B",
}

# Unsortierte Jobs des Tages (Startzeit in Minuten ab 00:00 Uhr, Dauer in Minuten)
raw_jobs = [
    {"id": "Job_1", "customer": "Kunde_A", "start": 1, "duration": 2},
    {"id": "Job_2", "customer": "Kunde_B", "start":1, "duration": 3},  # 08:00 - 09:30 (zeitgleich mit Job 1)
    {"id": "Job_3", "customer": "Kunde_C", "start": 510, "duration": 60},  # 08:30 - 09:30
    {"id": "Job_4", "customer": "Kunde_A", "start": 600, "duration": 180},  # 10:00 - 13:00
    {"id": "Job_5", "customer": "Kunde_B", "start": 630, "duration": 120},  # 10:30 - 12:30
    {"id": "Job_6", "customer": "Kunde_A", "start": 780, "duration": 90},  # 13:00 - 14:30
]

# ==========================================
# 2. PRE-PROCESSING
# ==========================================

# Strikt chronologische Sortierung nach Startzeit (mit Job-ID als Tie-Breaker)
sorted_jobs = sorted(raw_jobs, key=lambda x: (x["start"], x["id"]))

# Mapping der Indizes j in {1, ..., n}
n_jobs = len(sorted_jobs)
J = list(range(1, n_jobs + 1))
K = boxes
C = customers

# Dictionary-Zugriffe für Parameter
job_dict = {j: sorted_jobs[j - 1] for j in J}
S = {j: job_dict[j]["start"] for j in J}
P = {j: job_dict[j]["duration"] for j in J}
E = {j: S[j] + P[j] for j in J}
c_job = {j: job_dict[j]["customer"] for j in J}

# Binäre Matrix U_0
U_0 = {}
for k in K:
    for c in C:
        U_0[k, c] = 1 if initial_state[k] == c else 0

# Erzeugung des Überlappungsgraphen O
O = []
for j1 in J:
    for j2 in J:
        if j1 < j2 and S[j1] <= S[j2] < E[j1]:
            O.append((j1, j2))

# ==========================================
# 3. MILP MODELLERSTELLUNG (PuLP)
# ==========================================

model = pulp.LpProblem("Kisten_Scheduling_Minimum_Cards", pulp.LpMinimize)

# --- Entscheidungsvariablen ---
# ÄNDERUNG: Explizite Liste von Tuples übergeben
x = pulp.LpVariable.dicts("x", [(j, k) for j in J for k in K], cat=pulp.LpBinary)
y = pulp.LpVariable.dicts("y", [(j, k) for j in J for k in K], cat=pulp.LpBinary)
u = pulp.LpVariable.dicts("u", [(j, k, c) for j in J for k in K for c in C], cat=pulp.LpBinary)

# --- Zielfunktion ---
model += pulp.lpSum(y[j, k] for j in J for k in K), "Gesamtzahl_Kartenwechsel"

# --- Nebenbedingungen ---

# A. Eindeutige Job-Zuweisung: Jeder Job genau eine Kiste
for j in J:
    model += pulp.lpSum(x[j, k] for k in K) == 1, f"Assign_Job_{j}"

# B. Kapazität & Zeitkonflikte (Überlappungssperre)
for k in K:
    for (j1, j2) in O:
        model += x[j1, k] + x[j2, k] <= 1, f"Overlap_k{k}_j{j1}_j{j2}"

# C. Eindeutigkeit des Zustandscodes
for j in J:
    for k in K:
        model += pulp.lpSum(u[j, k, c] for c in C) == 1, f"SingleState_j{j}_k{k}"

# ==========================================
# D. Sequentielle Zustandsverfolgung (u_j,k,c)
# ==========================================

for k in K:
    # --- 1. Neuzuweisung bei Nutzung (hängt nur von j und k ab) ---
    # Für j = 1
    model += u[1, k, c_job[1]] >= x[1, k], f"StateInit_Use_k{k}"

    # Für j > 1
    for j in J:
        if j > 1:
            model += u[j, k, c_job[j]] >= x[j, k], f"State_Use_j{j}_k{k}"

    # --- 2. Zustandserhalt bei Nicht-Nutzung (hängt von j, k UND c ab) ---
    for c in C:
        # Für j = 1
        model += u[1, k, c] <= U_0[k, c] + x[1, k], f"StateInit_Hold1_k{k}_c{c}"
        model += u[1, k, c] >= U_0[k, c] - x[1, k], f"StateInit_Hold2_k{k}_c{c}"

        # Für j > 1
        for j in J:
            if j > 1:
                model += u[j, k, c] <= u[j - 1, k, c] + x[j, k], f"State_Hold1_j{j}_k{k}_c{c}"
                model += u[j, k, c] >= u[j - 1, k, c] - x[j, k], f"State_Hold2_j{j}_k{k}_c{c}"

# ==========================================
# E. Aktivierung der Kartenwechsel-Strafe (y_j,k)
# ==========================================

for k in K:
    # Für j = 1
    model += y[1, k] >= x[1, k] - U_0[k, c_job[1]], f"Penalty_j1_k{k}"

    # Für j > 1
    for j in J:
        if j > 1:
            model += y[j, k] >= x[j, k] - u[j - 1, k, c_job[j]], f"Penalty_j{j}_k{k}"
# ==========================================
# 4. LÖSUNG DES MODELLS
# ==========================================

solver = pulp.PULP_CBC_CMD(msg=False)
status = model.solve(solver)

# ==========================================
# 5. ERGEBNISAUSGABE
# ==========================================

print(f"Status der Optimierung: {pulp.LpStatus[status]}")
print(f"Minimale Anzahl Kartenwechsel gesamt: {int(pulp.value(model.objective))}\n")

# Tabellarische Auswertung
schedule = []
for j in J:
    assigned_box = [k for k in K if pulp.value(x[j, k]) > 0.5][0]
    card_change = int(pulp.value(y[j, assigned_box]))

    # Ermittlung des Vorzustands für die Ausgabe
    if j == 1:
        prev_card = initial_state[assigned_box]
    else:
        prev_card = [c for c in C if pulp.value(u[j - 1, assigned_box, c]) > 0.5][0]

    schedule.append({
        "Job ID": job_dict[j]["id"],
        "Start": f"{S[j] // 60:02d}:{S[j] % 60:02d}",
        "Ende": f"{E[j] // 60:02d}:{E[j] % 60:02d}",
        "Kunde": c_job[j],
        "Zugewiesene Kiste": assigned_box,
        "Karte Vorher": prev_card,
        "Kartenwechsel nötig?": "JA" if card_change == 1 else "Nein"
    })

df_schedule = pd.DataFrame(schedule)
print(df_schedule.to_string(index=False))