import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from src.backend.user_chart import get_all_registrations_per_week


def generate_plot():
    # Holen der aggregierten Registrierungsdaten (Liste von Tupeln: (Week, Total))
    data = get_all_registrations_per_week()

    # Erstelle ein DataFrame aus den Daten
    df = pd.DataFrame(data, columns=['Week', 'Total'])

    # Falls nötig, stelle sicher, dass die 'Week'-Spalte als Datetime interpretiert wird
    df['Week'] = pd.to_datetime(df['Week'])




    # Erstellen des Plots
    plt.figure(figsize=(10, 6))

    # Verwende formatierten Datumsstrings als x-Achse
    plt.bar(df['Week'].dt.strftime("%Y-%m-%d"), df['Total'], color='#0d94b0')

    plt.xlabel('Week (Monday)')
    plt.ylabel('Total Registered Users')
    plt.title('Registrations per Week')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Den Plot in einen BytesIO-Puffer speichern
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Den Puffer in einen Base64-String kodieren
    plot_data = base64.b64encode(buf.getvalue()).decode('utf8')

    return plot_data
