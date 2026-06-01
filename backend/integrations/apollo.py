import httpx
import os
from models.campaign import Campaign


APOLLO_BASE = "https://api.apollo.io/v1"


async def find_prospects(icp: dict, limit: int = 25) -> list[dict]:
    """Search Apollo for prospects matching the ICP."""

    api_key = os.getenv("APOLLO_API_KEY")
    headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}

    payload = {
        "api_key": api_key,
        "per_page": limit,
        "person_titles": icp.get("job_titles", []),
        "organization_industry_tag_ids": [],  # map industries separately if needed
        "person_seniorities": icp.get("seniority_levels", []),
        "person_locations": icp.get("locations", []),
        "q_keywords": " ".join(icp.get("keywords", [])),
    }

    if icp.get("company_size_min") or icp.get("company_size_max"):
        payload["organization_num_employees_ranges"] = [
            f"{icp.get('company_size_min', 1)},{icp.get('company_size_max', 10000)}"
        ]

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{APOLLO_BASE}/mixed_people/search", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    prospects = []
    for person in data.get("people", []):
        email = (person.get("email") or "").strip()
        if not email or "apollo" in email:
            continue
        prospects.append({
            "first_name": person.get("first_name", ""),
            "last_name": person.get("last_name", ""),
            "email": email,
            "company": person.get("organization", {}).get("name"),
            "title": person.get("title"),
            "linkedin_url": person.get("linkedin_url"),
            "apollo_id": person.get("id"),
        })

    return prospects
