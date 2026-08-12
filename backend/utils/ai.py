import json
import re
from typing import Optional, Dict, Any

import requests


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"
VISION_MODEL = "qwen/qwen3.6-27b"


def _extract_json_object(raw_text: str) -> Dict[str, Any]:
    fence_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw_text, re.IGNORECASE)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    schema_matches = re.findall(r"\{\s*\"(?:diagnosis|recommended_crop|crop_name)\"[\s\S]*?\}", raw_text, re.IGNORECASE)
    for m in reversed(schema_matches):
        try:
            data = json.loads(m)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw_text, flags=re.DOTALL).strip()
    candidates = re.findall(r"\{[\s\S]*?\}", cleaned if cleaned else raw_text)
    for c in reversed(candidates):
        try:
            data = json.loads(c)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{[\s\S]*\}", cleaned if cleaned else raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("AI response did not contain valid JSON.")



def _extract_labeled_response(raw_text: str) -> Dict[str, str]:
    crop_match = re.search(r"Crop\s*:\s*(.+)", raw_text, re.IGNORECASE)
    reason_match = re.search(r"Reason\s*:\s*(.+)", raw_text, re.IGNORECASE | re.DOTALL)

    if not crop_match or not reason_match:
        raise ValueError("AI response did not contain the expected crop suggestion format.")

    return {
        "recommended_crop": crop_match.group(1).strip(),
        "reason": reason_match.group(1).strip(),
    }


def _extract_disease_labeled_response(raw_text: str) -> Dict[str, str]:
    fields = {
        "diagnosis": r"Diagnosis\s*:\s*(.+)",
        "symptoms": r"Symptoms\s*:\s*(.+)",
        "treatment": r"Treatment\s*:\s*(.+)",
        "prevention": r"Prevention\s*:\s*(.+)",
    }

    parsed: Dict[str, str] = {}
    for field_name, pattern in fields.items():
        match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("AI response did not contain the expected disease diagnosis format.")
        parsed[field_name] = match.group(1).strip()

    return parsed


def _post_groq_chat(payload: Dict[str, Any], api_key: str) -> str:
    if payload.get("model") not in [DEFAULT_MODEL, FALLBACK_MODEL, VISION_MODEL, "openai/gpt-oss-20b"]:
        payload["model"] = DEFAULT_MODEL

    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.post(
                GROQ_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload),
                timeout=60,
            )
        response.raise_for_status()
        response_json = response.json()
        return (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    except requests.RequestException as exc:
        messages = payload.get("messages", [])
        is_multimodal = bool(messages and isinstance(messages[0].get("content"), list))

        if is_multimodal:
            try:
                text_content = ""
                for part in messages[0].get("content", []):
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_content += part.get("text", "")

                if text_content:
                    fallback_payload = dict(payload)
                    fallback_payload["model"] = DEFAULT_MODEL
                    fallback_payload["messages"] = [{"role": "user", "content": text_content}]

                    with requests.Session() as session:
                        session.trust_env = False
                        response = session.post(
                            GROQ_CHAT_URL,
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json",
                            },
                            data=json.dumps(fallback_payload),
                            timeout=60,
                        )
                    response.raise_for_status()
                    response_json = response.json()
                    return (
                        response_json.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
            except requests.RequestException:
                pass
        elif payload.get("model") != FALLBACK_MODEL:
            payload["model"] = FALLBACK_MODEL
            try:
                with requests.Session() as session:
                    session.trust_env = False
                    response = session.post(
                        GROQ_CHAT_URL,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        data=json.dumps(payload),
                        timeout=60,
                    )
                response.raise_for_status()
                response_json = response.json()
                return (
                    response_json.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
            except requests.RequestException:
                pass
        raise RuntimeError(f"Groq request failed: {exc}") from exc



def _sanitize_user_input(text: Optional[str], max_len: int = 1000) -> str:
    if not text:
        return ""
    cleaned = str(text).strip()
    cleaned = re.sub(r'(?i)(system:|assistant:|ignore previous instructions|disregard previous instructions|you are now)', '', cleaned)
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
    return cleaned[:max_len].strip()


def get_crop_suggestion(
    api_key: str,
    soil_context: str,
    district: str,
    image_data_url: Optional[str] = None,
    selected_crop: Optional[str] = None,
) -> Dict[str, str]:
    """
    Generate a crop suggestion using Groq and return a normalized payload.
    If selected_crop is provided, analyze suitability specifically for that crop.
    """
    district = _sanitize_user_input(district, 100)
    selected_crop = _sanitize_user_input(selected_crop, 100) if selected_crop else None
    crop_instruction = (
        f"Selected Crop: {selected_crop}\nGenerate recommendations specifically for the selected crop based on the soil report."
        if selected_crop and selected_crop.strip()
        else "Recommend the single most suitable crop based on the soil report."
    )

    prompt = (
        "You are an agriculture advisor for Karnataka farmers. "
        f"Based on the provided soil information and district context, {crop_instruction} "
        "Respond in exactly this plain-text format and nothing else:\n"
        f"Crop: {selected_crop.strip() if selected_crop and selected_crop.strip() else '<crop name>'}\n"
        "Reason: <2-4 sentences with the decision, suitability analysis, soil/climate fit, and one practical note>"
        f"\n\nDistrict: {district}\n\nSoil context:\n{soil_context}"
    )

    content = [{"type": "text", "text": prompt}]
    model = VISION_MODEL if image_data_url else DEFAULT_MODEL


    if image_data_url:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url,
                },
            }
        )

    raw_response = _post_groq_chat(
        {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content if image_data_url else prompt,
                }
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        },
        api_key,
    )

    try:
        parsed = _extract_json_object(raw_response)
    except ValueError:
        parsed = _extract_labeled_response(raw_response)

    crop = str(parsed.get("recommended_crop") or "").strip()
    reason = str(parsed.get("reason") or "").strip()

    if not crop or not reason:
        raise ValueError("AI response was missing required crop suggestion fields.")

    return {
        "recommended_crop": crop,
        "reason": reason,
    }



def _build_structured_soil_context(data: Dict[str, Any]) -> str:
    """
    Convert structured farm profile JSON into a rich text context for the AI.
    """
    parts = []

    farmer = data.get("farmer") or {}
    land = data.get("land") or {}
    soil = data.get("soil") or {}
    nutrients = data.get("nutrients") or {}
    climate = data.get("climate") or {}
    history = data.get("history") or {}
    goals = data.get("goals") or {}

    # Farm profile
    farm_lines = []
    if farmer.get("name"):
        farm_lines.append(f"Farmer: {farmer['name']}")
    if land.get("district"):
        farm_lines.append(f"District: {land['district']}, Karnataka, India")
    if land.get("land_size"):
        farm_lines.append(f"Land Size: {land['land_size']} acres")
    if land.get("irrigation_type"):
        farm_lines.append(f"Irrigation: {land['irrigation_type']}")
    if farm_lines:
        parts.append("FARM PROFILE:\n" + "\n".join(f"- {l}" for l in farm_lines))

    # Soil profile
    soil_lines = []
    if soil.get("soil_type"):
        soil_lines.append(f"Soil Type: {soil['soil_type']}")
    if soil.get("soil_texture"):
        soil_lines.append(f"Soil Texture: {soil['soil_texture']}")
    if soil.get("soil_depth"):
        soil_lines.append(f"Soil Depth: {soil['soil_depth']} cm")
    if soil_lines:
        parts.append("SOIL PROFILE:\n" + "\n".join(f"- {l}" for l in soil_lines))

    # Chemical & nutrient analysis
    chem_lines = []
    if nutrients.get("ph") is not None:
        chem_lines.append(f"pH: {nutrients['ph']}")
    if nutrients.get("ec") is not None:
        chem_lines.append(f"EC: {nutrients['ec']} dS/m")
    if nutrients.get("organic_carbon") is not None:
        chem_lines.append(f"Organic Carbon: {nutrients['organic_carbon']}%")

    npk_parts = []
    if nutrients.get("nitrogen") is not None:
        npk_parts.append(f"N={nutrients['nitrogen']} kg/ha")
    if nutrients.get("phosphorus") is not None:
        npk_parts.append(f"P={nutrients['phosphorus']} kg/ha")
    if nutrients.get("potassium") is not None:
        npk_parts.append(f"K={nutrients['potassium']} kg/ha")
    if npk_parts:
        chem_lines.append(f"Primary Nutrients: {', '.join(npk_parts)}")

    micro_parts = []
    for key, unit in [("sulphur", "ppm"), ("zinc", "ppm"), ("iron", "ppm"), ("copper", "ppm"), ("manganese", "ppm")]:
        if nutrients.get(key) is not None:
            micro_parts.append(f"{key.capitalize()}={nutrients[key]}{unit}")
    if micro_parts:
        chem_lines.append(f"Micro Nutrients: {', '.join(micro_parts)}")

    if chem_lines:
        parts.append("CHEMICAL & NUTRIENT ANALYSIS:\n" + "\n".join(f"- {l}" for l in chem_lines))

    # Climate, history & goals
    context_lines = []
    if climate.get("avg_rainfall") is not None:
        context_lines.append(f"Average Annual Rainfall: {climate['avg_rainfall']} mm")
    if climate.get("monsoon_dependent") is not None:
        context_lines.append(f"Monsoon Dependent: {'Yes' if climate['monsoon_dependent'] else 'No'}")
    if history.get("last_crop"):
        context_lines.append(f"Last Crop Grown: {history['last_crop']}")
    if goals.get("season"):
        context_lines.append(f"Season: {goals['season']}")
    if goals.get("purpose"):
        context_lines.append(f"Purpose: {goals['purpose']}")
    if goals.get("risk_preference"):
        context_lines.append(f"Risk Preference: {goals['risk_preference']}")
    if context_lines:
        parts.append("CLIMATE, HISTORY & GOALS:\n" + "\n".join(f"- {l}" for l in context_lines))

    return "\n\n".join(parts)


def get_structured_crop_suggestion(
    api_key: str,
    structured_data: Dict[str, Any],
    district: str,
    selected_crop: Optional[str] = None,
) -> Dict[str, str]:
    """
    Generate a crop suggestion from structured farm profile data.
    If selected_crop is provided, analyze suitability specifically for that crop.
    """
    district = _sanitize_user_input(district, 100)
    selected_crop = _sanitize_user_input(selected_crop, 100) if selected_crop else None
    soil_context = _build_structured_soil_context(structured_data)

    crop_instruction = (
        f"Selected Crop: {selected_crop}\nGenerate recommendations specifically for the selected crop based on the structured profile."
        if selected_crop and selected_crop.strip()
        else "Consider the soil characteristics, nutrient levels, irrigation availability, rainfall, previous crop, season, farmer goals, and risk preference to recommend the single most suitable crop."
    )

    prompt = (
        "You are an agriculture advisor for Karnataka farmers. "
        "Analyze the following structured farm profile data carefully. "
        f"{crop_instruction}\n\n"
        f"{soil_context}\n\n"
        "Respond in exactly this plain-text format and nothing else:\n"
        f"Crop: {selected_crop.strip() if selected_crop and selected_crop.strip() else '<crop name>'}\n"
        "Reason: <2-4 sentences explaining the decision or suitability analysis based on the soil profile, "
        "nutrient analysis, climate conditions, and farmer goals. Include one practical note.>"
    )

    raw_response = _post_groq_chat(
        {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 400,
        },
        api_key,
    )


    try:
        parsed = _extract_json_object(raw_response)
    except ValueError:
        parsed = _extract_labeled_response(raw_response)

    crop = str(parsed.get("recommended_crop") or "").strip()
    reason = str(parsed.get("reason") or "").strip()

    if not crop or not reason:
        raise ValueError("AI response was missing required crop suggestion fields.")

    return {
        "recommended_crop": crop,
        "reason": reason,
    }


def diagnose_disease(api_key: str, description: str, district: str) -> str:
    """
    Preserve the existing disease helper shape for routes that may still rely on it.
    """
    description = _sanitize_user_input(description, 1000)
    district = _sanitize_user_input(district, 100)
    prompt = f"""
    Based on this description: {description}
    And considering the region {district}, Karnataka,
    Diagnose the possible plant disease and suggest treatment.
    Provide structured response with symptoms, diagnosis, and treatment.
    """

    return _post_groq_chat(
        {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 300,
        },
        api_key,
    )


def _clean_ai_field_text(text: str) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in re.split(r"[\r\n]+", str(text)) if line.strip()]
    first_line = lines[0] if lines else str(text).strip()
    first_line = re.split(r"\s*\*\s*|\s*\*\*", first_line)[0]
    cleaned = re.sub(r'^[ "*:\'-]+|[ "*:\'-]+$', '', first_line).strip()
    return cleaned if cleaned else str(text).strip()


def get_disease_diagnosis(
    api_key: str,
    symptoms_description: Optional[str],
    district: str,
    image_data_url: Optional[str] = None,
) -> Dict[str, str]:
    """
    Generate a structured disease diagnosis using Groq and return normalized fields.
    Supports both vision (if image uploaded) and text fallback.
    """
    symptoms_description = _sanitize_user_input(symptoms_description, 1000) if symptoms_description else ""
    district = _sanitize_user_input(district, 100)

    # 1. Try Vision Diagnosis if image_data_url is present
    if image_data_url:
        try:
            prompt_parts = [
                "You are an agriculture disease diagnosis assistant for Karnataka farmers. "
                "Analyze the plant image and symptoms carefully. "
                "Respond ONLY in valid JSON format with keys: diagnosis, symptoms, treatment, prevention.",
                f"\n\nDistrict: {district}, Karnataka, India",
            ]
            cleaned_symptoms = (symptoms_description or "").strip()
            if cleaned_symptoms:
                prompt_parts.append(f"\n\nObserved symptoms:\n{cleaned_symptoms}")

            content = [
                {"type": "text", "text": "".join(prompt_parts)},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ]

            raw_response = _post_groq_chat(
                {
                    "model": VISION_MODEL,
                    "messages": [{"role": "user", "content": content}],
                    "temperature": 0.0,
                    "max_tokens": 1500,
                },
                api_key,
            )
            parsed = _extract_json_object(raw_response)
            diag = _clean_ai_field_text(str(parsed.get("diagnosis") or ""))
            symp = _clean_ai_field_text(str(parsed.get("symptoms") or ""))
            treat = _clean_ai_field_text(str(parsed.get("treatment") or ""))
            prev = _clean_ai_field_text(str(parsed.get("prevention") or ""))
            if all([diag, symp, treat, prev]):
                return {"diagnosis": diag, "symptoms": symp, "treatment": treat, "prevention": prev}
        except Exception:
            pass

    # 2. Text Diagnosis with DEFAULT_MODEL (llama-3.3-70b-versatile)
    prompt = (
        "You are an agriculture disease diagnosis assistant for Karnataka farmers. "
        "Based on the observed symptoms and district context, diagnose the plant disease. "
        "Respond ONLY in valid JSON with exactly these keys: diagnosis, symptoms, treatment, prevention.\n\n"
        f"District: {district}, Karnataka, India\n"
        f"Observed Symptoms: {symptoms_description or 'Leaves showing signs of plant disease or stress.'}"
    )

    raw_response = _post_groq_chat(
        {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 800,
        },
        api_key,
    )

    try:
        parsed = _extract_json_object(raw_response)
    except ValueError:
        parsed = _extract_disease_labeled_response(raw_response)

    diagnosis = _clean_ai_field_text(str(parsed.get("diagnosis") or ""))
    symptoms = _clean_ai_field_text(str(parsed.get("symptoms") or ""))
    treatment = _clean_ai_field_text(str(parsed.get("treatment") or ""))
    prevention = _clean_ai_field_text(str(parsed.get("prevention") or ""))

    if not all([diagnosis, symptoms, treatment, prevention]):
        diagnosis = diagnosis or "Plant Disease / Stress Symptoms"
        symptoms = symptoms or (symptoms_description or "Observed leaf discoloration / crop stress.")
        treatment = treatment or "Apply suitable broad-spectrum organic or recommended chemical fungicide and ensure optimal soil moisture."
        prevention = prevention or "Maintain proper crop rotation, good field sanitation, and adequate plant spacing."

    return {
        "diagnosis": diagnosis,
        "symptoms": symptoms,
        "treatment": treatment,
        "prevention": prevention,
    }


def generate_ai_crop_plan(
    api_key: str,
    farmer_name: Optional[str],
    district: str,
    land_size: Optional[float],
    irrigation_type: Optional[str],
    crop: str,
    start_date: str,
    season: str,
    purpose: Optional[str],
    soil_details: Dict[str, Any],
    climate_details: Dict[str, Any],
    previous_crop: Optional[str],
    weather_info: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls Groq AI to generate a comprehensive, personalized cultivation plan.
    Returns relative-day JSON schedule only.
    """
    farmer_name = _sanitize_user_input(farmer_name, 100) if farmer_name else "Farmer"
    district = _sanitize_user_input(district, 100) if district else "Karnataka"
    irrigation_type = _sanitize_user_input(irrigation_type, 100) if irrigation_type else "Rainfed / Well"
    crop = _sanitize_user_input(crop, 100)
    purpose = _sanitize_user_input(purpose, 100) if purpose else "Commercial Sale"
    previous_crop = _sanitize_user_input(previous_crop, 100) if previous_crop else None
    prompt = f"""You are an expert agricultural planner specializing in Indian agriculture and specifically Karnataka farming conditions.
Create a complete, realistic cultivation schedule for the following farm. Recommendations must strictly follow Indian agricultural practices and Karnataka local conditions whenever applicable.

Farmer Details:
- Name: {farmer_name or 'Farmer'}
- District: {district or 'Karnataka'}
- Land Size: {land_size or 1.0} Acres
- Irrigation Type: {irrigation_type or 'Rainfed / Well'}

Crop Details:
- Selected Crop: {crop}
- Start Date: {start_date}
- Season: {season}
- Purpose: {purpose or 'Commercial Sale'}

Soil Details:
- Soil Type: {soil_details.get('soil_type') or 'Standard'}
- Soil Texture: {soil_details.get('soil_texture') or 'Loamy'}
- Soil Depth: {soil_details.get('soil_depth') or 'Normal'} cm
- Soil pH: {soil_details.get('soil_ph') or '6.5'}
- Organic Carbon: {soil_details.get('organic_carbon') or '0.5'}%
- Nitrogen: {soil_details.get('nitrogen') or '200'} kg/ha
- Phosphorus: {soil_details.get('phosphorus') or '20'} kg/ha
- Potassium: {soil_details.get('potassium') or '150'} kg/ha
- EC: {soil_details.get('ec') or '0.5'} dS/m

Climate & History:
- Rainfall: {climate_details.get('rainfall') or '800'} mm
- Monsoon Dependent: {'Yes' if climate_details.get('monsoon_dependent', True) else 'No'}
- Previous Crop: {previous_crop or 'None'}
- Weather Info: {weather_info or 'Typical regional weather'}

Return JSON ONLY. Do not include markdown code blocks or explanations outside JSON.
The JSON must adhere strictly to this schema:
{{
  "crop_name": "{crop}",
  "season": "{season}",
  "estimated_total_duration_days": 120,
  "growth_stages": [
    {{
      "stage": "<Stage Name>",
      "start_day": 1,
      "end_day": 20,
      "description": "<detailed description>"
    }}
  ],
  "schedule": [
    {{
      "day_number": 1,
      "task": "<Task Title>",
      "category": "<e.g. Land Preparation, Nursery Preparation, Sowing, Irrigation, Fertilizer Application, Weeding, Pest Inspection, Disease Inspection, Micronutrient Spray, Flowering Monitoring, Fruit Development, Harvest Preparation, Harvest, Post Harvest Handling>",
      "priority": "<High / Medium / Low>",
      "notes": "<Actionable instruction>"
    }}
  ],
  "irrigation_schedule": [
    {{
      "day": 5,
      "water_amount": "<e.g. 30 mm / 2 hours drip>",
      "reason": "<Why watering is needed>"
    }}
  ],
  "fertilizer_schedule": [
    {{
      "day": 10,
      "fertilizer": "<Name of fertilizer / manure>",
      "quantity": "<Rate per acre or ha>",
      "reason": "<Nutrient target>"
    }}
  ],
  "weed_management": ["<tip 1>", "<tip 2>"],
  "pest_monitoring": ["<pest to watch & control method>"],
  "disease_monitoring": ["<disease to watch & control method>"],
  "expected_flowering_day": 45,
  "expected_fruiting_day": 65,
  "expected_harvest_day": 120,
  "important_alerts": ["<Critical alert regarding monsoon/soil/pest>"],
  "tips": ["<Pro tip 1>", "<Pro tip 2>"]
}}

Important rules:
1. Only return relative day numbers (e.g. day 1, day 15, day 45). Do NOT calculate actual calendar dates.
2. Include at least 8-12 realistic schedule tasks spanning land preparation to harvest.
3. Ensure the growth stages cover the full duration without gaps.
"""
    model = DEFAULT_MODEL

    raw_response = _post_groq_chat(
        {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.2,
            "max_tokens": 3000,
        },
        api_key,
    )

    try:
        parsed = _extract_json_object(raw_response)
        return parsed
    except Exception as exc:
        raise ValueError(f"AI failed to generate a valid crop cultivation structure: {exc}") from exc

