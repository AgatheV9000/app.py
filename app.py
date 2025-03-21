import folium
from flask import Flask, render_template, request, url_for

app = Flask(__name__, template_folder="templates")

locations = {
    "Gare de Calais Fréthun": (50.928, 1.809),
    "Gare de Calais Ville": (50.951, 1.858),
    "Université du Littoral Côte d'Opale": (50.960, 1.845)
}

transport_times = {
    "train": (10, "purple", "2,2"),
    "bus": (15, "orange", "8,2"),
    "pied": (30, "green", "10,5"),
    "vol_oiseau": (5, "blue", "5")
}

@app.route('/')
def home():
    return "Bienvenue sur ma page d'accueil !"

@app.route('/calcul', methods=['GET', 'POST'])
def calculette():
    result = None
    if request.method == 'POST':
        try:
            num1 = float(request.form['num1'])
            num2 = float(request.form['num2'])
            operation = request.form['operation']

            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                result = num1 / num2 if num2 != 0 else "Erreur : Division par zéro"
            else:
                result = "Erreur : Opération inconnue"

        except ValueError:
            result = "Erreur : Entrée invalide"

    return render_template('about.html', result=result)

@app.route('/about', methods=['GET', 'POST'])
def about():
    trajet_temps = ""
    polyline_train = None
    polyline_bus = None
    polyline_pied = None
    polyline_vol_oiseau = None

    if request.method == 'POST':
        m = folium.Map(location=[50.945, 1.85], zoom_start=12)

        colors = ["red", "purple", "green"]
        for (name, coord), color in zip(locations.items(), colors):
            folium.Marker(coord, popup=name, icon=folium.Icon(color=color)).add_to(m)

        trajet = [locations["Gare de Calais Fréthun"],
                  locations["Gare de Calais Ville"],
                  locations["Université du Littoral Côte d'Opale"]]

        folium.PolyLine([trajet[0], trajet[1]], color="purple", weight=5, popup="Train ~10 min").add_to(m)
        folium.PolyLine([trajet[1], trajet[2]], color="purple", weight=5, popup="Train ~10 min").add_to(m)

        destination = request.form.get('destination')
        mode = request.form.get('mode', 'train')

        if destination and destination in locations:
            lat_dest, lon_dest = locations[destination]
            folium.Marker([lat_dest, lon_dest], popup=destination, icon=folium.Icon(color="red")).add_to(m)

            if mode in transport_times:
                time, color, dash = transport_times[mode]

                if mode == "bus":
                    if polyline_bus:
                        m.remove_children(polyline_bus)
                    polyline_bus = folium.PolyLine([trajet[1], trajet[2]], color="orange", weight=5, dash_array="8,2", popup="Bus ~15 min").add_to(m)
                    trajet_temps = "Train (Fréthun → Ville) : ~10 min\nBus (Ville → ULCO) : ~15 min"
                elif mode == "pied":
                    if polyline_pied:
                        m.remove_children(polyline_pied)
                    polyline_pied = folium.PolyLine([trajet[1], trajet[2]], color="green", weight=5, dash_array="10,5", popup="Marche ~30 min").add_to(m)
                    trajet_temps = "Train (Fréthun → Ville) : ~10 min\nMarche (Ville → ULCO) : ~30 min"
                elif mode == "vol_oiseau":
                    if polyline_vol_oiseau:
                        m.remove_children(polyline_vol_oiseau)
                    polyline_vol_oiseau = folium.PolyLine([trajet[1], trajet[2]], color="blue", weight=5, dash_array="5", popup="Vol d'oiseau").add_to(m)
                    trajet_temps = "Train (Fréthun → Ville) : ~10 min\nVol d'oiseau (Ville → ULCO)"
                elif mode == "trajet_complet":
                    folium.PolyLine([trajet[0], trajet[1]], color="purple", weight=5, popup="Train ~10 min").add_to(m)
                    folium.PolyLine([trajet[1], trajet[2]], color="orange", weight=5, dash_array="8,2", popup="Bus ~15 min").add_to(m)
                    trajet_temps = "Train (Fréthun → Ville) : ~10 min\nBus (Ville → ULCO) : ~15 min"

        m.save('static/map.html')
        return render_template('about.html', trajet_temps=trajet_temps, map_html=url_for('static', filename='map.html'))

    return render_template('about.html', map_html=url_for('static', filename='map.html'))

if __name__ == '__main__':
    app.run(debug=True)