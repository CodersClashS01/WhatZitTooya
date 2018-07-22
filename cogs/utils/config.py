import asyncio
import json
from os.path import dirname, realpath, join


def check_config():
    join(dirname(realpath(dirname(__file__))), 'config.json')

    with open('config.json', 'r') as f:
        try:
            settings = json.load(f)
        except:
            settings = {}

    key_dict = {
        'token': 'Was ist dein Bot-Token? ',
        'prefix': 'Was soll der Präfix sein? ',
        'owner_id': 'Wir brauchen einen Owner. Gib bitte seine ID an: ',
        'bs_guild_id': 'Gib die ID der Gilde an, die für Schiffe Versenken verwendet werden soll. (siehe vorher Docs) ',
        'pg_user': 'Was ist dein PostgreSQL-Benutzername? ',
        'pg_pass': 'Was ist dein PostgreSQL-Passwort? ',
        'pg_db': 'Wie heißt die Datenbank zum Verbinden? ',
        'pg_host': 'Was ist die IP des Hosts der Datenbank? (Dieser Rechner = 127.0.0.1) ',
        'pg_port': 'Wie lautet der Connection-Port für PostgreSQL? (Standardport ist 5432) '
    }

    for key, value in key_dict.items():
        if key not in settings or len(settings.get(key)) == 0:
            settings[key] = input(value)

            with open('config.json', 'w') as f:
                asyncio.get_event_loop().run_in_executor(None, lambda: json.dump(settings, f, sort_keys=True, indent=4))