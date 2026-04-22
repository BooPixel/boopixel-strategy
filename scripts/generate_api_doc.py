"""Generate Google Ads API design document PDF for Basic Access application."""

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "BooPixel - Google Ads API Tool Design Document", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def section(self, title, body):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, body)
        self.ln(4)


pdf = PDF()
pdf.add_page()

pdf.section(
    "1. Company Overview",
    "BooPixel (https://app.boopixel.com) is a digital services platform for small and medium "
    "businesses in Brazil. We provide website creation, AI-powered customer service agents, "
    "SEO consulting, and marketing automation. Our team consists of 2 co-founders who manage "
    "all operations, including advertising campaigns on Google Ads."
)

pdf.section(
    "2. Tool Purpose",
    "We are building an internal tool to manage Google Ads campaigns programmatically. "
    "The tool will be used exclusively by BooPixel employees (internal use only). "
    "It will NOT be offered as a product or service to external users.\n\n"
    "Primary use cases:\n"
    "- Create and manage Search campaigns for lead generation\n"
    "- Monitor campaign performance (impressions, clicks, conversions, CPC, CPL)\n"
    "- Automate bid adjustments based on conversion data from our CRM\n"
    "- Generate performance reports for internal decision-making\n"
    "- Pause/enable campaigns based on business rules (budget limits, lead volume)"
)

pdf.section(
    "3. Architecture",
    "The tool is a Python script that runs locally or via scheduled tasks (cron). "
    "It uses the google-ads Python library to interact with the Google Ads API.\n\n"
    "Components:\n"
    "- Python 3.13+ with google-ads SDK\n"
    "- OAuth 2.0 Desktop App flow for authentication\n"
    "- Environment variables for credentials (.env file)\n"
    "- MCC account (860-999-5521) managing client account (469-236-2147)\n\n"
    "Data flow:\n"
    "1. Script authenticates via OAuth 2.0 refresh token\n"
    "2. Reads campaign/ad group/keyword performance via GoogleAdsService.Search\n"
    "3. Applies business rules (e.g., pause keyword if CPC > threshold)\n"
    "4. Writes changes via mutate operations\n"
    "5. Outputs reports to local files or sends email summaries"
)

pdf.section(
    "4. API Features Used",
    "- GoogleAdsService.Search (GAQL queries for reporting)\n"
    "- CampaignService (create, update, pause campaigns)\n"
    "- AdGroupService (manage ad groups)\n"
    "- AdGroupAdService (manage ads)\n"
    "- AdGroupCriterionService (manage keywords)\n"
    "- CustomerService (account info)\n"
    "- BiddingStrategyService (bid management)\n"
    "- ConversionActionService (conversion tracking)"
)

pdf.section(
    "5. Rate Limiting & Best Practices",
    "- All operations use a single MCC account (860-999-5521)\n"
    "- Expected API call volume: < 1,000 requests/day\n"
    "- Batch mutate operations when possible\n"
    "- Exponential backoff for transient errors\n"
    "- Caching of unchanged resources to minimize reads\n"
    "- No real-time user-facing requests (batch/scheduled only)"
)

pdf.section(
    "6. Accounts",
    "- MCC (Manager Account): 860-999-5521\n"
    "- Client Account: 469-236-2147\n"
    "- Google Cloud Project: boopixel\n"
    "- OAuth Client Type: Desktop App\n"
    "- All managed by the same organization (BooPixel)"
)

pdf.section(
    "7. Security",
    "- OAuth 2.0 credentials stored in local .env file (not in source control)\n"
    "- Refresh tokens are never logged or transmitted\n"
    "- Access limited to BooPixel co-founders only\n"
    "- No external user access to the tool\n"
    "- No storage of Google Ads data in external databases"
)

pdf.section(
    "8. Compliance",
    "- We comply with Google Ads API Terms and Conditions\n"
    "- We comply with Google Ads policies for all campaigns\n"
    "- No automated creation of ads without human review\n"
    "- No scraping or data extraction for external use\n"
    "- Tool is for campaign management and reporting only"
)

output = "/Users/fernandocelmer/Lab/BooPixel/boopixel-strategy/scripts/output/google_ads_api_design.pdf"
pdf.output(output)
print(f"PDF gerado: {output}")
