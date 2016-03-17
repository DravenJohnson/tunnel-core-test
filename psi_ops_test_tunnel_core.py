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

CHECK_IP_ADDRESS_URL_REMOTE = run.CHECK_IP_ADDRESS_URL_REMOTE

def __test_tunnel_core(transport, encoded_server_list, expected_egress_ip_addresses, test_propagation_channel_id = '0'):

    has_remote_check = len(CHECK_IP_ADDRESS_URL_REMOTE) > 0

    config = {
        "TargetServerEntry": encoded_server_list, # Single Test Server Parameter
        "TunnelProtocol": transport, # Single or group Test Protocol
        "PropagationChannelId" : test_propagation_channel_id, # Propagation Channel ID = "Testing"
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

    cmd = 'cmd.exe /c start "%s" \
    --config \
    "%s"' \
    % (TUNNEL_CORE, CONFIG_FILE_NAME)

    print 'Start Testing Server "%s" with Protocol "%s"' % (expected_egress_ip_addresses,transport)

    try:

        proc = subprocess.Popen(shlex.split(cmd))

        time.sleep(5)

        # if proc.returncode != 0:
        #     raise Exception('Tunnel Core Testing Fail')

        #TODO: add check proxy part
        urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': '127.0.0.1:8080'})))

        if has_remote_check:
            # Get egress IP from web site in different GeoIP region; remote split tunnel is proxied

            egress_ip_address = urllib2.urlopen(CHECK_IP_ADDRESS_URL_REMOTE).read().split('\n')[0]

            is_proxied = (egress_ip_address in expected_egress_ip_addresses)

            if not is_proxied:
                raise Exception('Remote case: egress is %s and expected egresses are %s' % (
                                    egress_ip_address, ','.join(expected_egress_ip_addresses)))
            else:
                # Just for test
                print egress_ip_address

    finally:
        try:
            win32ui.FindWindow(None, TUNNEL_CORE).PostMessage(win32con.WM_CLOSE)
        except Exception as e:
            print e
        try:
            os.remove(CONFIG_FILE_NAME)
        except Exception as e:
            print "Remove Config File Failed" + str(e)
