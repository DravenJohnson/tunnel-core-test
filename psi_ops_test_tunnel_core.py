import json
import os
import subprocess
import shlex
import time
import signal
import run
import win32ui
import win32con

SOURCE_ROOT = os.path.join(os.path.abspath('.'), 'bin')
TUNNEL_CORE = os.path.join(SOURCE_ROOT, 'windows', 'psiphon-tunnel-core-i686.exe')
CONFIG_FILE_NAME = os.path.join(SOURCE_ROOT, 'tunnel-core-config.config')

CHECK_IP_ADDRESS_URL_LOCAL = run.CHECK_IP_ADDRESS_URL_LOCAL
CHECK_IP_ADDRESS_URL_REMOTE = run.CHECK_IP_ADDRESS_URL_REMOTE


def __test_tunnel_core(expected_egress_ip_addresses, propagation_channel_id, target_server, tunnel_protocol, sponsor_id):

    has_remote_check = len(CHECK_IP_ADDRESS_URL_REMOTE) > 0
    has_local_check = len(CHECK_IP_ADDRESS_URL_LOCAL) > 0

    config = {
        "TargetServerEntry": target_server, # Single Test Server Parameter
        "TunnelProtocol": tunnel_protocol, # Single or group Test Protocol
        "EgressRegion" : "",
        "PropagationChannelId" : propagation_channel_id,
        "SponsorId" : sponsor_id,
        # "RemoteServerListUrl" : "",
        # "RemoteServerListSignaturePublicKey" : "",
        "LogFilename" : "",
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

    print 'Start Testing Server "%s" with Protocol "%s"' % (expected_egress_ip_addresses, tunnel_protocol)

    try:

        proc = subprocess.Popen(shlex.split(cmd))

        time.sleep(25)

        # if proc.returncode != 0:
        #     raise Exception('Tunnel Core Testing Fail')

        #TODO: add check proxy part
        urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': 'http://127.0.0.1:8080'})))

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
        try:
            win32ui.FindWindow(None, TUNNEL_CORE).PostMessage(win32con.WM_CLOSE)
        except Exception as e:
            print e
        try:
            os.remove(CONFIG_FILE_NAME)
        except Exception as e:
            print "Remove Config File Failed" + str(e)


# Haven't Test this part yet
def test_server(ip_address, capabilities, web_server_port, web_server_secret, encoded_server_list,
                split_tunnel_url_format, split_tunnel_signature_public_key, split_tunnel_dns_server, version,
                expected_egress_ip_addresses, test_propagation_channel_id = '0', test_cases = None, executable_path = None):

    for test_case in local_test_cases:
        if test_case in ['OSSH', 'SSH', 'HTTP', 'HTTPS']:
            try:
                result = __test_tunnel_conre(test_propagation_channel_id, encoded_server_list, test_cases, sponsor_id)
                results[test_case] = 'PASS' if result else 'FAIL'
            except Exception as ex:
                results[test_case] = 'FAIL: ' + str(ex)
