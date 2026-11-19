from flask import Flask, jsonify, render_template, request
from netmiko import ConnectHandler

app = Flask(__name__)

# Credentials stay on the server. The browser never sees them.
USERNAME = "admin"
PASSWORD = "eve123"
SECRET = "eve123"

DEFAULTS = {"ip": "192.168.10.103", "port": 32770}
COMMANDS = ["show version", "show ip interface brief", "show running-config"]

DEMO_OUTPUT = {
    "show version": "Cisco IOS Software, 3700 Software (C3725-ADVENTERPRISEK9-M), Version 12.4(15)T14\nROM: ROMMON Emulation Microcode\nR1 uptime is 15 minutes",
    "show ip interface brief": (
        "Interface            IP-Address      OK? Method Status                Protocol\n"
        "FastEthernet0/0      192.168.1.1     YES NVRAM  up                    up\n"
        "FastEthernet0/1      192.168.10.50   YES manual up                    up\n"
        "FastEthernet1/0      unassigned      YES NVRAM  administratively down down"
    ),
    "show running-config": "Building configuration...\n\nhostname R1\n!\nusername admin privilege 15 secret 5 $1$...\n!\nline vty 0 4\n login local\n transport input telnet",
}


@app.route("/")
def index():
    return render_template("index.html", defaults=DEFAULTS, commands=COMMANDS)


@app.route("/api/run", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}

    if data.get("demo"):
        return jsonify(ok=True, results=[{"command": c, "output": DEMO_OUTPUT[c]} for c in COMMANDS])

    try:
        port = int(data.get("port", DEFAULTS["port"]))
    except (TypeError, ValueError):
        return jsonify(ok=False, error="Port must be a number."), 400

    device = {
        "device_type": "cisco_ios_telnet",
        "ip": str(data.get("ip", DEFAULTS["ip"])).strip(),
        "port": port,
        "username": USERNAME,
        "password": PASSWORD,
        "secret": SECRET,
        "global_delay_factor": 2,
    }

    try:
        conn = ConnectHandler(**device)
        conn.enable()
        results = [{"command": c, "output": conn.send_command(c)} for c in COMMANDS]
        conn.disconnect()
        return jsonify(ok=True, results=results)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 502


if __name__ == "__main__":
    app.run(port=5001, debug=True)