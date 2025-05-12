import network
import urequests as requests
import time
from machine import Pin

# Configuración WiFi 
WIFI_SSID = 'PaulCh'
WIFI_PASSWORD = 'Paul1234'

# Configuración Firebase
FIREBASE_URL = 'https://maestria-iiot-rppico-default-rtdb.firebaseio.com/'
FIREBASE_API_KEY = 'AIzaSyCG9om499BzFsSaqWuJ4k6l-uE9r0-xWic'
FIREBASE_EMAIL = 'paulchasi@hotmail.com'
FIREBASE_PASSWORD = 'Paul2179'

# Variables globales
id_token = None

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(15):
            if wlan.isconnected():
                break
            time.sleep(1)
        if not wlan.isconnected():
            raise RuntimeError("Error de conexión WiFi")
    print("✅ WiFi conectado")
    print("📶 IP:", wlan.ifconfig()[0])

def firebase_auth():
    global id_token
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    auth_data = {
        "email": FIREBASE_EMAIL,
        "password": FIREBASE_PASSWORD,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        if response.status_code == 200:
            id_token = response.json()['idToken']
            print("🔑 Autenticación exitosa con Firebase")
            return True
        print(f"❌ Error de autenticación (HTTP {response.status_code}):", response.text)
        return False
    except Exception as e:
        print("❌ Error en auth:", str(e))
        return False
    finally:
        if 'response' in locals():
            response.close()

def read_firebase_data():
    url = f"{FIREBASE_URL}random.json?auth={id_token}"  # Lee todo el nodo random
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Visualización mejorada
            print("\n" + "═"*35)
            print("📊 DATOS DE FIREBASE")
            print("═"*35)
            print(f"🔢 Data: {data.get('data', 'N/D')}")
            print(f"🌡 Temperatura: {data.get('temperatura', 'N/D')}°C")
            print("═"*35)
            
            return data
        print(f"❌ Error de lectura (HTTP {response.status_code}):", response.text)
        return None
    except Exception as e:
        print("❌ Error de conexión:", str(e))
        return None
    finally:
        if 'response' in locals():
            response.close()

def main():
    connect_wifi()
    
    if not firebase_auth():
        print("⚠️ No se puede continuar sin autenticación")
        return
    
    print("\n🔄 Iniciando monitoreo de Firebase...")
    while True:
        read_firebase_data()
        time.sleep(10)  # Lectura cada 3 segundos

if __name__ == "__main__":
    main()