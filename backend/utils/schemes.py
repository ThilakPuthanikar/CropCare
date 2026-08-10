import json
from typing import Iterable, List, Optional

from ..models.scheme import Scheme


DEFAULT_SCHEMES = [
    {
        "title": "PM-KISAN Samman Nidhi",
        "description": "Direct income support scheme providing assured annual financial assistance to all eligible landholding farmer families across India via Direct Benefit Transfer (DBT).",
        "type": "national",
        "beneficiary": "small",
        "benefits": "Rs. 6,000 per financial year, transferred directly into bank accounts in three equal installments of Rs. 2,000 every 4 months.",
        "eligibility": "All landholding farmer families with cultivable landholding in their names. Exclusions apply to institutional landholders, constitutional post holders, serving/retired government employees, doctors, engineers, lawyers, and income tax payers.",
        "documents_required": [
            "Aadhaar Card (mandatory for e-KYC and DBT link)",
            "Bank Account Details (Passbook copy showing account number and IFSC code)",
            "Land Ownership Records (Updated RTC / Khata / RoR - Record of Rights showing survey number and ownership)",
            "Active Mobile Number linked with Aadhaar",
        ],
        "steps_to_apply": [
            "Step 1: Portal or Center Visit - Visit the official portal https://pmkisan.gov.in/ and click on 'New Farmer Registration', or visit your nearest Common Service Center (CSC) / Raitha Samparka Kendra (RSK).",
            "Step 2: Land & Personal Data Entry - Select Rural/Urban farmer registration, enter your Aadhaar number, state (Karnataka), and mobile number. Input your exact land details including Survey Number, Dag Number, and Khata Area.",
            "Step 3: Document Upload - Upload clear scanned copies of your land ownership proof (RTC/RoR) and Aadhaar card.",
            "Step 4: Mandatory e-KYC Completion - Complete OTP-based e-KYC on the portal or biometric e-KYC at a CSC to link your Aadhaar with DBT payment routing.",
            "Step 5: Verification & Payment Tracking - Your local agriculture department and revenue officers verify land ownership against the state Bhoomi database. Once approved, track your installment status under 'Beneficiary Status' on the portal.",
        ],
        "duration": "Ongoing Annual Benefit",
        "official_link": "https://pmkisan.gov.in/",
        "icon": "fas fa-rupee-sign",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Flagship comprehensive crop insurance scheme providing risk coverage from pre-sowing to post-harvest against natural calamities, pests, and diseases.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Comprehensive insurance coverage for crop loss. Highly subsidized farmer premium: only 2% for Kharif crops, 1.5% for Rabi crops, and 5% for annual commercial/horticultural crops.",
        "eligibility": "All farmers growing notified crops in notified insurance areas (districts/taluks). Both loanee (KCC) and non-loanee farmers (including sharecroppers and tenant farmers with valid tenancy agreements) are eligible.",
        "documents_required": [
            "Aadhaar Card",
            "Bank Account Passbook (showing account number and IFSC code)",
            "Land Records (RTC / Khata / Pahani / Sowing Certificate from Village Accountant or Revenue Officer)",
            "Crop Sowing Declaration (or self-declaration of sowing date and crop variety)",
            "Tenancy / Sharecropper Agreement (if cultivating leased land)",
        ],
        "steps_to_apply": [
            "Step 1: Check Notification & Cut-off Dates - Verify that your crop and district/taluk are notified for the current Kharif/Rabi season before the enrollment deadline (usually July 31 for Kharif and December 31 for Rabi).",
            "Step 2: Choose Application Channel - Apply online via https://pmfby.gov.in/, through Samrakshane (Karnataka state portal), at a primary agricultural cooperative bank (PACS), or at a Common Service Center (CSC).",
            "Step 3: Submit Crop & Land Details - Enter your Survey Number, notified crop name, area sown in hectares, and bank details.",
            "Step 4: Pay Subsidized Premium - Pay your share of the insurance premium (1.5% to 5%) online or at the bank counter and receive an official policy receipt (Acknowledge ID).",
            "Step 5: Claim Filing & Settlement - In case of localized crop loss or mid-season adversity, intimate the insurance company or agriculture officer within 72 hours via the Crop Insurance App/Toll-Free Helpline with geotagged photos of the damaged crop for survey and claim payout.",
        ],
        "duration": "Seasonal (Kharif / Rabi cycle)",
        "official_link": "https://pmfby.gov.in/",
        "icon": "fas fa-shield-alt",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Kisan Credit Card",
        "description": "Institutional short-term crop credit and working capital support mechanism enabling farmers to purchase agricultural inputs and meet farming expenses at subsidized interest rates.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Short-term crop loans up to Rs. 3 Lakhs at a subsidized interest rate of 7% per annum. Prompt repayment within the due date earns an additional 3% interest subvention, lowering the effective interest rate to just 4% per annum. Collateral-free loan limit up to Rs. 1.60 Lakhs.",
        "eligibility": "Individual farmers, joint borrowers, tenant farmers, sharecroppers, and Self-Help Groups (SHGs) involved in agricultural production or allied activities (dairy, poultry, fisheries).",
        "documents_required": [
            "Identity Proof (Aadhaar Card, Voter ID, PAN Card, or Driving License)",
            "Address Proof (Aadhaar Card or Utility Bill)",
            "Land Records (Updated RTC / Khata showing landholding and encumbrance status)",
            "Cropping Plan (Details of crops grown across Kharif and Rabi seasons)",
            "2 Passport-size Photographs",
        ],
        "steps_to_apply": [
            "Step 1: Obtain KCC Application Form - Download the simplified 1-page KCC application form from https://www.myscheme.gov.in/schemes/kcc or visit your commercial bank, Regional Rural Bank (Karnataka Gramin Bank), or cooperative bank branch.",
            "Step 2: Fill Cropping & Credit Requirements - List the crops you plan to grow, acreage, and estimated operational costs for seeds, fertilizers, and labor.",
            "Step 3: Submit Land & Verification Documents - Attach your updated land records (RTC) and Aadhaar card at the bank branch.",
            "Step 4: Bank Inspection & Limit Sanction - The bank field officer verifies your cultivation records and calculates your scale of finance credit limit.",
            "Step 5: Card Activation & Drawal - Receive your KCC RuPay ATM/Debit card and passbook to withdraw working capital directly from ATMs or purchase agricultural inputs from authorized dealers.",
        ],
        "duration": "Renewable 5-Year Credit Limit (Annual Review)",
        "official_link": "https://www.myscheme.gov.in/schemes/kcc",
        "icon": "fas fa-credit-card",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "PM-KUSUM Scheme (Component B)",
        "description": "Clean energy agricultural irrigation initiative providing heavy financial subsidies for setting up standalone off-grid solar-powered agriculture pumps.",
        "type": "national",
        "beneficiary": "small",
        "benefits": "60% capital subsidy (30% Central + 30% State) on standalone off-grid Solar Agriculture Pumps (up to 7.5 HP capacity). Farmers pay only 10% upfront beneficiary contribution, while the remaining 30% is provided as an institutional bank loan.",
        "eligibility": "Individual farmers, Water User Associations, and Farmer Producer Organizations (FPOs) who own cultivable land with a water source (borewell, open well, or farm pond) without an existing grid-connected electric pump connection.",
        "documents_required": [
            "Aadhaar Card",
            "Land Ownership Record (RTC / Khata copy)",
            "Bank Account Passbook copy",
            "Certificate of Water Source (Borewell depth / yield confirmation or open well details)",
            "Passport-size Photograph",
        ],
        "steps_to_apply": [
            "Step 1: Check State Portal Registration - In Karnataka, applications for PM-KUSUM are processed via the Karnataka Renewable Energy Development Limited (KREDL) or ESCOM (BESCOM/HESCOM) portal when registration windows open.",
            "Step 2: Submit Application & Pump Specifications - Select your required pump capacity (3 HP, 5 HP, or 7.5 HP - surface or submersible) corresponding to your water source depth and land area.",
            "Step 3: Document Verification & Technical Feasibility - State technical officers verify land ownership and water source availability on your farmland.",
            "Step 4: Pay 10% Beneficiary Share - Once sanctioned and the demand note is issued, deposit your 10% beneficiary contribution online to the designated state agency account.",
            "Step 5: Installation & Inspection - Authorized vendors install the solar panel arrays, controller, and pump set on your farm, followed by joint commissioning inspection and 5-year warranty activation.",
        ],
        "duration": "Capital Subsidy + 5-Year Vendor Warranty",
        "official_link": "https://pmkusum.mnre.gov.in/",
        "icon": "fas fa-solar-panel",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Soil Health Card Scheme",
        "description": "Scientific soil testing and nutrient management advisory program providing farm-specific fertilizer prescriptions to optimize crop yield and prevent soil degradation.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Free comprehensive lab testing of soil samples across 12 vital macro and micro parameters (pH, EC, Organic Carbon, Available N, P, K, S, Zn, Fe, Cu, Mn, and B). Provides a tailored Soil Health Card with specific fertilizer and organic amendment dosage recommendations to reduce input cost by 15-25% and boost crop yield.",
        "eligibility": "All farming families cultivating agricultural land across India.",
        "documents_required": [
            "Aadhaar Card / Voter ID",
            "Land Record (RTC / Survey Number details)",
            "Soil Sample Details Form (Geotagged coordinates, previous crop grown, and irrigation type)",
        ],
        "steps_to_apply": [
            "Step 1: Sample Collection Guidance - Collect grid-based soil samples (V-shaped cut 15 cm deep from 5-10 spots across the field, mix thoroughly, quarter down to 500 grams).",
            "Step 2: Submit Sample to Testing Laboratory - Deliver the labeled 500g soil sample bag to your nearest Raitha Samparka Kendra (RSK), Krishi Vigyan Kendra (KVK), or district mobile soil testing laboratory.",
            "Step 3: Registration on SHC Portal - The agriculture assistant registers your farmer ID, survey number, and sample code on the online portal https://soilhealth.dac.gov.in/.",
            "Step 4: Laboratory Analysis & Prescription Generation - Scientists analyze the 12 soil parameters and generate a customized crop-wise fertilizer prescription table.",
            "Step 5: Card Collection & Implementation - Collect your printed/digital Soil Health Card from the RSK or download it online via OTP, and apply the exact recommended NPK and micronutrient dosage for your upcoming season.",
        ],
        "duration": "Renewed every 2 years",
        "official_link": "https://soilhealth.dac.gov.in/",
        "icon": "fas fa-vial",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Krishi Bhagya",
        "description": "Flagship Karnataka state water conservation and dryland farming initiative promoting rainwater harvesting through farm ponds (Krishi Honda) and efficient micro-irrigation.",
        "type": "state",
        "beneficiary": "small",
        "benefits": "Up to 80% to 90% financial assistance (subsidy) for constructing farm ponds (Krishi Honda), UV-stabilized polythene lining to prevent seepage, diesel/solar lifting pump sets, and micro-irrigation systems (drip/sprinkler) across 131 rainfed taluks in Karnataka.",
        "eligibility": "Small and marginal farmers (80-90% subsidy) and general category farmers (80% subsidy) in rainfed/dryland agricultural zones of Karnataka who own cultivable land and depend primarily on monsoon rainfall.",
        "documents_required": [
            "Aadhaar Card",
            "Land Ownership Documents (Current year RTC / Pahani and Mutation copy)",
            "Bank Account Passbook (for direct subsidy transfer / vendor payment)",
            "Small/Marginal Farmer Certificate (if claiming 90% subsidy rate)",
            "Caste Certificate (for SC/ST farmers claiming enhanced assistance)",
            "Passport-size Photograph",
        ],
        "steps_to_apply": [
            "Step 1: Visit Raitha Samparka Kendra (RSK) - Approach your Hobli-level Raitha Samparka Kendra or Assistant Director of Agriculture (ADA) office during the application period.",
            "Step 2: Submit Application with Land Profile - Submit the Krishi Bhagya application form along with your RTC, Aadhaar, and proposed farm pond dimensions.",
            "Step 3: Field Pre-Inspection - An Agriculture Officer / Technical Assistant visits your field to verify site feasibility, catchment area, and GPS coordinates for the pond.",
            "Step 4: Sanction Order & Pond Construction - Upon receiving the administrative sanction order, excavate the farm pond and install the UV-stabilized polythene lining as per technical specifications.",
            "Step 5: Post-Inspection & Subsidy Release - Department engineers inspect the completed pond, take geotagged verification photos, and release the subsidy directly via DBT or to the authorized equipment vendor.",
        ],
        "duration": "One-time capital infrastructure subsidy",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-water",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Ganga Kalyana Scheme",
        "description": "Karnataka social welfare irrigation project providing 100% financial assistance for drilling free borewells and installing pump sets for small and marginal SC/ST/OBC farmers.",
        "type": "state",
        "beneficiary": "small",
        "benefits": "100% financial assistance (up to Rs. 3.50 Lakhs to Rs. 4.00 Lakhs) for drilling free borewells, supply of submersible pump sets, accessories, and complete electrical electrification/solar energization for small and marginal farmers belonging to SC, ST, OBC, and Minority communities who lack perennial irrigation facilities.",
        "eligibility": "Small and marginal farmers holding between 1.20 acres to 5.00 acres of dryland in Karnataka. Must belong to SC/ST (via Dr. B.R. Ambedkar/Valmiki Corporations), OBC (via D. Devaraj Urs Corporation), or Minority communities. Must not have an existing borewell or irrigation connection on their land.",
        "documents_required": [
            "Aadhaar Card",
            "Land Records (RTC / Pahani covering at least 1.20 acres of contiguous land)",
            "Caste and Income Certificate issued by Tahsildar (Annual family income within prescribed limits)",
            "Small/Marginal Farmer Certificate issued by Revenue Authority",
            "Self-declaration / Affidavit confirming no prior borewell on the property",
            "Bank Account Passbook copy",
        ],
        "steps_to_apply": [
            "Step 1: Check Corporation Portal / Notification - Apply online through the respective development corporation portal (https://kmdeve.karnataka.gov.in/ or Seva Sindhu / KDDC) when the annual enrollment window is announced.",
            "Step 2: Document Submission & Screening - Fill out personal, caste, and land holding details and upload scanned copies of your RTC, Caste/Income certificate, and Aadhaar.",
            "Step 3: Taluk Selection Committee Approval - Applications are screened and selected by the Taluk Level Selection Committee headed by the local MLA and District/Taluk Social Welfare Officers.",
            "Step 4: Groundwater Hydro-geological Survey - Geologists from the Mines & Geology Department conduct scientific groundwater point identification on your farmland.",
            "Step 5: Drilling, Electrification & Handover - Approved empanelled contractors drill the borewell, install the submersible pump set, and coordinate with ESCOMs (BESCOM/HESCOM/GESCOM) for power connection and handover to the farmer.",
        ],
        "duration": "One-time complete irrigation asset provision",
        "official_link": "https://kalyanamitra.karnataka.gov.in/",
        "icon": "fas fa-tint",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Raitha Siri",
        "description": "Specialized Karnataka state incentive scheme promoting the cultivation and conservation of nutri-cereals and minor millets (Siri Dhanya) among small and marginal farmers.",
        "type": "state",
        "beneficiary": "marginal",
        "benefits": "Direct cash incentive of Rs. 10,000 per hectare (up to a maximum of 2 hectares / Rs. 20,000 per farmer) for cultivating nutri-cereals / minor millets (Foxtail millet, Little millet, Kodo millet, Proso millet, Barnyard millet, and Browntop millet) during the agricultural season.",
        "eligibility": "All farmers in Karnataka who cultivate approved minor millets on their agricultural land during the notified Kharif season. Land registration in RTC under millet crop sowing (Siri Dhanya) is mandatory.",
        "documents_required": [
            "Aadhaar Card",
            "Land Ownership Record (Updated RTC showing millet crop sowing entry under crop details)",
            "Bank Account Passbook linked with Aadhaar (for direct DBT incentive transfer)",
            "Farmer Registration ID on FRUITS Portal (https://fruits.karnataka.gov.in/)",
        ],
        "steps_to_apply": [
            "Step 1: Register on FRUITS Portal - Ensure you have a valid Farmer ID (FID) on Karnataka's FRUITS (Farmer Registration and Unified Beneficiary Information System) portal with your exact RTC linked.",
            "Step 2: Sowing & RTC Crop Booking - Sow minor millets on your farmland during the Kharif season and ensure the Village Accountant / Crop Survey team records the millet crop name correctly in your RTC (Column 12 / Crop details).",
            "Step 3: Submit Raitha Siri Application at RSK - Visit your local Raitha Samparka Kendra (RSK) with your FID, RTC copy, and Aadhaar card to apply for the Raitha Siri incentive.",
            "Step 4: Field Verification by Agriculture Department - The Assistant Agriculture Officer (AAO) verifies field cultivation and checks the digital crop survey record.",
            "Step 5: DBT Cash Incentive Disbursement - Upon successful verification, the Rs. 10,000 per hectare financial incentive is credited directly into your Aadhaar-linked bank account.",
        ],
        "duration": "Seasonal incentive per hectare",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-seedling",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Karnataka Farm Mechanization Support",
        "description": "State agricultural engineering initiative subsidizing modern farming equipment, tractors, power tillers, and custom hiring center implements to boost farm productivity.",
        "type": "state",
        "beneficiary": "general",
        "benefits": "Up to 50% to 75% financial subsidy on agricultural machinery including tractors, power tillers, rotavators, seed-cum-fertilizer drills, multi-crop threshers, and plant protection sprayers. Additional 10% subsidy bonus for SC/ST farmers.",
        "eligibility": "All registered farmers in Karnataka holding agricultural land. Priority given to small/marginal farmers and those who have not availed farm machinery subsidy under the department in the past 5 to 7 years.",
        "documents_required": [
            "Aadhaar Card",
            "Land Records (RTC / Pahani copy)",
            "FRUITS Portal Farmer ID (FID)",
            "Bank Account Passbook copy",
            "Caste / Category Certificate (for SC/ST/OBC farmers claiming higher subsidy percentages)",
            "Quotation from Department-Empanelled Machinery Manufacturer/Dealer",
        ],
        "steps_to_apply": [
            "Step 1: Select Approved Machinery & Vendor - Choose the required equipment from the official Karnataka Agriculture Department empanelled rate-contract list and obtain a quotation from an authorized dealer.",
            "Step 2: Submit Application via RSK / DBT Portal - Apply online through the Karnataka DBT Portal or submit physical application with quotation and RTC at the local Raitha Samparka Kendra (RSK).",
            "Step 3: Seniority & Approval Sanction (Permit Order) - Applications are processed based on target allocation and seniority. Once approved, the department issues a formal Purchase Permit (Work Order).",
            "Step 4: Purchase & Vendor Billing - Purchase the machinery by paying your farmer contribution share to the dealer within the stipulated validity period (usually 30 days) and obtain the GST invoice with engine/chassis numbers.",
            "Step 5: Physical Verification & Subsidy Settlement - The Agriculture Officer inspects the machinery, records serial numbers and geotagged farmer photo with the implement, and releases the subsidy directly to the vendor or farmer bank account.",
        ],
        "duration": "Annual target-based scheme",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-tractor",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Bhoochetana",
        "description": "Soil health enhancement and yield-gap reduction program providing subsidized micronutrients and soil amendments directly to Karnataka farmers.",
        "type": "state",
        "beneficiary": "general",
        "benefits": "Supply of essential soil amendments and secondary/micronutrients (Gypsum, Zinc Sulphate, Borax, and bio-fertilizers/vermicompost) at 50% subsidized rates directly through Raitha Samparka Kendras (RSKs) to bridge nutrient deficiencies and increase yield by 20-30%.",
        "eligibility": "All farmers across Karnataka whose soil test reports or regional soil fertility maps indicate deficiencies in Zinc, Boron, Sulphur, or Organic Carbon.",
        "documents_required": [
            "Aadhaar Card",
            "FRUITS Farmer ID (FID) / RTC copy",
            "Soil Health Card or RSK Nutrient Recommendation Slip",
        ],
        "steps_to_apply": [
            "Step 1: Check Nutrient Recommendation - Consult your farm's Soil Health Card or ask the Agriculture Officer at the local Raitha Samparka Kendra (RSK) about specific soil deficiencies in your Hobli.",
            "Step 2: Visit RSK During Input Distribution Window - Visit the RSK before sowing season (Kharif/Rabi) when subsidized agricultural inputs and micronutrient bags are stocked.",
            "Step 3: Biometric Authentication & Indent Generation - Provide your FRUITS ID and Aadhaar for biometric/OTP verification on the department Point of Sale (PoS) system.",
            "Step 4: Pay 50% Farmer Cost Share - Pay only 50% of the government rate for the prescribed quantity of Gypsum, Zinc Sulphate, and Boron bags.",
            "Step 5: Field Application - Mix the micronutrients with farmyard manure or soil during basal dressing or land preparation as per the technical dosage chart provided by the RSK agronomist.",
        ],
        "duration": "Seasonal input distribution",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-leaf",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
]


def normalize_text_list(value: Optional[Iterable[str] | str]) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]

    text_value = str(value).strip()
    if not text_value:
        return []

    try:
        parsed = json.loads(text_value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (TypeError, ValueError, json.JSONDecodeError):
        pass

    if "\n" in text_value:
        return [line.strip(" -\t\r") for line in text_value.splitlines() if line.strip(" -\t\r")]

    return [item.strip() for item in text_value.split(",") if item.strip()]


def serialize_text_list(items: Optional[Iterable[str] | str]) -> Optional[str]:
    normalized_items = normalize_text_list(items)
    if not normalized_items:
        return None
    return json.dumps(normalized_items)


def scheme_to_payload(scheme: Scheme) -> dict:
    return {
        "id": scheme.id,
        "title": scheme.title,
        "description": scheme.description or "Scheme details are available from the official source.",
        "type": scheme.type or "national",
        "beneficiary": scheme.beneficiary or "general",
        "benefits": scheme.benefits or "Refer to the official scheme guidance.",
        "eligibility": scheme.eligibility or "Check the official eligibility criteria before applying.",
        "documents_required": normalize_text_list(scheme.documents_required),
        "steps_to_apply": normalize_text_list(scheme.steps_to_apply),
        "duration": scheme.duration or "Refer to official notification",
        "official_link": scheme.official_link or "#",
        "icon": scheme.icon or "fas fa-hand-holding-heart",
        "state": scheme.state,
        "district": scheme.district,
        "is_active": bool(scheme.is_active),
        "created_at": scheme.created_at,
        "updated_at": scheme.updated_at,
    }
