import ipaddress
import re
import urllib.request
from bs4 import BeautifulSoup
import socket
import requests
from googlesearch import search
import whois
from datetime import date
from urllib.parse import urlparse

class FeatureExtraction:
    def __init__(self, url):
        self.url = url
        self.domain = ""
        self.whois_response = None
        self.parsed_url = None
        self.response = None
        self.soup = None
        self.features = []

        # Parse URL
        try:
            self.parsed_url = urlparse(url)
            self.domain = self.parsed_url.netloc
        except:
            self.parsed_url = None

        # Fetch page
        try:
            self.response = requests.get(url, timeout=5)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            self.response = None
            self.soup = None

        # Whois lookup
        try:
            self.whois_response = whois.whois(self.domain)
        except:
            self.whois_response = None

        # Extract features
        self.features = [
            self.UsingIp(),
            self.longUrl(),
            self.shortUrl(),
            self.symbol(),
            self.redirecting(),
            self.prefixSuffix(),
            self.SubDomains(),
            self.Hppts(),
            self.DomainRegLen(),
            self.Favicon(),
            self.NonStdPort(),
            self.HTTPSDomainURL(),
            self.RequestURL(),
            self.AnchorURL(),
            self.LinksInScriptTags(),
            self.ServerFormHandler(),
            self.InfoEmail(),
            self.AbnormalURL(),
            self.WebsiteForwarding(),
            self.StatusBarCust(),
            self.DisableRightClick(),
            self.UsingPopupWindow(),
            self.IframeRedirection(),
            self.AgeofDomain(),
            self.DNSRecording(),
            self.WebsiteTraffic(),
            self.PageRank(),
            self.GoogleIndex(),
            self.LinksPointingToPage(),
            self.StatsReport()
        ]

    # ---------------- Feature Functions ---------------- #

    def UsingIp(self):
        try:
            ipaddress.ip_address(self.url)
            return -1
        except:
            return 1

    def longUrl(self):
        if len(self.url) < 54: return 1
        if 54 <= len(self.url) <= 75: return 0
        return -1

    def shortUrl(self):
        short_urls = 'bit\.ly|goo\.gl|tinyurl\.com|ow\.ly|is\.gd'
        return -1 if re.search(short_urls, self.url) else 1

    def symbol(self):
        return -1 if "@" in self.url else 1

    def redirecting(self):
        return -1 if self.url.rfind("//") > 6 else 1

    def prefixSuffix(self):
        return -1 if '-' in self.domain else 1

    def SubDomains(self):
        dot_count = self.domain.count('.')
        if dot_count == 1: return 1
        elif dot_count == 2: return 0
        return -1

    def Hppts(self):
        return 1 if self.parsed_url and self.parsed_url.scheme == 'https' else -1

    def DomainRegLen(self):
        try:
            creation_date = self.whois_response.creation_date
            expiration_date = self.whois_response.expiration_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            if isinstance(expiration_date, list): expiration_date = expiration_date[0]
            age_months = (expiration_date.year - creation_date.year)*12 + (expiration_date.month - creation_date.month)
            return 1 if age_months >= 12 else -1
        except:
            return -1

    def Favicon(self):
        try:
            for link in self.soup.find_all('link', href=True):
                if self.domain in link['href']:
                    return 1
            return -1
        except:
            return -1

    def NonStdPort(self):
        return -1 if ":" in self.domain else 1

    def HTTPSDomainURL(self):
        return -1 if "https" in self.domain else 1

    def RequestURL(self):
        try:
            success = 0
            total = 0
            if not self.soup: return 0
            for tag in self.soup.find_all(['img','audio','embed','iframe'], src=True):
                total += 1
                if self.url in tag['src'] or self.domain in tag['src'] or tag['src'].count('.') == 1:
                    success += 1
            if total == 0: return 0
            percentage = success / total * 100
            if percentage < 22.0: return 1
            elif 22.0 <= percentage < 61.0: return 0
            else: return -1
        except:
            return -1

    def AnchorURL(self):
        try:
            unsafe = 0
            total = 0
            if not self.soup: return -1
            for a in self.soup.find_all('a', href=True):
                total += 1
                href = a['href'].lower()
                if "#" in href or "javascript" in href or "mailto" in href or not (self.url in href or self.domain in href):
                    unsafe += 1
            if total == 0: return -1
            percentage = unsafe / total * 100
            if percentage < 31.0: return 1
            elif 31.0 <= percentage < 67.0: return 0
            else: return -1
        except:
            return -1

    def LinksInScriptTags(self):
        try:
            success = 0
            total = 0
            if not self.soup: return 0
            for tag in self.soup.find_all(['link','script'], href=True, src=True):
                total += 1
                if self.url in tag.get('href', '') or self.domain in tag.get('href', '') or self.url in tag.get('src','') or self.domain in tag.get('src',''):
                    success += 1
            if total == 0: return 0
            percentage = success / total * 100
            if percentage < 17.0: return 1
            elif 17.0 <= percentage < 81.0: return 0
            else: return -1
        except:
            return -1

    def ServerFormHandler(self):
        try:
            if not self.soup: return -1
            forms = self.soup.find_all('form', action=True)
            if not forms: return 1
            for form in forms:
                action = form['action']
                if action == "" or action == "about:blank":
                    return -1
                elif self.url not in action and self.domain not in action:
                    return 0
            return 1
        except:
            return -1

    def InfoEmail(self):
        try:
            if self.soup and re.findall(r"mailto:", str(self.soup)):
                return -1
            return 1
        except:
            return -1

    def AbnormalURL(self):
        try:
            return 1 if self.response and self.response.text == str(self.whois_response) else -1
        except:
            return -1

    def WebsiteForwarding(self):
        try:
            if self.response is None: return -1
            if len(self.response.history) <= 1: return 1
            elif len(self.response.history) <= 4: return 0
            else: return -1
        except:
            return -1

    def StatusBarCust(self):
        try:
            if self.response and re.search(r"<script>.+onmouseover.+</script>", self.response.text):
                return 1
            return -1
        except:
            return -1

    def DisableRightClick(self):
        try:
            if self.response and re.search(r"event.button ?== ?2", self.response.text):
                return 1
            return -1
        except:
            return -1

    def UsingPopupWindow(self):
        try:
            if self.response and re.search(r"alert\(", self.response.text):
                return 1
            return -1
        except:
            return -1

    def IframeRedirection(self):
        try:
            if self.response and re.search(r"<iframe>|<frameBorder>", self.response.text):
                return 1
            return -1
        except:
            return -1

    def AgeofDomain(self):
        try:
            if not self.whois_response: return -1
            creation_date = self.whois_response.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            today = date.today()
            age_months = (today.year - creation_date.year)*12 + (today.month - creation_date.month)
            return 1 if age_months >= 6 else -1
        except:
            return -1

    def DNSRecording(self):
        return self.AgeofDomain()

    def WebsiteTraffic(self):
        return 0  # Placeholder for safe execution

    def PageRank(self):
        return 0  # Placeholder for safe execution

    def GoogleIndex(self):
        try:
            result = list(search(self.url, num_results=5))
            return 1 if result else -1
        except:
            return 1

    def LinksPointingToPage(self):
        try:
            if not self.response: return -1
            links = re.findall(r"<a href=", self.response.text)
            if len(links) == 0: return 1
            elif len(links) <= 2: return 0
            else: return -1
        except:
            return -1

    def StatsReport(self):
        try:
            ip_address = socket.gethostbyname(self.domain)
            return 1
        except:
            return -1

    def getFeaturesList(self):
        return self.features
 