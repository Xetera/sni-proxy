from typing import Iterable
from mitmproxy import tls, http, connection, addonmanager
from mitmproxy.addons.tlsconfig import TlsConfig
from mitmproxy.http import HTTPFlow
import yaml


def matches_any(domains: Iterable[str], domain: str) -> bool:
    return any(to_unblock in domain for to_unblock in domains)


class SNIProxy:
    config = TlsConfig()
    sni: str
    domains: Iterable[str]
    delicate_domains: Iterable[str]

    def load(self, _loader: addonmanager.Loader):
        with open("./domains.yaml") as f:
            out = yaml.safe_load(f)
            self.domains = out.get("domains", [])
            self.delicate_domains = out.get("delicate_domains", [])
            self.sni = out.get("default_sni", "google.com")

    def request(self, flow: HTTPFlow):
        if flow.request.scheme == "http":
            # Firefox displays an annoying message if it thinks its
            # captive portal check is being intercepted by a mitm redirect

            # we also need mitm.it to be accessible in http so mitmproxy can
            # change the response to be a cert download page
            if flow.request.host in ("detectportal.firefox.com", "mitm.it"):
                # TBH I don't think this is working for firefox at all lol
                return

            # Always redirect other non-https requests to https
            # since they will be blocked without TLS
            flow.response = http.Response.make(
                307,
                b"",
                {"Location": flow.request.url.replace("http://", "https://")},
            )

    def tls_start_server(self, data: tls.TlsData):
        if isinstance(data.conn, connection.Server):
            (domain, _) = data.conn.address
            if matches_any(self.domains, domain):
                data.context.client.sni = self.sni
            elif matches_any(self.delicate_domains, domain):
                data.context.client.sni = rf"{domain}."

        self.config.tls_start_server(data)


addons = [SNIProxy()]
