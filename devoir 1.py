import json
import os

FICHIYE_JSON = "agence_data.json"


class Vehicule:
    def __init__(self, immatriculation, marque, tarif_journalier):
        immatriculation = immatriculation.strip()
        marque = marque.strip()
        if immatriculation == "":
            print("L'immatriculation ne peut pas etre vide")
        if marque == "":
            print("La marque ne peut pas etre vide")
        if tarif_journalier <= 0:
            print("Le tarif doit etre positif")
        self._immatriculation = immatriculation
        self._marque = marque
        self._tarif = tarif_journalier

    def lire_tarif(self):
        return self._tarif

    def change_tarif(self, nouveau_tarif):
        if nouveau_tarif <= 0:
            print("Le tarif doit etre superieur a 0")
            return False
        self._tarif = nouveau_tarif
        return True

    def description(self):
        return f"{self._immatriculation} - {self._marque} - {self._tarif}"

    def calcule_location(self, nombre_jour):
        if nombre_jour <= 0:
            print("Le jour doit etre superieur a 0")
            return 0
        return self._tarif * nombre_jour


class Voiture(Vehicule):
    def __init__(self, immatriculation, marque, tarif_journalier, nb_place):
        super().__init__(immatriculation, marque, tarif_journalier)
        self._nb_place = nb_place

    def calcule_location(self, nombre_jour):
        montant = super().calcule_location(nombre_jour)
        if nombre_jour >= 7:
            montant = round(montant * 0.9, 2)
        return montant

    def description(self):
        return super().description() + f" - {self._nb_place} places"


class Moto(Vehicule):
    def __init__(self, immatriculation, marque, tarif_journalier, cylindre):
        super().__init__(immatriculation, marque, tarif_journalier)
        self._cylindre = cylindre

    def calcule_location(self, nombre_jour):
        montant = super().calcule_location(nombre_jour)
        if montant == 0:
            return 0
        return montant + 10

    def description(self):
        return super().description() + f" - {self._cylindre} cm3"


class Client:
    def __init__(self, id_client, nom, email, telephone):
        nom = nom.strip()
        email = email.strip()
        telephone = telephone.strip()
        if nom == "":
            print("Le nom ne peut pas etre vide")
        if "@" not in email:
            print("L'email n'est pas correct")
        if telephone == "":
            print("Le telephone ne peut pas etre vide")
        self.id_client = id_client
        self.nom = nom
        self.email = email
        self.telephone = telephone

    def description(self):
        return f"{self.id_client} - {self.nom} - {self.email} - {self.telephone}"


class Reservation:
    def __init__(self, id_reservation, client, vehicule, date_debut, date_fin, statut="confirme", frais_retard=0):
        self._id = id_reservation
        self._client = client
        self._vehicule = vehicule
        self._date_debut = date_debut
        self._date_fin = date_fin
        self._statut = statut
        self._frais_retard = frais_retard

    def lire_statut(self):
        return self._statut

    def depart(self):
        if self._statut != "confirme":
            print("Depart impossible : la reservation est " + self._statut)
            return False
        self._statut = "en_cours"
        return True

    def retour(self, jour_retour):
        if self._statut != "en_cours":
            print("Retour impossible : la reservation est " + self._statut)
            return False
        if jour_retour > self._date_fin:
            retard = jour_retour - self._date_fin
            self._frais_retard = retard * self._vehicule.lire_tarif() * 1.5
        self._statut = "termine"
        return True

    def total(self):
        return self.montant() + self._frais_retard

    def nombre_jour(self):
        return self._date_fin - self._date_debut

    def montant(self):
        return self._vehicule.calcule_location(self.nombre_jour())

    def chevauche(self, autre):
        if self._vehicule._immatriculation != autre._vehicule._immatriculation:
            return False
        return self._date_debut < autre._date_fin and autre._date_debut < self._date_fin

    def description(self):
        return (
            f"Reservation {self._id} - {self._client.description()} - "
            f"{self._vehicule.description()} - du {self._date_debut} "
            f"au {self._date_fin} - {self.montant()}"
        )


class Agence:
    def __init__(self):
        self._vehicules = []
        self._clients = []
        self._reservations = []
        self._prochain_id = 1
        self.charger_donnees()

    def sauvegarder_donnees(self):
        """Sove tout sa ki gen nan ajans lan nan yon fichye JSON otomatikman"""
        donnees = {
            "prochain_id": self._prochain_id,
            "vehicules": [
                {
                    "type": "voiture" if isinstance(v, Voiture) else "moto",
                    "immatriculation": v._immatriculation,
                    "marque": v._marque,
                    "tarif": v._tarif,
                    "extra": v._nb_place if isinstance(v, Voiture) else v._cylindre
                } for v in self._vehicules
            ],
            "clients": [
                {
                    "id": c.id_client,
                    "nom": c.nom,
                    "email": c.email,
                    "telephone": c.telephone
                } for c in self._clients
            ],
            "reservations": [
                {
                    "id": r._id,
                    "client_id": r._client.id_client,
                    "immat_vehicule": r._vehicule._immatriculation,
                    "date_debut": r._date_debut,
                    "date_fin": r._date_fin,
                    "statut": r._statut,
                    "frais_retard": r._frais_retard
                } for r in self._reservations
            ]
        }
        with open(FICHIYE_JSON, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)

    def charger_donnees(self):
        """Lè pwogram nan kòmanse, l ap chache fichye a pou retabli done yo"""
        if not os.path.exists(FICHIYE_JSON):
            return

        try:
            with open(FICHIYE_JSON, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                self._prochain_id = donnees.get("prochain_id", 1)

                # Rekonstwi Machin yo
                for v_data in donnees.get("vehicules", []):
                    if v_data["type"] == "voiture":
                        self._vehicules.append(
                            Voiture(v_data["immatriculation"], v_data["marque"], v_data["tarif"], v_data["extra"]))
                    else:
                        self._vehicules.append(
                            Moto(v_data["immatriculation"], v_data["marque"], v_data["tarif"], v_data["extra"]))

                # Rekonstwi Kliyan yo
                for c_data in donnees.get("clients", []):
                    self._clients.append(Client(c_data["id"], c_data["nom"], c_data["email"], c_data["telephone"]))

                # Rekonstwi Rezèvasyon yo
                for r_data in donnees.get("reservations", []):
                    client_trouve = next((c for c in self._clients if c.id_client == r_data["client_id"]), None)
                    vehicule_trouve = next(
                        (v for v in self._vehicules if v._immatriculation == r_data["immat_vehicule"]), None)

                    if client_trouve and vehicule_trouve:
                        res = Reservation(
                            r_data["id"], client_trouve, vehicule_trouve,
                            r_data["date_debut"], r_data["date_fin"],
                            r_data["statut"], r_data["frais_retard"]
                        )
                        self._reservations.append(res)
        except Exception as e:
            print(f"Erè nan chajman done yo: {e}")

    def ajoute_vehicule(self, vehicule):
        self._vehicules.append(vehicule)
        self.sauvegarder_donnees()

    def ajoute_client(self, client):
        self._clients.append(client)
        self.sauvegarder_donnees()

    def reserve(self, client, vehicule, date_debut, date_fin):
        if date_fin <= date_debut:
            print("La date de fin doit etre apres la date de debut")
            return None
        nouvelle = Reservation(self._prochain_id, client, vehicule, date_debut, date_fin)
        for r in self._reservations:
            if r.chevauche(nouvelle):
                print("Refuse : le vehicule est deja reserve a ces dates")
                return None
        self._reservations.append(nouvelle)
        self._prochain_id += 1
        self.sauvegarder_donnees()
        return nouvelle

    def liste_reservation(self):
        if not self._reservations:
            print("Okenn rezèvasyon.")
        for r in self._reservations:
            print(r.description())

    def liste_vehicules(self):
        if not self._vehicules:
            print("Okenn machin.")
        for i in range(len(self._vehicules)):
            print(i + 1, "-", self._vehicules[i].description())

    def liste_clients(self):
        if not self._clients:
            print("Okenn kliyan.")
        for c in self._clients:
            print(c.description())

    def trouver_vehicule(self, numero):
        if 1 <= numero <= len(self._vehicules):
            return self._vehicules[numero - 1]
        return None

    def trouver_client(self, numero):
        if 1 <= numero <= len(self._clients):
            return self._clients[numero - 1]
        return None

    def trouver_reservation(self, numero):
        if 1 <= numero <= len(self._reservations):
            return self._reservations[numero - 1]
        return None

    def nombre_clients(self):
        return len(self._clients)


def lire_entier(message):
    texte = input(message)
    while not texte.isdigit():
        print("Entrer un nombre entier : ")
        texte = input(message)
    return int(texte)


def menu():
    agence = Agence()
    while True:
        print()
        print("1. Ajouter un vehicule")
        print("2. Ajouter un client")
        print("3. Faire une reservation")
        print("4. Liste des reservations")
        print("5. Depart")
        print("6. Retour")
        print("0. Quitter")
        choix = input("Votre choix : ")

        if choix == "0":
            print("Au revoir")
            break
        elif choix == "1":
            type_v = input("Type (voiture/moto) : ").strip().lower()
            immat = input("Immatriculation : ")
            marque = input("Marque : ")
            tarif = lire_entier("Tarif journalier : ")
            if type_v == "voiture":
                places = lire_entier("Nombre de places : ")
                agence.ajoute_vehicule(Voiture(immat, marque, tarif, places))
                print("✔ Machin anrejistre epi sove nan JSON!")
            elif type_v == "moto":
                cylindre = lire_entier("Cylindree : ")
                agence.ajoute_vehicule(Moto(immat, marque, tarif, cylindre))
                print("✔ Moto anrejistre epi sove nan JSON!")
            else:
                print("Type inconnu")
        elif choix == "2":
            nom = input("Nom : ")
            email = input("Email : ")
            telephone = input("Telephone : ")
            id_client = agence.nombre_clients() + 1
            agence.ajoute_client(Client(id_client, nom, email, telephone))
            print("✔ Kliyan anrejistre epi sove nan JSON!")
        elif choix == "3":
            agence.liste_clients()
            if agence._clients:
                client = agence.trouver_client(lire_entier("Numero du client : "))
                agence.liste_vehicules()
                if agence._vehicules:
                    vehicule = agence.trouver_vehicule(lire_entier("Numero du vehicule : "))

                    if client is None or vehicule is None:
                        print("Client ou vehicule introuvable")
                    else:
                        debut = lire_entier("Jour de debut : ")
                        fin = lire_entier("Jour de fin : ")
                        r = agence.reserve(client, vehicule, debut, fin)
                        if r is not None:
                            print("✔ Reservation acceptee epi sove!")
        elif choix == "4":
            agence.liste_reservation()
        elif choix == "5":
            r = agence.trouver_reservation(lire_entier("Numero de la reservation : "))
            if r is None:
                print("Reservation introuvable")
            else:
                if r.depart():
                    agence.sauvegarder_donnees()
                    print("✔ Depart enregistre!")
        elif choix == "6":
            r = agence.trouver_reservation(lire_entier("Numero de la reservation : "))
            if r is None:
                print("Reservation introuvable")
            else:
                jour = lire_entier("Jour de retour : ")
                if r.retour(jour):
                    agence.sauvegarder_donnees()
                    print(f" Retour enregistre, total a payer : {r.total()}")
        else:
            print("Choix invalide")


if __name__ == "__main__":
    menu()