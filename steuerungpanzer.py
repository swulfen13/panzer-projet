import asyncio
import sys
import subprocess

#  Automatische Installation fehlender Bibliotheken
REQUIRED_LIBRARIES = ["bleak", "keyboard"]
for lib in REQUIRED_LIBRARIES:
    try:
        __import__(lib)
    except ImportError:
        print(f" Installiere {lib}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import keyboard
from bleak import BleakClient, BleakScanner

#  UUID für LEGO SPIKE Bluetooth-Kommunikation
SPIKE_UART_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

#  Geschwindigkeit für Hub 1
SPEED = 50


# Funktion zum Senden von Befehlen an einen Hub
async def send_command(mac_address, command):
    async with BleakClient(mac_address) as client:
        if await client.is_connected():
            print(f" Sende an {mac_address}: {command}")
            await client.write_gatt_char(SPIKE_UART_UUID, command.encode() + b"\n")


#  Funktion zum Finden der MAC-Adresse eines SPIKE Hubs
async def find_spike_hubs():
    print(" Suche nach SPIKE Hubs...")
    devices = await BleakScanner.discover()
    for device in devices:
        if "LEGO" in (device.name or "") or "SPIKE" in (device.name or ""):
            print(f" Gefunden: {device.name} - MAC-Adresse: {device.address}")


#  Steuerung für Hub 1 mit WASD (Spielmodus)
async def control_hub_1(hub_1_mac):
    print(" Steuerung für Hub 1 gestartet! (W = Vorwärts, S = Rückwärts, A = Links, D = Rechts, Q = Stop)")

    while True:
        if keyboard.is_pressed("w"):  # Vorwärts
            await send_command(hub_1_mac, f"motor.run('A', {SPEED}); motor.run('B', {SPEED})")
        elif keyboard.is_pressed("s"):  # Rückwärts
            await send_command(hub_1_mac, f"motor.run('A', {-SPEED}); motor.run('B', {-SPEED})")
        elif keyboard.is_pressed("a"):  # Links drehen
            await send_command(hub_1_mac, f"motor.run('A', {-SPEED}); motor.run('B', {SPEED})")
        elif keyboard.is_pressed("d"):  # Rechts drehen
            await send_command(hub_1_mac, f"motor.run('A', {SPEED}); motor.run('B', {-SPEED})")
        elif keyboard.is_pressed("q"):  # Stoppen
            await send_command(hub_1_mac, "motor.stop('A'); motor.stop('B')")

        await asyncio.sleep(0.1)  # Kurze Pause für CPU-Schonung


#  Steuerung für Hub 2 (Hier kannst du eigene Befehle setzen)
async def control_hub_2(hub_2_mac):
    print("⚙ Starte Hub 2 (frei programmierbar)")
    await asyncio.sleep(2)  # Kleiner Start-Delay

    #  Hier kannst du eigene Befehle setzen!
    await send_command(hub_2_mac, "motor.run('C', 75)")  # Beispiel: Motor C mit 75% Leistung starten
    await asyncio.sleep(3)  # Wartezeit
    await send_command(hub_2_mac, "motor.stop('C')")  # Motor C stoppen


#  Hauptprogramm: Erst MAC-Adressen scannen, dann Steuerung starten
async def main():
    await find_spike_hubs()  # Erst nach SPIKE Hubs suchen
    hub_1_mac = input(" Gib die MAC-Adresse für Hub 1 ein (WASD-Steuerung): ")
    hub_2_mac = input(" Gib die MAC-Adresse für Hub 2 ein (frei programmierbar): ")

    await asyncio.gather(
        control_hub_1(hub_1_mac),  # Steuerung für Hub 1
        control_hub_2(hub_2_mac)  # Eigene Steuerung für Hub 2
    )


#  Starte das Programm
asyncio,run(main())
