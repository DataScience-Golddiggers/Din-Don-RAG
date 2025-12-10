import csv
import random
import os

def generate_dataset(output_file, num_samples=1000):
    # Define templates for different categories (intents)
    templates = {
        "tasse": [
            "Quanto costano le tasse universitarie?",
            "Quali sono le scadenze per le tasse?",
            "Come posso pagare la prima rata?",
            "Ci sono agevolazioni per l'ISEE?",
            "A quanto ammonta la seconda rata?",
            "Dove trovo il bollettino per le tasse?",
            "Ho pagato le tasse in ritardo, c'è una mora?",
            "Come richiedere la riduzione delle tasse?",
            "Qual è l'importo massimo delle tasse?",
            "Esiste un rimborso per le tasse?",
            "Vorrei sapere quanto si paga di tasse.",
            "Mi dici le scadenze dei pagamenti?",
            "Come funziona il calcolo delle tasse in base al reddito?",
            "Devo pagare la tassa regionale?",
            "Quando scade la terza rata?"
        ],
        "corsi": [
            "Quali corsi di laurea offrite?",
            "C'è un corso di ingegneria informatica?",
            "Mi parli del corso di medicina?",
            "Qual è il piano di studi per economia?",
            "Quali sono gli insegnamenti del primo anno?",
            "I corsi sono a frequenza obbligatoria?",
            "Dove trovo l'elenco dei corsi disponibili?",
            "C'è un corso di laurea magistrale in fisica?",
            "Vorrei informazioni sul corso di lettere.",
            "Quali materie si studiano a giurisprudenza?",
            "Il corso di design è a numero chiuso?",
            "Come funziona il corso di laurea triennale?",
            "Ci sono corsi in lingua inglese?",
            "Posso seguire i corsi online?",
            "Chi è il coordinatore del corso di biologia?"
        ],
        "localita": [
            "Dove si trova l'università?",
            "Qual è l'indirizzo della sede centrale?",
            "Come arrivo al campus?",
            "Dove sono le aule di ingegneria?",
            "C'è una mappa delle sedi?",
            "In che via si trova la segreteria?",
            "Come raggiungo l'università dalla stazione?",
            "Dove si svolgono le lezioni di matematica?",
            "La sede di architettura è in centro?",
            "Qual è la posizione del laboratorio di chimica?",
            "Dove posso parcheggiare vicino all'università?",
            "Ci sono navette per il campus?",
            "L'università è accessibile ai disabili?",
            "Dove si trova l'aula magna?",
            "Mi indichi la strada per la facoltà?"
        ],
        "iscrizione": [
            "Come faccio a iscrivermi?",
            "Quando aprono le immatricolazioni?",
            "C'è un test d'ingresso?",
            "Quali documenti servono per l'iscrizione?",
            "Come funziona la procedura di immatricolazione online?",
            "Posso iscrivermi part-time?",
            "Qual è la scadenza per l'iscrizione?",
            "Come mi iscrivo al test di ammissione?",
            "Cosa devo fare per il trasferimento da un altro ateneo?",
            "L'iscrizione è aperta agli studenti stranieri?",
            "Come recupero le credenziali per l'iscrizione?",
            "Devo portare il diploma originale?",
            "Come finalizzo l'iscrizione?",
            "C'è un bando per l'ammissione?",
            "Posso iscrivermi con riserva?"
        ],
        "esami": [
            "Quando sono gli appelli d'esame?",
            "Come mi prenoto a un esame?",
            "Dove trovo il calendario degli esami?",
            "Posso rifiutare un voto?",
            "Come funziona la verbalizzazione?",
            "Quanti appelli ci sono all'anno?",
            "Cosa succede se non passo un esame?",
            "Gli esami sono scritti o orali?",
            "Dove vedo i risultati degli esami?",
            "Posso dare esami di altri corsi?",
            "Come cancello una prenotazione?",
            "Quando escono le date degli esami?",
            "C'è il salto d'appello?",
            "Posso sostenere due esami lo stesso giorno?",
            "Chi contatto per problemi con la prenotazione?"
        ],
        "contatti": [
            "Qual è il numero della segreteria?",
            "Come contatto l'ufficio orientamento?",
            "Qual è l'email della segreteria studenti?",
            "Quali sono gli orari di apertura?",
            "Posso prendere un appuntamento con la segreteria?",
            "Chi chiamo per informazioni amministrative?",
            "C'è un numero verde?",
            "A chi scrivo per problemi tecnici?",
            "Dove trovo i contatti dei professori?",
            "La segreteria risponde al telefono?",
            "Qual è l'orario di ricevimento?",
            "Come parlo con un operatore?",
            "C'è uno sportello fisico?",
            "Posso mandare una PEC?",
            "Chi è il referente per la disabilità?"
        ],
        "mensa": [
            "Dove si trova la mensa?",
            "Quanto costa un pasto in mensa?",
            "Quali sono gli orari della mensa?",
            "Serve una tessera per la mensa?",
            "C'è un menu per celiaci?",
            "Posso mangiare in mensa la sera?",
            "La mensa è aperta il sabato?",
            "Dove ricarico il badge per la mensa?",
            "Ci sono alternative vegetariane?",
            "Chi può accedere alla mensa?",
            "C'è un bar nell'università?",
            "Posso portare il pranzo da casa?",
            "Dove sono i distributori automatici?",
            "Come accedo alle tariffe agevolate per la mensa?",
            "Qual è il menu di oggi?"
        ],
        "biblioteca": [
            "Dove è la biblioteca?",
            "Quali sono gli orari della biblioteca?",
            "Come prendo un libro in prestito?",
            "C'è un'aula studio?",
            "Posso studiare in biblioteca la sera?",
            "Come cerco un libro nel catalogo?",
            "La biblioteca è aperta nel weekend?",
            "Ci sono prese per il computer in biblioteca?",
            "Devo prenotare il posto in biblioteca?",
            "Posso stampare in biblioteca?",
            "Come rinnovo un prestito?",
            "C'è il wifi in biblioteca?",
            "Posso accedere alle risorse digitali da casa?",
            "Dove restituisco i libri?",
            "C'è una sala silenzio?"
        ],
        "alloggi": [
            "Ci sono dormitori universitari?",
            "Come faccio domanda per un alloggio?",
            "Quanto costa una stanza nello studentato?",
            "Dove cerco casa vicino all'università?",
            "Ci sono convenzioni per gli affitti?",
            "Quando esce il bando alloggi?",
            "Chi ha diritto all'alloggio?",
            "Gli alloggi sono misti?",
            "C'è una bacheca per gli annunci di affitto?",
            "Posso ospitare qualcuno nello studentato?",
            "Cosa è incluso nell'affitto dello studentato?",
            "Ci sono appartamenti per studenti disabili?",
            "Come rinuncio al posto alloggio?",
            "Dove si trovano le residenze universitarie?",
            "C'è un servizio di foresteria?"
        ],
        "irrelevant": [
            "Che tempo fa oggi?",
            "Chi ha vinto lo scudetto?",
            "Mi consigli una ricetta per la carbonara?",
            "Quanto dista la luna dalla terra?",
            "Qual è il miglior film del 2024?",
            "Come si cambia una ruota?",
            "Raccontami una barzelletta.",
            "Chi è il presidente degli Stati Uniti?",
            "Qual è la capitale della Francia?",
            "Come si fa il nodo alla cravatta?",
            "Cosa c'è stasera in TV?",
            "Mi consigli un ristorante cinese?",
            "Quanto costa un biglietto per il cinema?",
            "Come si cura il mal di gola?",
            "Qual è il significato della vita?",
            "Scrivimi una poesia.",
            "Chi ha scoperto l'America?",
            "Come si gioca a scacchi?",
            "Qual è il tuo colore preferito?",
            "Fai un salto.",
            "Genera un numero casuale.",
            "Parliamo di politica.",
            "Cosa ne pensi dell'intelligenza artificiale?",
            "Mi serve un idraulico.",
            "Dove posso comprare delle scarpe?",
            "Qual è la velocità della luce?",
            "Chi sono i Beatles?",
            "Come si pianta un albero?",
            "Perché il cielo è blu?",
            "Dimmi il tuo nome."
        ]
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Generating dataset with approximately {num_samples} samples...")

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question', 'label']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Generate base samples
        all_samples = []
        for label, questions in templates.items():
            for q in questions:
                all_samples.append({'question': q, 'label': label})
        
        # Augment data to reach num_samples
        # Simple augmentation: duplication (in a real scenario, use synonyms or paraphrasing)
        # Here we just repeat the list until we reach the desired count to ensure distribution
        
        generated_count = 0
        while generated_count < num_samples:
            random.shuffle(all_samples)
            for sample in all_samples:
                if generated_count >= num_samples:
                    break
                writer.writerow(sample)
                generated_count += 1

    print(f"Dataset generated at: {output_file}")
    print(f"Total samples: {generated_count}")

if __name__ == "__main__":
    output_path = os.path.join("data", "raw", "training_dataset.csv")
    # Generate a decent amount of data, e.g., 2000 rows
    generate_dataset(output_path, num_samples=2000)
