import json
import logging
from typing import Dict, Any, Optional
from ..schemas.land_lease import LandLeaseInputSchema
from ..utils.ai import _post_groq_chat, _extract_json_object

logger = logging.getLogger(__name__)


def generate_land_lease_ai_assessment(
    input_data: LandLeaseInputSchema,
    valuation: Dict[str, Any],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calls Groq AI to generate a detailed strategic land lease assessment based on
    the land characteristics and the deterministic valuation numbers.
    Returns a structured dictionary with AI insights.
    """
    min_price = valuation["calculated_min_price"]
    max_price = valuation["calculated_max_price"]
    per_acre_min = valuation["per_acre_min"]
    per_acre_max = valuation["per_acre_max"]
    confidence = valuation["confidence_score"]
    acres = valuation["acres"]

    # Fallback response template
    fallback_response = {
        "summary": (
            f"Based on our agricultural valuation analysis for {acres} acres of land in {input_data.district}, Karnataka, "
            f"the estimated annual lease value ranges between Rs. {min_price:,.0f} and Rs. {max_price:,.0f} "
            f"(Rs. {per_acre_min:,.0f} – Rs. {per_acre_max:,.0f} per acre/year)."
        ),
        "estimated_range_explanation": (
            f"This range reflects the baseline agricultural lease rate in {input_data.district} adjusted for key characteristics "
            f"such as water availability ({input_data.water_availability}), electricity supply, road accessibility ({input_data.road_access}), "
            f"and infrastructure features."
        ),
        "positive_factors": [
            f"Location in {input_data.district} with established cropping suitability.",
            f"Irrigation setup ({input_data.water_availability}) enhancing crop security.",
            f"Road accessibility ({input_data.road_access}) facilitating logistics."
        ],
        "negative_factors": [
            "Local seasonal weather fluctuations and rainfall dependency.",
            "Market price variations for harvested agricultural commodities."
        ],
        "important_considerations": [
            "Ensure clear boundary verification and survey matching before signing the lease agreement.",
            "Formulate clear written lease terms regarding electricity bill payments and equipment maintenance."
        ],
        "recommendations": [
            "Utilize the recommended range as a fair starting baseline during lessor-lessee negotiations.",
            "Execute a legally registered lease agreement specifying lease duration, escalation clauses, and permitted land use."
        ],
        "assumptions": [
            "Land is free from legal disputes and encumbrances.",
            "Standard agricultural practices and soil conservation will be followed by the lessee."
        ],
        "disclaimer": (
            "This AI-generated land lease estimation is provided for informational and guidance purposes only. "
            "Actual lease transactions may vary based on hyper-local demand, spot negotiations, and specific property features."
        )
    }

    if not api_key:
        logger.info("No Groq API key provided. Returning structured valuation assessment fallback.")
        return fallback_response

    system_prompt = (
        "You are an expert agricultural economist, land valuation specialist, and farming consultant in Karnataka, India.\n"
        "You must analyze agricultural land parameters and produce a detailed strategic assessment in valid JSON format.\n"
        "CRITICAL RULE: The numerical lease range has already been algorithmically computed by our valuation model. "
        "DO NOT alter or contradict the provided numbers. Base your analysis entirely on explaining these exact numbers. "
        "Use 'Rs.' for Indian Rupees currency formatting."
    )

    infra_str = ", ".join(input_data.infrastructure) if input_data.infrastructure else "None specified"

    user_prompt = f"""
    Please generate a comprehensive Land Lease Assessment JSON for the following agricultural property:

    --- LAND DETAILS ---
    State: {input_data.state}
    District: {input_data.district}
    Taluk/Village: {input_data.taluk or 'N/A'} / {input_data.village or 'N/A'}
    Total Area: {input_data.input_size} {input_data.input_unit} ({acres} Acres normalized)
    Land Type: {input_data.land_type}
    Soil Type: {input_data.soil_type}
    Current Use: {input_data.current_use}
    Intended Crop / Use: {input_data.intended_use}
    Water Availability: {input_data.water_availability} (Source: {input_data.water_source or 'N/A'}, System: {input_data.irrigation_type or 'N/A'})
    Electricity: {'Available (' + str(input_data.electricity_reliability) + ')' if input_data.electricity_available else 'No direct connection'}
    Road & Transport Access: {input_data.road_access} ({input_data.transport_access or 'Standard'})
    Infrastructure On-Site: {infra_str}
    Lease Term Duration: {input_data.lease_duration_years} Years

    --- DETERMINISTIC VALUATION RESULTS ---
    Estimated Annual Lease Price: Rs. {min_price:,.0f} - Rs. {max_price:,.0f}
    Estimated Rate Per Acre/Year: Rs. {per_acre_min:,.0f} - Rs. {per_acre_max:,.0f} / acre / year
    Confidence Level: {confidence}

    Return ONLY a JSON object with these exact keys:
    {{
        "summary": "2-3 sentence overview of the property's lease potential and market fit",
        "estimated_range_explanation": "Detailed paragraph explaining how location, water, road, and infrastructure justify this specific Rs. {min_price:,.0f} - Rs. {max_price:,.0f} range",
        "positive_factors": ["List of 3-4 major value-enhancing factors"],
        "negative_factors": ["List of 2-3 constraints or risk factors"],
        "important_considerations": ["List of 3 key operational or legal risks"],
        "recommendations": ["List of 3 strategic recommendations for negotiation and lease terms"],
        "assumptions": ["List of 2-3 key assumptions made during valuation"],
        "disclaimer": "Standard advisory disclaimer statement"
    }}
    """


    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1200,
        "response_format": {"type": "json_object"}
    }

    try:
        raw_text = _post_groq_chat(payload, api_key)
        parsed_json = _extract_json_object(raw_text)

        # Validate required keys
        for required_key in ["summary", "estimated_range_explanation", "positive_factors", "recommendations"]:
            if required_key not in parsed_json:
                raise ValueError(f"AI response missing required key: {required_key}")

        return parsed_json
    except Exception as exc:
        logger.warning(f"Groq AI call failed for land lease assessment: {exc}. Using robust fallback.")
        return fallback_response
