import json
from typing import Iterable, List, Optional

from ..models.scheme import Scheme


DEFAULT_SCHEMES = [
    {
        "title": "PM-KISAN Samman Nidhi",
        "description": "Income support scheme for eligible farmer families through direct benefit transfer.",
        "type": "national",
        "beneficiary": "small",
        "benefits": "Rs. 6,000 per year in three installments.",
        "eligibility": "Landholding farmer families, subject to central government exclusions.",
        "documents_required": ["Aadhaar card", "Bank account details", "Land records"],
        "steps_to_apply": [
            "Visit the PM-KISAN portal or nearest agriculture office.",
            "Submit Aadhaar, bank details, and land ownership records.",
            "Complete beneficiary verification.",
            "Track payment status through the official portal.",
        ],
        "duration": "Ongoing",
        "official_link": "https://pmkisan.gov.in/",
        "icon": "fas fa-rupee-sign",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance support for notified crops against yield losses and localized risks.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Insurance coverage for crop loss subject to notified crop and season rules.",
        "eligibility": "Farmers cultivating notified crops in notified areas.",
        "documents_required": ["Aadhaar card", "Bank passbook", "Land record or cultivation proof", "Sowing details"],
        "steps_to_apply": [
            "Check whether your crop and area are notified for the season.",
            "Apply through the official portal, bank, or Common Service Center.",
            "Submit land and sowing details before the deadline.",
            "Report losses within the prescribed timeline if crop damage occurs.",
        ],
        "duration": "Seasonal enrollment",
        "official_link": "https://pmfby.gov.in/",
        "icon": "fas fa-shield-alt",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Kisan Credit Card",
        "description": "Institutional credit support for crop production, allied activities, and working capital needs.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Access to short-term agricultural credit through participating banks.",
        "eligibility": "Farmers, tenant farmers, sharecroppers, and eligible allied-sector beneficiaries as per bank norms.",
        "documents_required": ["Identity proof", "Address proof", "Land or cultivation records", "Passport-size photo"],
        "steps_to_apply": [
            "Approach a participating bank branch or apply through the official KCC process.",
            "Submit identity, address, and cultivation details.",
            "Complete bank verification and credit assessment.",
            "Receive the sanctioned KCC limit and card access.",
        ],
        "duration": "Renewable credit facility",
        "official_link": "https://www.myscheme.gov.in/schemes/kcc",
        "icon": "fas fa-credit-card",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Soil Health Card Scheme",
        "description": "Soil testing program that helps farmers improve nutrient management and crop planning.",
        "type": "national",
        "beneficiary": "general",
        "benefits": "Field-specific soil nutrient recommendations and soil health reporting.",
        "eligibility": "Farmers seeking soil testing support through agriculture department channels.",
        "documents_required": ["Land details", "Farmer ID proof", "Soil sample information"],
        "steps_to_apply": [
            "Contact the local agriculture office or soil testing center.",
            "Submit the soil sample following the recommended method.",
            "Register the sample with land and farmer details.",
            "Collect the soil health report and follow nutrient guidance.",
        ],
        "duration": "Periodic testing support",
        "official_link": "https://soilhealth.dac.gov.in/",
        "icon": "fas fa-vial",
        "state": None,
        "district": None,
        "is_active": True,
    },
    {
        "title": "Krishi Bhagya",
        "description": "Karnataka support program focused on farm ponds and rainwater conservation for dryland farmers.",
        "type": "state",
        "beneficiary": "small",
        "benefits": "Support for water harvesting structures and related conservation components.",
        "eligibility": "Eligible Karnataka farmers, especially in rain-fed and dryland areas, subject to state norms.",
        "documents_required": ["Aadhaar card", "RTC or land records", "Bank account details", "Passport-size photo"],
        "steps_to_apply": [
            "Visit the local Raitha Samparka Kendra or Karnataka agriculture office.",
            "Submit land and identity documents for scheme screening.",
            "Complete field verification by department staff.",
            "Receive approval and proceed as per department guidance.",
        ],
        "duration": "State program cycle",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-water",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Raitha Siri",
        "description": "Karnataka support initiative for eligible small and marginal farmers to improve cultivation capacity.",
        "type": "state",
        "beneficiary": "marginal",
        "benefits": "State support targeted at resource-constrained farmers under notified conditions.",
        "eligibility": "Eligible small and marginal farmers in Karnataka as notified by the state.",
        "documents_required": ["Aadhaar card", "Land records", "Income or category proof if applicable", "Bank account details"],
        "steps_to_apply": [
            "Check current eligibility guidance with the local agriculture office.",
            "Submit application through the notified Karnataka agriculture channel.",
            "Attach land, identity, and bank details.",
            "Await verification and sanction communication.",
        ],
        "duration": "As per state notification",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-seedling",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Bhoochetana",
        "description": "Karnataka soil and productivity improvement program promoting balanced nutrient management and extension support.",
        "type": "state",
        "beneficiary": "general",
        "benefits": "Agronomic support for improving soil fertility and farm productivity.",
        "eligibility": "Farmers in Karnataka covered by the notified implementation areas.",
        "documents_required": ["Aadhaar card", "Land records", "Bank details if subsidy-linked", "Crop details"],
        "steps_to_apply": [
            "Visit the local agriculture office or Raitha Samparka Kendra.",
            "Register your land and crop details.",
            "Participate in field guidance or department screening.",
            "Follow the approved package or support channel provided.",
        ],
        "duration": "Season-based implementation",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-leaf",
        "state": "Karnataka",
        "district": None,
        "is_active": True,
    },
    {
        "title": "Karnataka Farm Mechanization Support",
        "description": "State assistance for eligible farmers adopting approved agricultural machinery and equipment.",
        "type": "state",
        "beneficiary": "general",
        "benefits": "Subsidy support on approved implements and mechanization components as per state norms.",
        "eligibility": "Eligible farmers in Karnataka applying through the agriculture department process.",
        "documents_required": ["Aadhaar card", "Land records", "Quotation or invoice", "Bank account details"],
        "steps_to_apply": [
            "Review the approved machinery list and subsidy norms.",
            "Apply through the notified Karnataka agriculture portal or office.",
            "Upload or submit land, identity, and equipment documents.",
            "Complete verification and claim processing after approval.",
        ],
        "duration": "Annual or notification-based",
        "official_link": "https://raitamitra.karnataka.gov.in/",
        "icon": "fas fa-tractor",
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
