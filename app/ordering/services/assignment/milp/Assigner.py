from datetime import datetime, time, timedelta

import pulp

from sqlmodel import select, desc, or_

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
                .where(Order.delivery_date< self.assign_date + timedelta(days=3))
                .where(Order.deleted == False)
            ).all()
        )
        # Bereits laufende Bestellungen: auf ihrer bisherigen Kiste (crate_id)
        # klebt ihre Karte noch, weil sie bis mindestens self.assign_date
        # nicht zurückgegeben wurde - unabhängig davon, wie weit ihr
        # delivery_date schon zurückliegt. Ohne das kennt die Kapazitäts-/
        # Überlappungsprüfung (siehe O unten) nur Jobs ab self.orders bzw.
        # future_orders (max. 3 Tage voraus) und hält Kisten, die länger als
        # dieses Fenster unterwegs sind, fälschlich für frei - identischer
        # Fehler wie vormals in GreedyAssigner.get_present_crates. Ihre Kiste
        # ist bereits real fix (crate_id); sie werden unten per harter
        # Constraint auf genau diese Kiste gepinnt statt neu optimiert.
        not_returned_yet = Order.return_date >= datetime.combine(self.assign_date, time.min) + timedelta(days=1)
        still_open_orders = list(
            self.session.exec(
                select(Order)
                .where(Order.crate_id != None)
                .where(Order.delivery_date < self.assign_date)
                .where(Order.deleted == False)
                .where(or_(Order.return_date == None, not_returned_yet))
            ).all()
        )
        fixed_crate_by_order_id = {order.id: order.crate_id for order in still_open_orders}

        job_orders = list(self.orders) + future_orders + still_open_orders
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
                .where(Order.deleted == False)
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

        # Binäre Matrix U_0
        U_0 = {}
        for k in K:
            for c in C:
                U_0[k, c] = 1 if initial_state.get(k) == c else 0

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
        u = pulp.LpVariable.dicts("u", [(j, k, c) for j in J for k in K for c in C], cat=pulp.LpBinary)
                      # --- Warmstart ---
        x_start = self.get_warm_start(J, K, C, S, E, c_job, U_0)
        for (j, k) in x_start:
            x[j, k].setInitialValue(1)
            for alternatek in K:
                if alternatek != k:
                    x[j, alternatek].setInitialValue(0)

        # --- Zielfunktion ---
        model += pulp.lpSum(y[j, k] for j in J for k in K), "Gesamtzahl_Kartenwechsel"

        # --- Nebenbedingungen ---

        # A. Eindeutige Job-Zuweisung: Jeder Job genau eine Kiste
        for j in J:
            model += pulp.lpSum(x[j, k] for k in K) == 1, f"Assign_Job_{j}"

        # A2. Fixierung bereits laufender Jobs (still_open_orders) auf ihre
        # echte, bereits bekannte Kiste - sie werden nicht neu optimiert,
        # sondern blockieren darüber nur diese Kiste für die Dauer ihrer
        # Überlappung (siehe O unten).
        for j in J:
            fixed_crate = fixed_crate_by_order_id.get(job_dict[j]["id"])
            if fixed_crate is not None:
                model += x[j, fixed_crate] == 1, f"FixedAssignment_j{j}"

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

        # timeLimit/gapRel: die durch still_open_orders jetzt vollstaendige
        # Kapazitaetspruefung (siehe oben) vergroessert das Modell spuerbar -
        # ein Beweis der EXAKTEN Optimalitaet kann pro Tag mehrere Minuten
        # dauern. Ein 2%-Gap ist fuer die Kartenwechsel-Zaehlung praktisch
        # nicht von der exakten Loesung zu unterscheiden, laeuft aber in
        # angemessener Zeit durch - auch fuer den taeglichen Live-Einsatz
        # relevant (der sonst ebenso lange haengen wuerde).
        solver = pulp.GUROBI(msg=True, warmStart=True, timeLimit=90, gapRel=0.02)
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
            current_order.assigned_crate_id = assigned_box
            self.session.add(current_order)
            self.session.commit()

    def get_warm_start(self, J, K, C, S, E, c_job, U_0):
        """
        Erzeugt eine heuristische Startlösung (Warmstart) für die x-Variablen
        des MILP-Solvers.

        Analog zur "perfect crate"-Logik des GreedyAssigner (siehe
        `greedy.Assigner.GreedyAssigner.assign`) wird für jeden Job die Kiste
        gesucht, auf der zuletzt die Karte desselben Kunden klebte. Dafür
        wird Tag für Tag (chronologisch, wie in `J` sortiert) durch die Jobs
        iteriert und der Kistenzustand mitgeführt.

        Es wird nur bei einem echten "perfect crate"-Treffer ein Startwert
        vorgegeben: die Kiste muss frei sein und dabei höchstens 1 Tag
        ungenutzt geblieben sein. Andernfalls bekommt der Job keinen
        Startwert (kein Ausweichen auf eine andere Kiste).

        Zurückgegeben wird nur die Menge der (j, k), die belegt werden
        sollen (x_jk = 1) - nicht die vollständige, mit Nullen aufgefüllte
        Matrix.
        """
        # Zustand je Kiste: Kunde, dessen Karte aktuell klebt, und Tag, ab
        # dem die Kiste wieder frei ist (None = Zustand vor `assign_date`,
        # Leerstandsdauer unbekannt).
        current_customer = {k: None for k in K}
        free_from = {k: None for k in K}
        for k in K:
            for c in C:
                if U_0.get((k, c)) == 1:
                    current_customer[k] = c

        x_start = {}

        for j in J:  # J ist bereits chronologisch (Tag für Tag) sortiert
            day = S[j]
            customer = c_job[j]

            chosen = None
            for k in K:
                if current_customer[k] != customer:
                    continue
                if free_from[k] is not None and not (free_from[k] <= day <= free_from[k] + 1):
                    continue
                chosen = k
                break

            if chosen is not None:
                x_start[j, chosen] = 1
                current_customer[chosen] = customer
                free_from[chosen] = E[j]

        return x_start