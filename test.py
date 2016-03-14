import psi_ops_test_tunnel_core

def test_test_server(self, server, test_cases, version, test_propagation_channel_id, executable_path=None):
    return psi_ops_test_tunnel_core.test_server(
                                server.ip_address,
                                server.capabilities,
                                server.web_server_port,
                                server.web_server_secret,
                                [self.__get_encoded_server_entry(server)],
                                self.__split_tunnel_url_format(),
                                self.__split_tunnel_signature_public_key(),
                                self.__split_tunnel_dns_server(),
                                version,
                                [server.egress_ip_address],
                                test_propagation_channel_id,
                                test_cases,
                                executable_path)


def test_test_tunnel_core(propagation_channel_id, target_server, tunnel_protocol, sponsor_id):
    return psi_ops_test_tunnel_core.__test_tunnel_conre(propagation_channel_id, target_server, tunnel_protocol, sponsor_id)
