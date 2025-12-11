import os
import random
import psycopg2
from faker import Faker
from datetime import datetime, timedelta

def get_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            # Fallback to individual variables if DATABASE_URL is not set
            DB_HOST = os.getenv("DB_HOST", "localhost")
            DB_NAME = os.getenv("POSTGRES_DB", "postgres")
            DB_USER = os.getenv("POSTGRES_USER", "postgres")
            DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
            DB_PORT = os.getenv("DB_PORT", "5432")
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                port=DB_PORT
            )
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def seed_data():
    conn = get_connection()
    if not conn:
        return

    cur = conn.cursor()
    fake = Faker('it_IT')

    print("Inizio seeding dati...")

    # 1. Pulisci tabelle (ordine inverso per FK)
    cur.execute("TRUNCATE esami, appelli, insegnamenti, studenti, corsi_laurea RESTART IDENTITY CASCADE;")
    
    # 2. Corsi di Laurea UnivPM (Reali/Simili)
    corsi = [
        ('L-8', 'Ingegneria Informatica e dell\'Automazione', 'Triennale'),
        ('L-9', 'Ingegneria Gestionale', 'Triennale'),
        ('LM-32', 'Computer and Automation Engineering', 'Magistrale'),
        ('LM-DATA', 'Data Science for Economics and Business', 'Magistrale'),
    ]
    
    corsi_ids = []
    for cod, nome, tipo in corsi:
        cur.execute(
            "INSERT INTO corsi_laurea (codice, nome, tipo_laurea, descrizione) VALUES (%s, %s, %s, %s) RETURNING id;",
            (cod, nome, tipo, f"Corso di laurea in {nome}")
        )
        corsi_ids.append(cur.fetchone()[0])
    
    print(f"Inseriti {len(corsi_ids)} corsi di laurea.")

    # 3. Insegnamenti (Un sottoinsieme verosimile)
    materie_base = ["Analisi Matematica 1", "Fisica 1", "Fondamenti di Informatica", "Inglese"]
    materie_spec = ["Basi di Dati", "Sistemi Operativi", "Machine Learning", "Ricerca Operativa", "Economia Aziendale"]
    
    insegnamenti_ids = []
    for i, cid in enumerate(corsi_ids):
        # Aggiungi materie base a tutti
        for m in materie_base:
            codice = f"MAT-{random.randint(100,999)}"
            cur.execute(
                "INSERT INTO insegnamenti (codice, nome, cfu, anno_corso, semestre, corso_laurea_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (codice, m, random.choice([6, 9, 12]), 1, random.choice([1,2]), cid)
            )
            insegnamenti_ids.append(cur.fetchone()[0])
            
        # Aggiungi materie specifiche
        for m in materie_spec:
            codice = f"SPEC-{random.randint(100,999)}"
            cur.execute(
                "INSERT INTO insegnamenti (codice, nome, cfu, anno_corso, semestre, corso_laurea_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (codice, m, random.choice([6, 9]), random.choice([2,3]), random.choice([1,2]), cid)
            )
            insegnamenti_ids.append(cur.fetchone()[0])

    print(f"Inseriti insegnamenti.")

    # 4. Studenti (500)
    studenti_ids = []
    num_studenti = 500
    # Genera matricole univoche
    matricole_pool = random.sample(range(100000, 999999), num_studenti)
    
    for i in range(num_studenti):
        cid = random.choice(corsi_ids)
        matricola = f"S{matricole_pool[i]}"
        
        cur.execute(
            "INSERT INTO studenti (matricola, nome, cognome, email, data_nascita, corso_laurea_id, anno_iscrizione) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (
                matricola, 
                fake.first_name(), 
                fake.last_name(), 
                fake.unique.email(),  # Ensure unique email as well
                fake.date_of_birth(minimum_age=19, maximum_age=30),
                cid,
                random.randint(2020, 2024)
            )
        )
        studenti_ids.append(cur.fetchone()[0])

    print(f"Inseriti {num_studenti} studenti.")
    
    # 5. Appelli ed Esami
    # Per ogni insegnamento creiamo degli appelli nel passato
    for ins_id in insegnamenti_ids:
        for _ in range(3): # 3 appelli per materia
            data_appello = fake.date_between(start_date='-2y', end_date='today')
            cur.execute(
                "INSERT INTO appelli (insegnamento_id, data_appello, aula) VALUES (%s, %s, %s) RETURNING id;",
                (ins_id, data_appello, f"Aula {random.choice(['A', 'B', 'C'])}{random.randint(1,5)}")
            )
            appello_id = cur.fetchone()[0]

            # Iscriviamo casualmente degli studenti a questo appello
            num_iscritti = random.randint(5, 50)
            iscritti = random.sample(studenti_ids, min(num_iscritti, len(studenti_ids)))
            
            for stud_id in iscritti:
                # Generiamo voto
                voto = random.randint(15, 31) # 15-17 bocciati, 18-30 promossi, 31 lode
                stato = 'SUPERATO'
                lode = False
                
                if voto < 18:
                    stato = 'RESPINTO'
                    final_voto = 0 # O mantieni il voto insuff per statistiche
                elif voto == 31:
                    final_voto = 30
                    lode = True
                else:
                    final_voto = voto
                
                try:
                    cur.execute(
                        "INSERT INTO esami (studente_id, appello_id, voto, lode, stato) VALUES (%s, %s, %s, %s, %s);",
                        (stud_id, appello_id, final_voto, lode, stato)
                    )
                except psycopg2.IntegrityError:
                    conn.rollback() # Skip duplicati
                    continue
                conn.commit()

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding completato con successo!")

if __name__ == "__main__":
    seed_data()
