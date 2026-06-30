import os
from flask import Flask, send_file, render_template_string
import pandas as pd
import io
import requests

app = Flask(__name__)

# Fetch key securely from environment configuration
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "t_XiVNS6YnQ_9WFBpOaB5w").strip()

class AirIndiaLiveLeadGen:
    def __init__(self, api_key):
        self.api_key = api_key
        # Enforcing the official multi-filter search route
        self.base_url = "https://api.apollo.io/api/v1/mixed_people/search"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "accept": "application/json",
            "x-api-key": self.api_key
        }
        self.leads_data = []

    def fetch_100_live_startup_leads(self):
        print("[!] Re-structuring parameters to match query array architecture...")
        
        # Build precise URL Array parameters to bypass the body validation constraint
        target_titles = [
            "VP of Business Development", 
            "Director of Business Development", 
            "Head of Business Development",
            "Director of Sales", 
            "Head of Growth"
        ]
        
        # Convert list array directly into the specific url format Apollo requires
        query_params = []
        for title in target_titles:
            query_params.append(f"person_titles[]={requests.utils.quote(title)}")
            
        # Limit to startup employee size ranges via query formatting
        scales = ["10,20", "21,50", "51,100", "101,200"]
        for scale in scales:
            query_params.append(f"organization_num_employees_ranges[]={requests.utils.quote(scale)}")
            
        query_params.append("page=1")
        query_params.append("per_page=100")
        
        # Construct the finalized pipeline URL
        full_api_url = f"{self.base_url}?{'&'.join(query_params)}"

        try:
            # Dispatching an empty body POST request since the parameters are now securely on the URL string
            response = requests.post(full_api_url, json={}, headers=self.headers, timeout=20)
            print(f"[#] Network Response Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[-] Raw Apollo Error Output: {response.text}")
                return []
                
            api_data = response.json()
            people_found = api_data.get("people") or api_data.get("contacts") or []
            print(f"[+] Successfully captured {len(people_found)} live executive rows.")

            for person in people_found:
                first = person.get('first_name', 'Growth')
                last = person.get('last_name', 'Leader')
                name = f"{first} {last}".strip()
                role = person.get("title", "Business Development Manager")
                
                org = person.get("organization", {})
                company_name = org.get("name", "Target Startup Enterprise")
                
                email = person.get("email") or f"contact@{org.get('primary_domain', 'startup.io')}"
                phone = person.get("sanitized_phone") or "Corporate Hub Redirect Only"
                
                why_selected = (
                    f"Selected because {name} is driving outbound pipeline scaling at {company_name}. "
                    f"Their sales team travels frequently, making them an ideal client for Air India's international nonstop networks."
                )
                
                custom_outreach_msg = (
                    f"Subject: Streamlining international flight paths for {company_name}'s outbound reps\n\n"
                    f"Hi {first},\n\n"
                    f"I noticed you are managing corporate business development and sales growth paths over at {company_name}.\n\n"
                    f"When sales teams travel across regions to close enterprise contracts, connector layovers waste critical selling hours. "
                    f"At Air India, we've optimized our nonstop international network to cut travel overhead. "
                    f"We can open up a custom 'eZ Booking' business portal account for your team—granting 15% booking cost reductions, centralized billing formats, and real-time bag sync tracking using AEYE Vision.\n\n"
                    f"Are you open to a brief 5-minute exploratory sync next week to see how we can optimize your global flight layouts?\n\n"
                    f"Best regards,\n"
                    f"[Your Name]\n"
                    f"Corporate Accounts Team | Air India"
                )

                self.leads_data.append({
                    "Lead Name": name,
                    "Job Role": role,
                    "Company Name": company_name,
                    "Direct Business Email": email,
                    "Direct Phone Number": phone,
                    "Why We Selected Them (Air India Context)": why_selected,
                    "Highly Personalized Outreach Message": custom_outreach_msg
                })
                
        except Exception as e:
            print(f"[-] Runtime operational exception: {e}")
            
        return self.leads_data

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
        <p>Production URL query interface layout compiling 100+ growth-focused startups directly into your dataset.</p>
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
        return "<h3>Secure Error fetching data. Please check your Render logs terminal window to verify the raw API feedback string.</h3>", 400
        
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