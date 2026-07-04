import json
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import HTTPException

from ..models.crop_plan import CropPlan


PLANNER_CROP_LIBRARY = {
    "rice": {"label": "Rice", "duration_days": 125, "category": "cereal"},
    "ragi": {"label": "Ragi", "duration_days": 115, "category": "cereal"},
    "maize": {"label": "Maize", "duration_days": 120, "category": "cereal"},
    "jowar": {"label": "Jowar", "duration_days": 115, "category": "cereal"},
    "groundnut": {"label": "Groundnut", "duration_days": 120, "category": "pulse"},
    "sugarcane": {"label": "Sugarcane", "duration_days": 330, "category": "cash"},
    "cotton": {"label": "Cotton", "duration_days": 180, "category": "cash"},
    "banana": {"label": "Banana", "duration_days": 330, "category": "fruit"},
    "coconut": {"label": "Coconut", "duration_days": 365, "category": "plantation"},
    "coffee": {"label": "Coffee", "duration_days": 270, "category": "plantation"},
    "tomato": {"label": "Tomato", "duration_days": 130, "category": "vegetable"},
}

STAGE_LIBRARY = {
    "cereal": [
        ("Field preparation", 0.16, "Prepare the seedbed and stabilize field moisture before crop establishment."),
        ("Establishment", 0.18, "Build a uniform stand and correct early stress quickly."),
        ("Vegetative growth", 0.26, "Drive canopy growth with split nutrition and weed control."),
        ("Reproductive phase", 0.22, "Protect flowering, grain set, and disease-sensitive stages."),
        ("Maturity and harvest", 0.18, "Finish cleanly and harvest at the right grain moisture."),
    ],
    "pulse": [
        ("Land preparation", 0.17, "Prepare loose, well-drained soil for root spread and pegging."),
        ("Early establishment", 0.18, "Protect emergence and avoid stand loss in the first weeks."),
        ("Vegetative spread", 0.24, "Support leaf growth and maintain balanced moisture."),
        ("Flowering and pod set", 0.23, "Protect reproductive growth from disease and moisture stress."),
        ("Pod fill and harvest", 0.18, "Harvest only after maturity checks confirm pod readiness."),
    ],
    "cash": [
        ("Field setup and planting", 0.15, "Prepare the field thoroughly and establish strong planting rows."),
        ("Stand build-up", 0.19, "Correct gaps and reduce early weed and pest competition."),
        ("Vegetative expansion", 0.24, "Push biomass growth with disciplined irrigation and nutrients."),
        ("Yield formation", 0.24, "Protect the crop while the economic yield component develops."),
        ("Maturity and harvest", 0.18, "Plan harvest timing for quality, transport, and low loss."),
    ],
    "fruit": [
        ("Pit preparation and planting", 0.12, "Set up healthy planting pits, drainage, and immediate irrigation."),
        ("Establishment care", 0.18, "Strengthen root anchorage and replace weak plants early."),
        ("Vegetative build-up", 0.28, "Drive canopy growth and maintain balanced basin nutrition."),
        ("Yield development", 0.24, "Protect bunch or fruit development from stress and lodging."),
        ("Harvest window", 0.18, "Harvest at the right maturity stage for handling and market quality."),
    ],
    "plantation": [
        ("Site preparation", 0.14, "Prepare pits, drainage, and long-term root support around the basin."),
        ("Establishment phase", 0.18, "Maintain survival, moisture balance, and early pest watch."),
        ("Vegetative maintenance", 0.26, "Support canopy health and split nutrient application."),
        ("Productive support", 0.24, "Sustain tree health, pest control, and crop load support."),
        ("Harvest cycle", 0.18, "Harvest mature produce and reset the block for the next cycle."),
    ],
    "vegetable": [
        ("Nursery and field preparation", 0.16, "Prepare healthy seedlings and a well-drained transplant field."),
        ("Transplant establishment", 0.18, "Reduce shock and maintain early survival after transplanting."),
        ("Vegetative growth", 0.22, "Support canopy build, staking, and regular nutrient supply."),
        ("Flowering and fruit set", 0.22, "Protect the crop during the most stress-sensitive stage."),
        ("Fruit development and harvest", 0.22, "Maintain fruit quality and harvest in planned rounds."),
    ],
}

TASK_LIBRARY = {
    "Field preparation": ["Prepare the field surface and drainage lines.", "Apply basal inputs before planting.", "Check spacing and planting material readiness."],
    "Establishment": ["Inspect stand uniformity and fill major gaps early.", "Control first-flush weeds before they dominate.", "Monitor for seedling stress, insects, or rot."],
    "Vegetative growth": ["Apply split nutrients based on active crop demand.", "Maintain irrigation balance and avoid prolonged stress.", "Scout for weeds, pests, and nutrient deficiency symptoms."],
    "Reproductive phase": ["Protect flowering and grain or fruit set from stress.", "Inspect closely for disease pressure and insect attack.", "Avoid delayed correction once yield formation starts."],
    "Maturity and harvest": ["Track maturity indicators before fixing harvest.", "Reduce avoidable moisture stress or quality loss near harvest.", "Harvest and dry or handle produce carefully after cutting."],
    "Land preparation": ["Prepare a loose, well-drained bed before sowing.", "Apply soil amendments or basal nutrients.", "Check seed quality and sowing depth consistency."],
    "Early establishment": ["Re-sow or repair major stand gaps quickly.", "Keep early weed pressure under control.", "Watch for shoot damage, root issues, or poor emergence."],
    "Vegetative spread": ["Support active foliage growth with split feeding.", "Maintain friable soil and stable moisture.", "Inspect leaves for disease and deficiency patterns."],
    "Flowering and pod set": ["Avoid sharp moisture swings during flowering.", "Continue pest and disease scouting at short intervals.", "Support reproductive growth with balanced nutrition."],
    "Pod fill and harvest": ["Check maturity physically before harvest.", "Lift or cut carefully to avoid produce loss.", "Dry produce well before storage."],
    "Field setup and planting": ["Prepare rows, furrows, or pits before planting.", "Place healthy planting material at proper spacing.", "Complete starter nutrient application."],
    "Stand build-up": ["Correct major gap patches and remove weak plants.", "Suppress early weed growth before canopy closure.", "Monitor for establishment pests and drainage issues."],
    "Vegetative expansion": ["Maintain steady irrigation through the active growth window.", "Apply split nutrients instead of one heavy dose.", "Review crop vigor across the field each week."],
    "Yield formation": ["Protect the crop during the main yield-building stage.", "Respond quickly to pest or disease hotspots.", "Avoid heavy stress from skipped irrigation or late inputs."],
    "Pit preparation and planting": ["Prepare pits with organic support and good drainage.", "Plant healthy material at the correct depth.", "Water immediately after planting."],
    "Establishment care": ["Replace weak plants where survival is poor.", "Maintain basin moisture without stagnation.", "Inspect for early stem, collar, or leaf damage."],
    "Vegetative build-up": ["Apply nutrients in split rounds around the root zone.", "Regulate excess shoots or canopy crowding where needed.", "Continue field scouting for disease and insect pressure."],
    "Harvest window": ["Check maturity based on crop signs and market target.", "Harvest carefully to reduce bruising or handling loss.", "Move produce quickly for sorting and sale."],
    "Site preparation": ["Prepare pits, mulch, and basin drainage support.", "Plant or reset healthy material only.", "Protect young plants from heat and water stress."],
    "Establishment phase": ["Maintain survival through basin moisture and mulching.", "Inspect for crown, collar, or early beetle or borer issues.", "Correct major basin drainage problems early."],
    "Vegetative maintenance": ["Apply split nutrients around the basin or root zone.", "Keep the basin clean and loosened where needed.", "Monitor leaf health and canopy color regularly."],
    "Productive support": ["Maintain irrigation in dry spells and support crop load.", "Continue sanitation and pest watch through the block.", "Review organic recycling or mulch condition."],
    "Harvest cycle": ["Harvest mature produce at the planned interval.", "Remove damaged or infested material after harvest.", "Prepare the next maintenance round."],
    "Nursery and field preparation": ["Raise healthy seedlings and prepare the transplant field.", "Apply starter nutrients before shifting seedlings.", "Ensure drainage is ready before planting."],
    "Transplant establishment": ["Transplant healthy seedlings at the right spacing.", "Irrigate immediately and reduce transplant shock.", "Watch for wilt, collar issues, and stand loss."],
    "Flowering and fruit set": ["Avoid major moisture swings during flowering.", "Inspect for blossom drop, fruit damage, or foliar disease.", "Keep airflow and canopy health under control."],
    "Fruit development and harvest": ["Support fruit fill with regular irrigation and nutrition.", "Harvest at the right market maturity stage.", "Sort damaged produce and maintain field sanitation."],
}


def get_crop_planner_config(crop_name: str) -> dict:
    crop_key = crop_name.lower().strip()
    if crop_key in PLANNER_CROP_LIBRARY:
        return PLANNER_CROP_LIBRARY[crop_key]

    label = crop_name.strip().title()
    if any(k in crop_key for k in ["gram", "bean", "pea", "lentil", "moong", "urad", "arhar", "soybean", "groundnut", "cowpea", "pulse"]):
        return {"label": label, "duration_days": 110, "category": "pulse"}
    elif any(k in crop_key for k in ["rice", "wheat", "maize", "ragi", "jowar", "bajra", "sorghum", "barley", "oat", "millet", "cereal"]):
        return {"label": label, "duration_days": 120, "category": "cereal"}
    elif any(k in crop_key for k in ["mustard", "sunflower", "safflower", "sesame", "castor", "linseed", "oil", "cotton", "sugarcane", "jute", "tobacco", "fodder", "berseem"]):
        return {"label": label, "duration_days": 130, "category": "cash"}
    elif any(k in crop_key for k in ["mango", "banana", "apple", "orange", "citrus", "guava", "papaya", "grape", "pomegranate", "litchi", "pineapple", "melon", "fruit"]):
        return {"label": label, "duration_days": 180, "category": "fruit"}
    elif any(k in crop_key for k in ["coconut", "coffee", "tea", "rubber", "cashew", "arecanut", "pepper", "cardamom", "turmeric", "ginger", "clove", "cinnamon", "nutmeg"]):
        return {"label": label, "duration_days": 240, "category": "plantation"}
    else:
        return {"label": label, "duration_days": 100, "category": "vegetable"}


def date_to_iso(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def parse_date_value(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def process_ai_crop_plan(ai_json: dict, planting_date: date) -> dict:
    """
    Takes relative-day AI schedule and computes exact calendar dates.
    """
    duration_days = int(ai_json.get("estimated_total_duration_days") or 120)
    harvest_date = planting_date + timedelta(days=duration_days - 1)

    growth_stages = []
    for stage in ai_json.get("growth_stages", []):
        start_day = int(stage.get("start_day") or 1)
        end_day = int(stage.get("end_day") or start_day + 10)
        s_date = planting_date + timedelta(days=start_day - 1)
        e_date = planting_date + timedelta(days=end_day - 1)
        growth_stages.append({
            "stage": stage.get("stage", "Growth"),
            "title": stage.get("stage", "Growth"),
            "start_day": start_day,
            "end_day": end_day,
            "day_range": f"{start_day}-{end_day}",
            "start_date": date_to_iso(s_date),
            "end_date": date_to_iso(e_date),
            "description": stage.get("description", ""),
            "tasks": [],
        })

    schedule = []
    for task in ai_json.get("schedule", []):
        day_num = int(task.get("day_number") or 1)
        t_date = planting_date + timedelta(days=day_num - 1)
        schedule.append({
            "day_number": day_num,
            "calendar_date": date_to_iso(t_date),
            "formatted_date": t_date.strftime("%d %b %Y"),
            "task": task.get("task", "Activity"),
            "category": task.get("category", "General"),
            "priority": task.get("priority", "Medium"),
            "notes": task.get("notes", ""),
        })
    schedule.sort(key=lambda x: x["day_number"])

    irrigation_schedule = []
    for irr in ai_json.get("irrigation_schedule", []):
        day_num = int(irr.get("day") or 1)
        i_date = planting_date + timedelta(days=day_num - 1)
        irrigation_schedule.append({
            "day": day_num,
            "calendar_date": date_to_iso(i_date),
            "formatted_date": i_date.strftime("%d %b %Y"),
            "water_amount": irr.get("water_amount", "Standard"),
            "reason": irr.get("reason", "Moisture maintenance"),
        })
    irrigation_schedule.sort(key=lambda x: x["day"])

    fertilizer_schedule = []
    for fert in ai_json.get("fertilizer_schedule", []):
        day_num = int(fert.get("day") or 1)
        f_date = planting_date + timedelta(days=day_num - 1)
        fertilizer_schedule.append({
            "day": day_num,
            "calendar_date": date_to_iso(f_date),
            "formatted_date": f_date.strftime("%d %b %Y"),
            "fertilizer": fert.get("fertilizer", "Nutrient input"),
            "quantity": fert.get("quantity", "As needed"),
            "reason": fert.get("reason", "Crop nutrition"),
        })
    fertilizer_schedule.sort(key=lambda x: x["day"])

    flowering_day = ai_json.get("expected_flowering_day")
    fruiting_day = ai_json.get("expected_fruiting_day")

    return {
        "ai_generated": True,
        "crop_name": ai_json.get("crop_name", ""),
        "season": ai_json.get("season", ""),
        "estimated_total_duration_days": duration_days,
        "planting_date": date_to_iso(planting_date),
        "estimated_harvest_date": date_to_iso(harvest_date),
        "formatted_harvest_date": harvest_date.strftime("%d %b %Y"),
        "growth_stages": growth_stages,
        "schedule": schedule,
        "irrigation_schedule": irrigation_schedule,
        "fertilizer_schedule": fertilizer_schedule,
        "weed_management": ai_json.get("weed_management", []),
        "pest_monitoring": ai_json.get("pest_monitoring", []),
        "disease_monitoring": ai_json.get("disease_monitoring", []),
        "expected_flowering_day": flowering_day,
        "expected_flowering_date": date_to_iso(planting_date + timedelta(days=int(flowering_day) - 1)) if flowering_day else None,
        "expected_fruiting_day": fruiting_day,
        "expected_fruiting_date": date_to_iso(planting_date + timedelta(days=int(fruiting_day) - 1)) if fruiting_day else None,
        "expected_harvest_day": duration_days,
        "important_alerts": ai_json.get("important_alerts", []),
        "tips": ai_json.get("tips", []),
    }


def build_crop_plan_payload(crop: str, planting_date: date, harvest_date: date, reminders: Optional[dict] = None) -> dict:
    crop_key = crop.lower().strip()
    crop_config = get_crop_planner_config(crop_key)
    duration_days = (harvest_date - planting_date).days + 1
    if duration_days <= 0:
        raise HTTPException(status_code=400, detail="Harvest date must be on or after planting date.")

    stage_defs = STAGE_LIBRARY[crop_config["category"]]
    stages = []
    elapsed_days = 0
    for index, (title, share, description) in enumerate(stage_defs):
        remaining_days = duration_days - elapsed_days
        stage_days = remaining_days if index == len(stage_defs) - 1 else max(1, int(round(duration_days * share)))
        if index != len(stage_defs) - 1:
            stage_days = min(stage_days, duration_days - elapsed_days - (len(stage_defs) - index - 1))
        start_day = elapsed_days + 1
        end_day = elapsed_days + stage_days
        stages.append(
            {
                "title": title,
                "description": description,
                "day_range": f"{start_day}-{end_day}",
                "start_date": date_to_iso(planting_date + timedelta(days=start_day - 1)),
                "end_date": date_to_iso(planting_date + timedelta(days=end_day - 1)),
                "tasks": TASK_LIBRARY[title],
            }
        )
        elapsed_days = end_day

    reminder_payload = reminders or {"watering": False, "fertilizing": False, "pest_control": False, "pruning": False}
    return {
        "crop": crop_key,
        "crop_label": crop_config["label"],
        "planting_date": date_to_iso(planting_date),
        "harvest_date": date_to_iso(harvest_date),
        "duration_days": duration_days,
        "duration_months": round(duration_days / 30, 1),
        "reminders": reminder_payload,
        "stages": stages,
    }


def serialize_crop_plan(plan: CropPlan) -> dict:
    crop_config = get_crop_planner_config(plan.crop)
    today = date.today()
    crop_age_days = (today - plan.planting_date).days + 1
    harvest_countdown = (plan.harvest_date - today).days

    stages_data = json.loads(plan.stages_json or "[]")
    reminders = json.loads(plan.reminders_json or "{}")

    # Check if this is an AI generated plan payload stored inside stages_json
    if isinstance(stages_data, dict) and stages_data.get("ai_generated"):
        ai_plan = stages_data
        growth_stages = ai_plan.get("growth_stages", [])
        schedule = ai_plan.get("schedule", [])
        
        current_stage = None
        for st in growth_stages:
            s_date = parse_date_value(st["start_date"])
            e_date = parse_date_value(st["end_date"])
            if s_date <= today <= e_date:
                current_stage = st
                break
        if not current_stage and growth_stages:
            current_stage = growth_stages[-1] if today > plan.harvest_date else growth_stages[0]

        todays_tasks = [t for t in schedule if t.get("calendar_date") == today.isoformat()]
        upcoming_tasks = [t for t in schedule if t.get("calendar_date") > today.isoformat()]
        next_task = upcoming_tasks[0] if upcoming_tasks else None

        return {
            "id": plan.id,
            "ai_generated": True,
            "crop": plan.crop,
            "crop_label": crop_config.get("label", plan.crop.capitalize()),
            "planting_date": date_to_iso(plan.planting_date),
            "harvest_date": date_to_iso(plan.harvest_date),
            "duration_days": plan.duration_days,
            "duration_months": round(plan.duration_days / 30, 1),
            "reminders": reminders,
            "stages": growth_stages,
            "ai_details": ai_plan,
            "crop_age_days": crop_age_days,
            "harvest_countdown": harvest_countdown,
            "current_stage": current_stage,
            "todays_tasks": todays_tasks,
            "next_task": next_task,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "is_active": plan.harvest_date >= today,
        }

    # Backward compatibility for legacy seeded plans
    current_stage = get_current_plan_stage(plan, today)
    live_reminder = get_live_plan_reminder(plan, today)
    todays_tasks = []
    if current_stage and current_stage.get("tasks"):
        todays_tasks = [{"task": t, "category": "General", "priority": "Medium"} for t in current_stage["tasks"]]

    return {
        "id": plan.id,
        "ai_generated": False,
        "crop": plan.crop,
        "crop_label": crop_config.get("label", plan.crop.capitalize()),
        "planting_date": date_to_iso(plan.planting_date),
        "harvest_date": date_to_iso(plan.harvest_date),
        "duration_days": plan.duration_days,
        "duration_months": round(plan.duration_days / 30, 1),
        "reminders": reminders,
        "stages": stages_data if isinstance(stages_data, list) else [],
        "crop_age_days": crop_age_days,
        "harvest_countdown": harvest_countdown,
        "current_stage": current_stage,
        "live_reminder": live_reminder,
        "todays_tasks": todays_tasks,
        "next_task": None,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "is_active": plan.harvest_date >= today,
    }


def get_current_plan_stage(plan: CropPlan, on_date: Optional[date] = None) -> Optional[dict]:
    target_date = on_date or date.today()
    if target_date < plan.planting_date or target_date > plan.harvest_date:
        return None

    stages = json.loads(plan.stages_json or "[]")
    for stage in stages:
        start_date = parse_date_value(stage["start_date"])
        end_date = parse_date_value(stage["end_date"])
        if start_date <= target_date <= end_date:
            return stage

    return stages[-1] if stages else None


def get_live_plan_reminder(plan: CropPlan, on_date: Optional[date] = None) -> dict:
    target_date = on_date or date.today()
    reminders = json.loads(plan.reminders_json or "{}")
    stage = get_current_plan_stage(plan, target_date)

    if not stage:
        return {
            "message": f"The {plan.crop.capitalize()} plan is not active for {target_date.isoformat()}.",
            "time": None,
        }

    reminder_order = [
        ("watering", "Water management", "6:00 AM", "Review irrigation need for"),
        ("fertilizing", "Nutrient follow-up", "7:30 AM", "Check fertilizer timing for"),
        ("pest_control", "Pest scouting", "5:30 PM", "Inspect pest and disease pressure in"),
        ("pruning", "Canopy maintenance", "8:00 AM", "Review pruning or crop shaping tasks for"),
    ]

    enabled_reminders = [item for item in reminder_order if reminders.get(item[0])]
    lead_key, lead_label, lead_time, lead_text = enabled_reminders[0] if enabled_reminders else (
        None,
        "Stage review",
        "7:00 AM",
        "Review current stage tasks for",
    )

    supporting_actions = ", ".join(label for _, label, _, _ in enabled_reminders[1:3])
    support_suffix = f" Also keep {supporting_actions.lower()} in view." if supporting_actions else ""

    return {
        "message": (
            f"{lead_text} the {plan.crop.capitalize()} crop. "
            f"Current stage: {stage['title']}. Focus today on {stage['tasks'][0]}{support_suffix}"
        ),
        "time": lead_time,
    }
