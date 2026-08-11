from datetime import timedelta

import pulp

from sqlmodel import select, desc

from app.ordering.models import Order, Crate
from app.ordering.services.assignment.interface import AssignmentServiceInterface


class MilpAssigner(AssignmentServiceInterface):
    """
    MILP-basierte Zuordnung von Bestellungen zu Kisten (Kartenwechsel-Minimierung).

    Nur die Bestellungen des Tages `self.assign_date` (self.orders) werden
    tatsächlich neu zugeordnet und in der Datenbank gespeichert. Alle
    künftigen Bestellungen (delivery_date > assign_date) fließen lediglich
    als zusätzliche Jobs in die Optimierung ein, damit die heutige
    Zuordnung eine bereits absehbare künftige Belegung der Kisten
    berücksichtigt - ihre Kistenzuordnung wird dabei NICHT verändert.
    """

    def assign(self):
        if not self.orders:
            return

        # ==========================================
        # 1. EINGABEDATEN (aus der Datenbank)
        # ==========================================

        # Verfügbare Kisten
        crates = list(self.session.exec(select(Crate)).all())
        if not crates:
            return
        boxes = [crate.id for crate in crates]

        # Zukünftige Bestellungen dienen nur als Hilfe für die Optimierung
        # (bessere Vorausplanung der Kartenwechsel) - ihre Kistenzuordnung
        # wird nicht verändert/gespeichert.
        future_orders = list(
            self.session.exec(
                select(Order)
                .where(Order.delivery_date > self.assign_date )
                .where(Order.delivery_date< self.assign_date+timedelta(days=5))
                .where(Order.deleted == False)
            ).all()
        )
        job_orders = list(self.orders) + future_orders
        order_by_id = {order.id: order for order in job_orders}

        customers = {order.customer_id for order in job_orders}

        # Initialzustand am Morgen (U_0): Welche Karte klebt morgens auf welcher Kiste?
        # -> Kunde der letzten Bestellung, die die Kiste vor assign_date hatte
        initial_state = {}
        for crate in crates:
            last_order = self.session.exec(
                select(Order)
                .where(Order.crate_id == crate.id)
                .where(Order.delivery_date < self.assign_date)
                .order_by(desc(Order.delivery_date))
            ).first()
            if last_order is not None:
                initial_state[crate.id] = last_order.customer_id
                customers.add(last_order.customer_id)

        # Unsortierte Jobs des Zeitraums (Start = delivery_date, Dauer bis return_date)
        # Ist return_date (noch) nicht gesetzt (Kiste wurde noch nicht
        # zurückgegeben), ist die Dauer unbekannt - der Job blockiert dann
        # nur seinen eigenen delivery_date für die Überlappungsprüfung.
        raw_jobs = [
            {
                "id": order.id,
                "customer": order.customer_id,
                "start": order.delivery_date.toordinal(),
                "end": (
                    order.return_date.date().toordinal()
                    if order.return_date is not None
                    else order.delivery_date.toordinal()
                ),
            }
            for order in job_orders
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
        C = sorted(customers)

        # Dictionary-Zugriffe für Parameter
        job_dict = {j: sorted_jobs[j - 1] for j in J}
        S = {j: job_dict[j]["start"] for j in J}
        E = {j: job_dict[j]["end"] for j in J}
        c_job = {j: job_dict[j]["customer"] for j in J}

        # Kundencodes: 0 = keine Karte/leere Kiste, 1..|C| = tatsächliche Kunden.
        # Ersetzt die frühere One-Hot-Matrix U_0 (Kiste x Kunde) durch einen
        # einzelnen Code pro Kiste - das ist der Schlüssel zur Verkleinerung
        # des Modells weiter unten (siehe state[j,k]).
        c_code = {c: idx + 1 for idx, c in enumerate(C)}
        big_m = max(len(C), 1)  # deckt den vollen Wertebereich der Codes ab

        initial_code = {
            k: c_code[initial_state[k]] if k in initial_state else 0
            for k in K
        }

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
        x = pulp.LpVariable.dicts("x", [(j, k) for j in J for k in K], cat=pulp.LpBinary)
        y = pulp.LpVariable.dicts("y", [(j, k) for j in J for k in K], cat=pulp.LpBinary)
        # state[j,k]: Kundencode, der nach Job j auf Kiste k "klebt". Da dieser
        # Wert durch x eindeutig festgelegt wird, genügt EINE kontinuierliche
        # Variable pro (j,k) statt eines binären u[j,k,c] pro Kunde c - das
        # spart einen Faktor |C| an Variablen und Nebenbedingungen.
        state = pulp.LpVariable.dicts(
            "state", [(j, k) for j in J for k in K], lowBound=0, upBound=big_m, cat=pulp.LpContinuous
        )
        # d[j,k] = 1, falls der Kundencode vor Job j von dessen Kunde abweicht
        d = pulp.LpVariable.dicts("d", [(j, k) for j in J for k in K], cat=pulp.LpBinary)

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

        # ==========================================
        # C. Sequentielle Zustandsverfolgung (state_j,k) + Abweichungserkennung (d_j,k)
        # ==========================================

        for k in K:
            for j in J:
                prev = initial_code[k] if j == 1 else state[j - 1, k]

                # state[j,k] = Kunde von Job j, falls Kiste k dafür genutzt wird,
                # sonst bleibt der vorherige Zustand erhalten.
                model += state[j, k] <= c_code[c_job[j]] + big_m * (1 - x[j, k]), f"State_Use1_j{j}_k{k}"
                model += state[j, k] >= c_code[c_job[j]] - big_m * (1 - x[j, k]), f"State_Use2_j{j}_k{k}"
                model += state[j, k] <= prev + big_m * x[j, k], f"State_Hold1_j{j}_k{k}"
                model += state[j, k] >= prev - big_m * x[j, k], f"State_Hold2_j{j}_k{k}"

                # d[j,k] = 1, sobald der Zustand vor Job j nicht zu dessen Kunde passt
                model += prev - c_code[c_job[j]] <= big_m * d[j, k], f"Diff1_j{j}_k{k}"
                model += c_code[c_job[j]] - prev <= big_m * d[j, k], f"Diff2_j{j}_k{k}"

        # ==========================================
        # D. Aktivierung der Kartenwechsel-Strafe (y_j,k = x_j,k AND d_j,k)
        # ==========================================

        for k in K:
            for j in J:
                model += y[j, k] >= x[j, k] + d[j, k] - 1, f"Penalty_j{j}_k{k}"

        # ==========================================
        # 4. LÖSUNG DES MODELLS
        # ==========================================

        solver = pulp.PULP_CBC_CMD(msg=True)


        model.solve(solver)

        # ==========================================
        # 5. ERGEBNIS: NUR self.orders ZURÜCKSCHREIBEN
        # ==========================================

        crate_by_id = {crate.id: crate for crate in crates}
        assign_order_ids = {order.id for order in self.orders}

        for j in J:
            order_id = job_dict[j]["id"]
            if order_id not in assign_order_ids:
                continue
            assigned_box = [k for k in K if pulp.value(x[j, k]) > 0.5][0]
            current_order = order_by_id[order_id]
            current_order.crate = crate_by_id[assigned_box]
            self.session.add(current_order)