import json
import os
import subprocess
import shlex
import time
import signal

SOURCE_ROOT = os.path.join(os.path.abspath('.'), 'bin')
TUNNEL_CORE = os.path.join(SOURCE_ROOT, 'darwin', 'psiphon-tunnel-core-x86_64')
CONFIG_FILE_NAME = os.path.join(SOURCE_ROOT, 'tunnel-core-config.config')



def __test_tunnel_core(propagation_channel_id, target_server, tunnel_protocol, sponsor_id):

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

    cmd = '"%s" \
    --config \
    "%s"' \
    % (TUNNEL_CORE, CONFIG_FILE_NAME)

    try:

        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # TODO: Kill Process or stop Tunnel Core.
        # time.sleep(20)

        # try:
        #     proc.send_signal(signal.SIGINT)
        #     # proc.kill()
        # except OSError, e:
        #     print("Kill Error")

        output = proc.communicate()[1] # return the command output

        if proc.returncode != 0:
            raise Exception('Tunnel Core Testing Fail: ' + str(output))

    finally:
        # pass
        if '"count":1' in output:
            print "PASS"
        else:
            print "FAIL"
        os.remove(CONFIG_FILE_NAME)


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
