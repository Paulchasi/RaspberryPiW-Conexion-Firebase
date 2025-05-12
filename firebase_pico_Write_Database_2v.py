import network
import urequests as requests
import time
from machine import Pin, ADC

# Configuración WiFi
WIFI_SSID = 'PaulCh'
WIFI_PASSWORD = 'Paul1234'

# Configuración Firebase
FIREBASE_URL = 'https://maestria-iiot-rppico-default-rtdb.firebaseio.com/'
FIREBASE_API_KEY = 'AIzaSyCG9om499BzFsSaqWuJ4k6l-uE9r0-xWic'
FIREBASE_EMAIL = 'paulchasi@hotmail.com'
FIREBASE_PASSWORD = 'Paul2179'

# Configuración de hardware (ejemplo con sensor de temperatura interno)
#sensor_temp = ADC(4)  # Sensor de temperatura interno del Pico
#conversion_factor = 3.3 / (65535)  # Para convertir lectura ADC a voltaje

# Variables globales
id_token = None
contador = 0

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

def leer_temperatura():
    lectura = 63#sensor_temp.read_u16() * conversion_factor
    temperatura = 27 - (lectura - 0.706)/0.001721  # Fórmula para temperatura del Pico
    return round(temperatura, 2)

def actualizar_firebase():
    global contador
    contador += 1
    temperatura_actual = leer_temperatura()
    
    datos_actualizar = {
        "data": contador,
        "temperatura": temperatura_actual
    }
    
    url = f"{FIREBASE_URL}random.json?auth={id_token}"
    
    try:
        response = requests.patch(url, json=datos_actualizar)
        if response.status_code == 200:
            print("\n" + "═"*40)
            print("🔥 Datos actualizados en Firebase")
            print(f"🆕 Data: {contador}")
            print(f"🌡 Temperatura: {temperatura_actual}°C")
            print("═"*40)
            return True
        print(f"❌ Error al actualizar (HTTP {response.status_code}):", response.text)
        return False
    except Exception as e:
        print("❌ Error de conexión:", str(e))
        return False
    finally:
        if 'response' in locals():
            response.close()

def main():
    connect_wifi()
    
    if not firebase_auth():
        print("⚠️ No se puede continuar sin autenticación")
        return
    
    print("\n🔄 Iniciando actualización de Firebase...")
    while True:
        actualizar_firebase()
        time.sleep(10)  # Actualiza cada 5 segundos

if __name__ == "__main__":
    main()