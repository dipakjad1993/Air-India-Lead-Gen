import os
from flask import Flask, send_file, render_template_string
import pandas as pd
import io
import requests

app = Flask(__name__)

# PASTE YOUR APOLLO API KEY HERE (or set it as an Environment Variable on Render)
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "ZhKFnykcA1dthPc7FIUEmQ")

class AirIndiaLiveLeadGen:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.apollo.io/v1/mixed_people/search"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json"
        }
        self.leads_data = []

    def fetch_100_live_startup_leads(self):
        print("[!] Connecting to Apollo.io Production API Engine...")
        
        # Build payload targeting precisely 100 startup growth/BD profiles
        payload = {
            "api_key": self.api_key,
            "person_titles": [
                "VP of Business Development", 
                "Director of Business Development", 
                "Head of Business Development",
                "Director of Sales", 
                "Head of Growth",
                "VP of Sales"
            ],
            "organization_num_employees_ranges": ["10,20", "21,50", "51,100", "101,200"], # Restricting to Startups/SMBs
            "page": 1,
            "per_page": 100 # Pulling 100 live targets at once
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=20)
            if response.status_code != 200:
                print(f"[-] API Error: {response.status_code} - {response.text}")
                return []
            
            api_data = response.json()
            people_found = api_data.get("people", [])
            print(f"[+] Successfully fetched {len(people_found)} live decision-makers from database.")

            for person in people_found:
                name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
                role = person.get("title", "Growth Lead")
                
                # Extract organization details safely
                org = person.get("organization", {})
                company_name = org.get("name", "Target Startup")
                company_scale = f"{org.get('estimated_num_employees', 'SMB')} employees"
                raw_keywords = org.get("primary_domain", "")
                
                email = person.get("email", "Requesting Verification...")
                phone = person.get("sanitized_phone", "No Direct Line Listed")
                
                # Contextualizing Air India value propositions natively onto real-time data fields
                why_selected = (
                    f"Selected because {name} oversees global outbound revenue structures at {company_name} ({company_scale}). "
                    f"Their sales units require maximum time optimization. Air India's centralized nonstop network "
                    f"removes multi-stop layover overhead to international target ecosystems."
                )
                
                custom_outreach_msg = (
                    f"Subject: Streamlining travel pathways for the {company_name} sales squad\n\n"
                    f"Hi {person.get('first_name', 'Team')},\n\n"
                    f"I noticed you are managing global partnership expansion pathways over at {company_name}.\n\n"
                    f"When sales and BD teams are traveling across borders to secure enterprise contracts, layovers drag down efficiency. "
                    f"At Air India, we have built out an optimized nonstop flight grid connecting major corporate zones directly to top international hubs. "
                    f"We can integrate a dedicated 'eZ Booking' corporate framework for your team—unlocking custom flight tiers, 15% booking cost reductions, and automated real-time baggage updates via AEYE Vision.\n\n"
                    f"Are you open to a brief 5-minute sync next week to see how we can optimize your global flight layouts?\n\n"
                    f"Best regards,\n"
                    f"[Your Name]\n"
                    f"Corporate Accounts Team | Air India"
                )

                self.leads_data.append({
                    "Lead Name": name,
                    "Job Role": role,
                    "Company Name": company_name,
                    "Company Scale": company_scale,
                    "Direct Business Email": email,
                    "Direct Phone Number": phone,
                    "Corporate Target Alignment": "International BD Scale Plan",
                    "Why We Selected Them (Air India Context)": why_selected,
                    "Highly Personalized Outreach Message": custom_outreach_msg
                })
                
        except Exception as e:
            print(f"[-] Critical system runtime failure during API loop: {e}")
            
        return self.leads_data

# HTML UI Layout
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Air India Live B2B Engine</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f9f9f9; }
        .container { background: white; padding: 40px; border-radius: 10px; display: inline-block; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        button { background-color: #d11226; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #a30e1d; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #d11226;">Air India Executive Pipeline</h1>
        <p>Connects live to global B2B networks to filter 100+ targeted startup decision-makers in real time.</p>
        <form action="/download" method="GET">
            <button type="submit">Generate & Download 100+ Live Leads</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download_leads():
    engine = AirIndiaLiveLeadGen(api_key=APOLLO_API_KEY)
    data = engine.fetch_100_live_startup_leads()
    
    if not data:
        return "<h3>Error fetching live API records. Please check your Apollo API key setup configuration!</h3>", 400
        
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Live Corporate Targets")
    output.seek(0)
    
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="air_india_100_live_leads.xlsx"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)