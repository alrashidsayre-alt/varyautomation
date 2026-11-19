from netmiko import ConnectHandler

router_device = {
    'device_type': 'cisco_ios_telnet',
    'ip': '192.168.10.103',
    'port': 32770,
    'username': 'admin',
    'password': 'eve123',
    'secret': 'eve123',
}   

try:
    print("Connecting to the router...")
    net_connect = ConnectHandler(**router_device)

    net_connect.enable()

    commands_to_run = [
        "show version",
        "show ip interface brief",
        "show running-config"
    ]

    for cmd in commands_to_run:
        output = net_connect.send_command(cmd)
        print(f"Output of '{cmd}':\n{output}\n")

    net_connect.disconnect()
    print("\nDisconnected successfully.")
except Exception as e:
    print(f"Connection failed: {e}")