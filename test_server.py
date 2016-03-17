import json
import os
import subprocess
import shlex
import time
import signal
import run
import win32ui
import win32con
import urllib2

SOURCE_ROOT = os.path.join(os.path.abspath('.'), 'bin')
TUNNEL_CORE = os.path.join(SOURCE_ROOT, 'windows', 'psiphon-tunnel-core-i686.exe')
CONFIG_FILE_NAME = os.path.join(SOURCE_ROOT, 'tunnel-core-config.config')

'''
Nothing changed
'''
class PsiphonRunner:
    def __init__(self, encoded_server_entry,  executable_path):
        self.proc = None
        self.executable_path = executable_path
        self.encoded_server_entry = encoded_server_entry

    def connect_to_server(self, transport, split_tunnel_mode):
        self.servers_registry_value = 'Servers' + transport

        # Currently, tunnel-core will try to establish a connection on OSSH,SSH,MEEK
        # ports. The SSH registry value is overlooked. This forces the registry
        # value that is set SSH connections.
        if transport == 'SSH':
            self.servers_registry_value = 'ServersOSSH'

        # Internally we refer to "OSSH", but the display name is "SSH+", which is also used
        # in the registry setting to control which transport is used.
        if transport == 'OSSH':
            transport = 'SSH+'

        self.transport_value, self.transport_type = None, None
        self.split_tunnel_value, self.split_tunnel_type = None, None
        self.servers_value, self.servers_type = None, None
        reg_key = _winreg.OpenKey(REGISTRY_ROOT_KEY, REGISTRY_PRODUCT_KEY, 0, _winreg.KEY_ALL_ACCESS)
        transport_value, transport_type = _winreg.QueryValueEx(reg_key, REGISTRY_TRANSPORT_VALUE)
        _winreg.SetValueEx(reg_key, REGISTRY_TRANSPORT_VALUE, None, _winreg.REG_SZ, transport)
        split_tunnel_value, split_tunnel_type = _winreg.QueryValueEx(reg_key, REGISTRY_SPLIT_TUNNEL_VALUE)
        # Enable split tunnel with registry setting
        _winreg.SetValueEx(reg_key, REGISTRY_SPLIT_TUNNEL_VALUE, None, _winreg.REG_DWORD, 1 if split_tunnel_mode else 0)
        servers_value, servers_type = _winreg.QueryValueEx(reg_key, servers_registry_value)
        _winreg.SetValueEx(reg_key, servers_registry_value, None, _winreg.REG_SZ, '\n'.join(encoded_server_list))
        # Move appdata to clear it
        if os.path.exists(APPDATA_BACKUP_DIR):
            shutil.rmtree(APPDATA_BACKUP_DIR)
        os.rename(APPDATA_DIR, APPDATA_BACKUP_DIR)

        self.proc = subprocess.Popen([self.executable_path])

    def stop_psiphon(self):
        if self.transport_type and self.transport_value:
            _winreg.SetValueEx(reg_key, REGISTRY_TRANSPORT_VALUE, None, transport_type, transport_value)
        if self.split_tunnel_value and self.split_tunnel_type:
            _winreg.SetValueEx(reg_key, REGISTRY_SPLIT_TUNNEL_VALUE, None, split_tunnel_type, split_tunnel_value)
        if self.servers_type and self.servers_value:
            _winreg.SetValueEx(reg_key, servers_registry_value, None, servers_type, servers_value)
        try:
            win32ui.FindWindow(None, psi_ops_build_windows.APPLICATION_TITLE).PostMessage(win32con.WM_CLOSE)
        except Exception as e:
            print e
        if self.proc:
            self.proc.wait()
        # Restore appdata
        if os.path.exists(APPDATA_BACKUP_DIR):
            if os.path.exists(APPDATA_DIR):
                shutil.rmtree(APPDATA_DIR)
            os.rename(APPDATA_BACKUP_DIR, APPDATA_DIR)

'''
Tunnel Core Runner Class: Done
'''
class TunnelCoreRunner:
    def __init__(self, encoded_server_entry, propagation_channel_id = '0'):
        self.proc = None
        self.encoded_server_entry = encoded_server_entry
        self.propagation_channel_id = propagation_channel_id

    # Setup and create tunnel core config file.
    def _setup_tunnel_config(self, transport):
        config = {
            "TargetServerEntry": self.encoded_server_entry, # Single Test Server Parameter
            "TunnelProtocol": transport, # Single or group Test Protocol
            "PropagationChannelId" : self.propagation_channel_id, # Propagation Channel ID = "Testing"
            "SponsorId" : "0",
            "LocalHttpProxyPort" : 8080,
            "LocalSocksProxyPort" : 1080,
            "UseIndistinguishableTLS": True,
            "TunnelPoolSize" : 1,
            "ConnectionWorkerPoolSize" : 1,
            "PortForwardFailureThreshold" : 5
        }

        with open(CONFIG_FILE_NAME, 'w+') as config_file:
            json.dump(config, config_file)

    # Use the config file and tunnel core it self to connect to server
    def connect_to_server(self, transport, split_tunnel_mode = False):

        self._setup_tunnel_config(transport)

        cmd = 'cmd.exe /c start "%s" \
        --config \
        "%s"' \
        % (TUNNEL_CORE, CONFIG_FILE_NAME)

        self.proc = subprocess.Popen(shlex.split(cmd))

    def stop_psiphon(self):
        try:
            win32ui.FindWindow(None, TUNNEL_CORE).PostMessage(win32con.WM_CLOSE)
        except Exception as e:
            print e
        if self.proc:
           self.proc.wait()
        # Remove Config file
        try:
            os.remove(CONFIG_FILE_NAME)
        except Exception as e:
            print "Remove Config File Failed" + str(e)

'''
Nothing changed
'''
# @retry_on_exception_decorator
def __test_server(psiphon_runner, transport, expected_egress_ip_addresses):
    # test:
    # - spawn client process, which starts the VPN
    # - sleep 5 seconds, which allows time to establish connection
    # - determine egress IP address and assert it matches host IP address
    # - post WM_CLOSE to gracefully shut down the client and its connection

    has_remote_check = len(CHECK_IP_ADDRESS_URL_REMOTE) > 0
    has_local_check = len(CHECK_IP_ADDRESS_URL_LOCAL) > 0

    # Split tunnelling is not implemented for VPN.
    # Also, if there is no remote check, don't use split tunnel mode because we always want
    # to test at least one proxied case.

    if transport == 'VPN' or not has_remote_check:
        split_tunnel_mode = False
    else:
        split_tunnel_mode = random.choice([True, False])

    print 'Testing egress IP addresses %s in %s mode (split tunnel %s)...' % (
            ','.join(expected_egress_ip_addresses), transport, 'ENABLED' if split_tunnel_mode else 'DISABLED')

    try:

        runner.connect_to_server(transport, split_tunnel_mode)

        time.sleep(25)

        # In VPN mode, all traffic is routed through the proxy. In SSH mode, the
        # urlib2 ProxyHandler picks up the Windows Internet Settings and uses the
        # HTTP Proxy that is set by the client.
        urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler()))

        if has_local_check:
            # Get egress IP from web site in same GeoIP region; local split tunnel is not proxied

            egress_ip_address = urlopen(CHECK_IP_ADDRESS_URL_LOCAL, 30).read().split('\n')[0]

            is_proxied = (egress_ip_address in expected_egress_ip_addresses)

            if (transport == 'VPN' or not split_tunnel_mode) and not is_proxied:
                raise Exception('Local case/VPN/not split tunnel: egress is %s and expected egresses are %s' % (
                                    egress_ip_address, ','.join(expected_egress_ip_addresses)))

            if transport != 'VPN' and split_tunnel_mode and is_proxied:
                raise Exception('Local case/not VPN/split tunnel: egress is %s and expected egresses are ANYTHING OTHER THAN %s' % (
                                    egress_ip_address, ','.join(expected_egress_ip_addresses)))

        if has_remote_check:
            # Get egress IP from web site in different GeoIP region; remote split tunnel is proxied

            egress_ip_address = urlopen(CHECK_IP_ADDRESS_URL_REMOTE, 30).read().split('\n')[0]

            is_proxied = (egress_ip_address in expected_egress_ip_addresses)

            if not is_proxied:
                raise Exception('Remote case: egress is %s and expected egresses are %s' % (
                                    egress_ip_address, ','.join(expected_egress_ip_addresses)))

    finally:

        runner.stop_psiphon()
