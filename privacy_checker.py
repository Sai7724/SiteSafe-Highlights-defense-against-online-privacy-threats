import requests
from bs4 import BeautifulSoup
import tldextract
import whois
import spacy
from nlp_analyzer import ai_privacy_analysis
import ssl, socket
from datetime import datetime
from transformers import pipeline

# ------------------------- LOAD NLP MODELS -------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("⚠️ Error loading summarizer:", e)
    summarizer = None


# ------------------------- FETCH PRIVACY POLICY -------------------------
def get_privacy_policy(url):
    """
    Try to fetch the privacy policy page HTML.
    """
    try:
        if url.endswith('/'):
            privacy_url = url + "privacy-policy"
        else:
            privacy_url = url + "/privacy-policy"
        res = requests.get(privacy_url, timeout=8)
        if res.status_code == 200:
            return res.text
        return ""
    except Exception as e:
        print("Privacy policy fetch error:", e)
        return ""


# ------------------------- TRACKER BLOCKLIST ------------------------
TRACKER_BLOCKLIST = {}

def load_tracker_blocklist():
    """
    Load the Disconnect tracker blocklist.
    """
    global TRACKER_BLOCKLIST
    try:
        # URL for the Disconnect tracker list
        url = "https://s3.amazonaws.com/lists.disconnect.me/simple_tracker_prod.json"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            # Flatten the list of trackers
            for category in data['trackers'].values():
                for company, domains in category.items():
                    for domain in domains:
                        TRACKER_BLOCKLIST[domain] = company
            print("✅ Tracker blocklist loaded successfully.")
        else:
            print("⚠️ Failed to load tracker blocklist.")
    except Exception as e:
        print(f"⚠️ Error loading tracker blocklist: {e}")

# Load the blocklist when the module is imported
load_tracker_blocklist()

# ------------------------- TRACKER DETECTION -------------------------
def detect_trackers(html, url):
    """
    Detect and explain specific trackers used on the website using the blocklist.
    """
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all("script", src=True)
    site_domain = tldextract.extract(url).domain
    
    detected_trackers = set()

    for script in scripts:
        src = script.get("src")
        if not src:
            continue
        
        src_domain = tldextract.extract(src).registered_domain
        
        # Check against the blocklist
        if src_domain in TRACKER_BLOCKLIST:
            tracker_name = TRACKER_BLOCKLIST[src_domain]
            detected_trackers.add((tracker_name, f"Known tracker domain: {src_domain}"))
            
        # Also identify other third-party scripts
        elif src_domain and src_domain != site_domain:
            detected_trackers.add((f"3rd-party: {src_domain}", "External script that may collect data."))

    return list(detected_trackers)



# ------------------------- DOMAIN INFO -------------------------
def get_domain_info(url):
    """
    Get domain age and registrar using WHOIS and SSL fallback.
    """
    age = None
    registrar = None

    try:
        domain = tldextract.extract(url).fqdn
        info = whois.whois(domain)

        creation_date = info.creation_date
        if creation_date:
            if isinstance(creation_date, list):
                age = 2025 - creation_date[0].year
            else:
                age = 2025 - creation_date.year

        registrar = info.registrar if info.registrar else None
    except Exception as e:
        print("WHOIS error:", e)

    # SSL Fallback
    if age is None:
        try:
            hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_start = datetime.strptime(cert['notBefore'], "%b %d %H:%M:%S %Y %Z")
                    age = 2025 - ssl_start.year
        except Exception as e:
            print("SSL fallback error:", e)
            age = None

    return age, registrar


# ------------------------- SUMMARIZATION -------------------------
def summarize_policy(text):
    """
    Summarize privacy policy text using transformer model.
    """
    if not summarizer:
        return "Summarizer not available."
    try:
        short_text = text[:3000]
        summary = summarizer(short_text, max_length=150, min_length=40, do_sample=False)
        return summary[0]["summary_text"].strip()
    except Exception as e:
        print("Summarization error:", e)
        return "Unable to summarize privacy policy."


# ------------------------- MAIN ANALYSIS -------------------------
def analyze_url(url):
    report = {}
    score = 100

    # Website reachability
    try:
        res = requests.get(url, timeout=6)
        html = res.text
        report["status"] = "✅ Website reachable"
    except Exception as e:
        report["status"] = "❌ Website not reachable"
        return 0, report

    # HTTPS check
    if url.startswith("https"):
        report["https"] = "✅ Secure (HTTPS enabled)"
    else:
        report["https"] = "⚠️ Not Secure (No HTTPS)"
        score -= 20

    # Tracker detection
    trackers = detect_trackers(html, url)
    if len(trackers) > 0:
        tracker_details = "\n".join([f"• {t[0]} — {t[1]}" for t in trackers])
        report["trackers"] = f"⚠️ {len(trackers)} trackers detected:\n{tracker_details}"
        score -= len(trackers) * 8
    else:
        report["trackers"] = "✅ No trackers detected"

    # Privacy policy
    policy_text = get_privacy_policy(url)
    if policy_text:
        report["policy_found"] = "✅ Privacy policy found"
        summary = summarize_policy(policy_text)
        clean_text = " ".join([token.lemma_ for token in nlp(policy_text[:1500])])
        label, confidence = ai_privacy_analysis(clean_text)
        report["policy_summary"] = f"🧾 Summary: {summary}"
        report["policy_ai"] = f"AI Risk Level: {label.upper()} ({confidence}% confidence)"
        if label == "high risk":
            score -= 30
        elif label == "moderate risk":
            score -= 15
    else:
        report["policy_found"] = "❌ No privacy policy detected"
        report["policy_summary"] = "No summary available."
        score -= 15

    # Domain info
    age, registrar = get_domain_info(url)
    report["domain_age"] = f"{age} years" if age else "Unknown (privacy-protected)"
    report["registrar"] = registrar if registrar else "Unknown (privacy-protected)"

    # Final score
    if score >= 80:
        grade = "A (Low Risk)"
    elif score >= 60:
        grade = "B (Moderate Risk)"
    else:
        grade = "C (High Risk)"

    report["final"] = f"🔒 Privacy Score: {score}/100 — Grade: {grade}"
    return score, report
