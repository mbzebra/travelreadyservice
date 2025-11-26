from collections import defaultdict
from typing import Dict, List, Tuple

from app.models.schemas import ChecklistItem, TripParameters


class TripAnalyzer:
    def __init__(self, parameters: TripParameters) -> None:
        self.params = parameters
        self.items: Dict[str, Tuple[str, float, List[str]]] = {}
        self.category_counts = defaultdict(int)

    def generate_checklist(self) -> List[ChecklistItem]:
        self._add_core_documents()
        self._add_travel_mode_rules()
        self._add_travel_type_rules()
        self._add_climate_rules()
        self._add_duration_rules()
        self._add_demographic_rules()
        self._add_cultural_rules()
        self._ensure_minimum_items()
        prioritized = self._prioritize_items()
        return prioritized

    def _add_item(self, name: str, category: str, base_score: float, rationale: List[str]) -> None:
        key = name.lower()
        bonus = 0.0
        if self.params.destination_climate == self.params.origin_climate:
            bonus -= 0.1
        if self.params.duration_days >= 10:
            bonus += 0.2
        if self.params.duration_days >= 21:
            bonus += 0.4
        cumulative_score = base_score + bonus
        if key in self.items:
            existing_category, score, notes = self.items[key]
            merged_score = max(score, cumulative_score)
            merged_notes = list({*notes, *rationale})
            self.items[key] = (existing_category, merged_score, merged_notes)
        else:
            self.items[key] = (category, cumulative_score, rationale)
            self.category_counts[category] += 1

    def _add_core_documents(self) -> None:
        essentials = [
            ("Passport or government ID", "Documents", 1.0, ["Required for identification and border control"]),
            ("Boarding passes or tickets", "Documents", 1.0, ["Needed for transit checkpoints"]),
            ("Travel insurance details", "Documents", 0.9, ["Supports emergencies"]),
            ("Payment cards and local currency", "Finance", 0.9, ["Covers purchases across modes"]),
            ("Mobile phone and charger", "Electronics", 0.95, ["Core communication device"]),
            ("Medications and prescriptions", "Health", 0.95, ["Maintain health regimen"]),
            ("Basic toiletries", "Personal Care", 0.85, ["Daily hygiene essentials"]),
            ("Reusable water bottle", "Health", 0.65, ["Hydration on the go"]),
            ("Weather-ready outerwear", "Clothing", 0.8, ["Quick adaptation to changing conditions"]),
        ]
        for name, category, score, rationale in essentials:
            self._add_item(name, category, score, rationale)

    def _add_travel_type_rules(self) -> None:
        travel_type = self.params.travel_type
        if travel_type == "business":
            business_items = [
                ("Tailored suits or professional outfits", "Clothing", 0.95, ["Align with formal meetings"]),
                ("Dress shirts per meeting", "Clothing", 0.9, ["Fresh attire for each session"]),
                ("Formal shoes and belt", "Clothing", 0.85, ["Completes professional look"]),
                ("Laptop with charger", "Electronics", 1.0, ["Work execution and presentations"]),
                ("Presentation clicker and adapters", "Electronics", 0.8, ["Smooth presentation delivery"]),
                ("Business cards and portfolio", "Documents", 0.9, ["Networking support"]),
                ("Printed contracts and meeting notes", "Documents", 0.85, ["Reference materials"]),
            ]
            for item in business_items:
                self._add_item(*item)
        elif travel_type == "leisure":
            leisure_items = [
                ("Comfortable casual outfits", "Clothing", 0.85, ["Relaxed exploration"]),
                ("Walking sneakers", "Clothing", 0.8, ["Long city days"]),
                ("Camera or smartphone gimbal", "Electronics", 0.75, ["Capture experiences"]),
                ("Books or games", "Entertainment", 0.6, ["Downtime enjoyment"]),
                ("Snacks for transit", "Food", 0.55, ["Maintain energy en route"]),
                ("Souvenir budget tracker", "Finance", 0.5, ["Manage discretionary spending"]),
            ]
            for item in leisure_items:
                self._add_item(*item)
        elif travel_type == "adventure":
            adventure_items = [
                ("Activity-specific gear", "Gear", 1.0, ["Core for adventure goals"]),
                ("Hiking boots with grip", "Clothing", 0.95, ["Rough terrain stability"]),
                ("Comprehensive first aid kit", "Health", 0.95, ["Respond to injuries"]),
                ("Weatherproof technical layers", "Clothing", 0.9, ["Protection from elements"]),
                ("GPS device and offline maps", "Navigation", 0.85, ["Route-finding"]),
                ("Emergency whistle and multi-tool", "Safety", 0.85, ["Rapid response"]),
                ("Headlamp or flashlight", "Safety", 0.8, ["Low-light visibility"]),
            ]
            for item in adventure_items:
                self._add_item(*item)
        elif travel_type == "family":
            family_items = [
                ("Diapers or pull-ups", "Childcare", 0.95, ["Young child essentials"]),
                ("Formula and baby bottles", "Childcare", 0.9, ["Infant feeding"]),
                ("Toys and comfort items", "Childcare", 0.75, ["Reduce travel stress"]),
                ("Snacks and baby food", "Food", 0.85, ["Keep children fed"]),
                ("Stroller or carrier", "Childcare", 0.8, ["Mobility support"]),
                ("Child-safe medications", "Health", 0.85, ["Address minor ailments"]),
                ("Car seat or booster", "Childcare", 0.8, ["Safety for transport"]),
            ]
            for item in family_items:
                self._add_item(*item)
        elif travel_type == "backpacking":
            backpacking_items = [
                ("Ultralight backpack", "Gear", 0.9, ["Comfort over distance"]),
                ("Hostel lock and sleep sheet", "Safety", 0.8, ["Shared lodging security"]),
                ("Compact toiletries", "Personal Care", 0.7, ["Space efficiency"]),
                ("Multi-use clothing layers", "Clothing", 0.8, ["Versatility"]),
                ("Budget tracking app", "Finance", 0.65, ["Control expenses"]),
                ("Microfiber towel", "Personal Care", 0.7, ["Quick dry travel"]),
                ("Water purification tablets", "Health", 0.75, ["Safe hydration"]),
            ]
            for item in backpacking_items:
                self._add_item(*item)

    def _add_climate_rules(self) -> None:
        climate = self.params.destination_climate
        climate_items = {
            "tropical": [
                ("Broad-spectrum sunscreen", "Health", 0.9, ["UV protection"]),
                ("Light breathable clothing", "Clothing", 0.8, ["Heat management"]),
                ("Insect repellent", "Health", 0.85, ["Mosquito-heavy regions"]),
                ("Packable rain jacket", "Clothing", 0.75, ["Sudden showers"]),
                ("Humidity-safe toiletries", "Personal Care", 0.65, ["Prevent discomfort"]),
            ],
            "cold": [
                ("Insulated jacket", "Clothing", 0.95, ["Thermal protection"]),
                ("Base layers and thermals", "Clothing", 0.9, ["Effective layering"]),
                ("Gloves and knit hat", "Clothing", 0.85, ["Protect extremities"]),
                ("Moisturizer and lip balm", "Personal Care", 0.7, ["Prevent dryness"]),
                ("Snow traction accessories", "Safety", 0.65, ["Icy surfaces"]),
            ],
            "desert": [
                ("Sun hood or wide-brim hat", "Clothing", 0.9, ["Direct sun protection"]),
                ("Breathable long sleeves", "Clothing", 0.8, ["Minimize heat gain"]),
                ("Hydration bladder", "Health", 0.85, ["Carry sufficient water"]),
                ("Electrolyte tablets", "Health", 0.7, ["Prevent dehydration"]),
                ("Cooling towel", "Personal Care", 0.65, ["Temperature relief"]),
            ],
            "temperate": [
                ("Layerable mid-weight jacket", "Clothing", 0.8, ["Adaptable conditions"]),
                ("Compact umbrella", "Clothing", 0.65, ["Unpredictable showers"]),
                ("Versatile footwear", "Clothing", 0.7, ["City and trail ready"]),
                ("Neutral accessories", "Clothing", 0.55, ["Blend with varied outfits"]),
            ],
        }
        for item in climate_items.get(climate, []):
            self._add_item(*item)

    def _add_travel_mode_rules(self) -> None:
        mode = self.params.travel_mode
        rules = {
            "air": [
                ("TSA-compliant liquids bag", "Documents", 0.8, ["Airport security ready"]),
                ("Passport and ID holder", "Documents", 0.85, ["Speed through checkpoints"]),
                ("Neck pillow and eye mask", "Comfort", 0.65, ["Rest on flight"]),
                ("Charging cables for airport", "Electronics", 0.7, ["Leverage terminal outlets"]),
                ("Offline boarding passes", "Documents", 0.75, ["Access without connectivity"]),
            ],
            "car": [
                ("Road trip snacks", "Food", 0.55, ["Sustain energy while driving"]),
                ("Car charger and mounts", "Electronics", 0.6, ["Navigation power"]),
                ("Emergency car kit", "Safety", 0.8, ["Breakdown readiness"]),
                ("Spare tire check and tools", "Safety", 0.7, ["Road safety"]),
                ("Cooler for perishables", "Food", 0.55, ["Keep items fresh"]),
            ],
            "train": [
                ("Comfortable walking shoes", "Clothing", 0.65, ["Station transfers"]),
                ("Motion sickness medication", "Health", 0.6, ["Comfort on curves"]),
                ("Cabin-friendly layers", "Clothing", 0.55, ["Varying car temperatures"]),
                ("Power strip for shared outlets", "Electronics", 0.6, ["Limited sockets"]),
            ],
            "cruise": [
                ("Motion sickness bands or meds", "Health", 0.7, ["Open water stability"]),
                ("Cruise casual and formal wear", "Clothing", 0.65, ["Theme nights"]),
                ("Cabin power strip", "Electronics", 0.6, ["Few outlets"]),
                ("Deck-friendly footwear", "Clothing", 0.6, ["Non-slip surfaces"]),
            ],
        }
        for item in rules.get(mode, []):
            self._add_item(*item)

    def _add_duration_rules(self) -> None:
        duration = self.params.duration_days
        duration_rules = [
            (duration >= 7, "Laundry kit or detergent", "Personal Care", 0.55, ["Wash clothing during longer stays"]),
            (duration >= 14, "Extra rotation of outfits", "Clothing", 0.65, ["Reduce wear frequency"]),
            (duration >= 21, "Supplemental medication supply", "Health", 0.7, ["Maintain regimen for long trips"]),
        ]
        for condition, name, category, score, rationale in duration_rules:
            if condition:
                self._add_item(name, category, score, rationale)

    def _add_demographic_rules(self) -> None:
        for traveler in self.params.traveler_demographics:
            if traveler.age_group == "senior":
                self._add_item(
                    "Mobility aids or comfort cushions",
                    "Accessibility",
                    0.7,
                    ["Support for senior travelers"],
                )
                self._add_item(
                    "Prescription list copies",
                    "Health",
                    0.75,
                    ["Share with medical staff if needed"],
                )
            if traveler.has_special_needs:
                self._add_item(
                    "Accessibility documentation",
                    "Accessibility",
                    0.8,
                    ["Coordinate accommodations and assistance"],
                )
                self._add_item(
                    "Specialized equipment backups",
                    "Accessibility",
                    0.78,
                    ["Redundancy for critical aids"],
                )
            if traveler.age_group == "child":
                self._add_item(
                    "Comfort blanket or plush",
                    "Childcare",
                    0.7,
                    ["Reduce anxiety during transit"],
                )
                self._add_item(
                    "Child headphones",
                    "Entertainment",
                    0.6,
                    ["Protect hearing while providing media"],
                )

    def _add_cultural_rules(self) -> None:
        destination = self.params.destination_climate
        modest_regions = {"desert", "tropical"}
        if destination in modest_regions:
            self._add_item(
                "Modest attire options",
                "Cultural",
                0.6,
                ["Respectful clothing for cultural norms"],
            )
        self._add_item(
            "Local etiquette notes",
            "Cultural",
            0.55,
            ["Prepared for greetings and tipping norms"],
        )
        self._add_item(
            "Key phrases in local language",
            "Cultural",
            0.6,
            ["Smooth daily interactions"],
        )

    def _ensure_minimum_items(self) -> None:
        general_padding = [
            ("Travel-sized laundry bag", "Personal Care", 0.45, ["Organize worn clothing"]),
            ("Extra device batteries", "Electronics", 0.45, ["Backup power"]),
            ("Offline maps and guides", "Navigation", 0.5, ["Connectivity gaps"]),
            ("Copies of important documents", "Documents", 0.5, ["Redundancy for safety"]),
            ("Reusable shopping tote", "Convenience", 0.4, ["Carry purchases"]),
            ("Compression packing cubes", "Convenience", 0.42, ["Organize luggage"]),
            ("Hand sanitizer and wipes", "Health", 0.48, ["Hygiene in transit"]),
            ("Portable power bank", "Electronics", 0.62, ["Extended device uptime"]),
            ("Notebook and pen", "Documents", 0.4, ["Capture notes and addresses"]),
            ("Small sewing kit", "Convenience", 0.35, ["Wardrobe repairs"]),
            ("Earplugs", "Comfort", 0.38, ["Sleep in noisy settings"]),
            ("Eye mask", "Comfort", 0.37, ["Improve rest in transit"]),
            ("Travel pillow", "Comfort", 0.4, ["Neck support"],),
            ("Healthy grab-and-go snacks", "Food", 0.42, ["Keep energy stable"]),
            ("Refillable toiletry containers", "Personal Care", 0.4, ["Custom product sizes"]),
            ("Shoe bags", "Convenience", 0.33, ["Protect clothing"]),
            ("Travel clothesline", "Convenience", 0.36, ["Dry clothing quickly"]),
            ("Waterproof pouches", "Safety", 0.37, ["Protect electronics"],),
            ("Backup credit card", "Finance", 0.38, ["Redundancy for payments"]),
            ("International adapter", "Electronics", 0.55, ["Charge devices abroad"]),
            ("SIM card or eSIM plan", "Electronics", 0.5, ["Data connectivity"]),
            ("Weather alert subscriptions", "Safety", 0.35, ["Timely updates"]),
            ("Emergency contact card", "Safety", 0.4, ["Share critical info"]),
            ("Reusable utensils", "Food", 0.3, ["Eco-friendly dining"]),
            ("Collapsible daypack", "Convenience", 0.45, ["Daily outings"],),
            ("Small first aid add-ons", "Health", 0.44, ["Bandages and pain relief"]),
            ("Portable hotspot", "Electronics", 0.47, ["Reliable connectivity"]),
            ("Secure money belt", "Safety", 0.5, ["Lower theft risk"]),
            ("Travel-sized lint roller", "Clothing", 0.3, ["Maintain outfits"]),
            ("Refillable hand soap sheets", "Health", 0.31, ["Hygiene flexibility"]),
            ("Foldable rain poncho", "Clothing", 0.34, ["Unexpected showers"]),
            ("Laundry stain remover pen", "Personal Care", 0.32, ["Quick fixes"]),
            ("Multi-port charger", "Electronics", 0.46, ["Charge multiple devices"]),
            ("Noise-cancelling headphones", "Entertainment", 0.52, ["Better focus and rest"]),
            ("Travel-sized board games", "Entertainment", 0.28, ["Group fun"]),
            ("Wellness supplements", "Health", 0.29, ["Immune support"]),
            ("Seat-back organizer", "Comfort", 0.27, ["Keep essentials accessible"]),
            ("Travel-safe cutlery", "Food", 0.26, ["Picnics and takeout"]),
            ("Reusable straw", "Food", 0.25, ["Reduce waste"]),
            ("Packing checklist printout", "Documents", 0.24, ["Track packed items"]),
            ("Shoe deodorizer packets", "Personal Care", 0.23, ["Odor control"]),
            ("Softshell jacket", "Clothing", 0.35, ["Versatile layer"]),
            ("Foldable hat", "Clothing", 0.28, ["Sun or light rain coverage"]),
            ("Bluetooth tracker tags", "Safety", 0.41, ["Locate belongings"]),
            ("Handheld luggage scale", "Convenience", 0.33, ["Avoid overweight fees"]),
            ("Travel-sized yoga mat", "Health", 0.27, ["Maintain routines"]),
            ("Journal for reflection", "Entertainment", 0.22, ["Document experiences"]),
            ("Travel detergent sheets", "Personal Care", 0.26, ["Compact laundry option"]),
            ("Quick-dry base layers", "Clothing", 0.31, ["Comfort in varying climates"]),
            ("Clip-on reading light", "Entertainment", 0.21, ["Read without disturbing others"]),
            ("Emergency cash stash", "Finance", 0.34, ["Backup funds"]),
        ]
        while len(self.items) < 50 and general_padding:
            name, category, score, rationale = general_padding.pop(0)
            self._add_item(name, category, score, rationale)
        trimmed_padding = general_padding[: max(0, 100 - len(self.items))]
        for name, category, score, rationale in trimmed_padding:
            if len(self.items) >= 100:
                break
            self._add_item(name, category, score, rationale)

    def _prioritize_items(self) -> List[ChecklistItem]:
        ranked = sorted(self.items.items(), key=lambda entry: entry[1][1], reverse=True)
        prioritized: List[ChecklistItem] = []
        for name, (category, score, rationale) in ranked:
            priority = self._priority_label(score)
            prioritized.append(
                ChecklistItem(
                    name=name.title(),
                    category=category,
                    score=round(score, 2),
                    rationale=rationale,
                    priority=priority,
                )
            )
        return prioritized

    @staticmethod
    def _priority_label(score: float) -> str:
        if score >= 0.9:
            return "critical"
        if score >= 0.75:
            return "high"
        if score >= 0.5:
            return "medium"
        return "nice-to-have"
