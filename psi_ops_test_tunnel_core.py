import json
import os
import subprocess
import shlex


SOURCE_ROOT = os.path.join(os.path.abspath('../..'), 'psiphon-tunnel-core', 'ConsoleClient')
TUNNEL_CORE = os.path.join(SOURCE_ROOT, 'bin', 'darwin', 'psiphon-tunnel-core-x86_64')
CONFIG_FILE_NAME = os.path.join(SOURCE_ROOT, 'tunnel-core-config.config')



def __test_tunnel_conre(propagation_channel_id, target_server, tunnel_protocol):

    config = {
        "TargetServerEntry": target_server, # Single Test Server Parameter
        "TunnelProtocol": tunnel_protocol, # Single or group Test Protocol
        "EgressRegion" : "",
        "PropagationChannelId" : propagation_channel_id,
        "SponsorId" : "",
        "RemoteServerListUrl" : "",
        "RemoteServerListSignaturePublicKey" : "",
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

    cmd = '%s --config %s ' % (TUNNEL_CORE, CONFIG_FILE_NAME)

    try:

        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate() # return the command output

    finally:
        pass
        # os.remove(CONFIG_FILE_NAME)


def test_server(ip_address, capabilities, web_server_port, web_server_secret, encoded_server_list,
                split_tunnel_url_format, split_tunnel_signature_public_key, split_tunnel_dns_server, version,
                expected_egress_ip_addresses, test_propagation_channel_id = '0', test_cases = None, executable_path = None):

    for test_case in local_test_cases:
        if test_case in ['OSSH', 'SSH', 'HTTP', 'HTTPS']:
            try:
                result = self.__test_tunnel_conre()
                results[test_case] = 'PASS' if result else 'FAIL'
            except Exception as ex:
                results[test_case] = 'FAIL: ' + str(ex)
