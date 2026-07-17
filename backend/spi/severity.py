"""McKee (1993) SPI severity classes with bilingual labels + map colors.

नोट (Nepali): यो फाइलले SPI मानलाई खडेरीको गम्भीरता वर्गमा वर्गीकरण गर्छ।
सीमाहरू McKee et al. (1993) अनुसार छन् — नेपाली लेबलहरू DHM को
खडेरी अनुगमन उपकरणसँग मिल्दोजुल्दो राखिएको छ।
"""
from __future__ import annotations

# क्रमबद्ध वर्गहरू: सबैभन्दा सुक्खादेखि सबैभन्दा भिजेकोसम्म
SEVERITY_META: dict[str, dict] = {
    "extreme_dry": {
        "label_en": "Extremely Dry",
        "label_ne": "अत्यधिक सुक्खा",
        "color": "#7f1d1d",  # dark red
        "order": 0,
    },
    "severe_dry": {
        "label_en": "Severely Dry",
        "label_ne": "गम्भीर सुक्खा",
        "color": "#dc2626",  # red
        "order": 1,
    },
    "moderate_dry": {
        "label_en": "Moderately Dry",
        "label_ne": "मध्यम सुक्खा",
        "color": "#f59e0b",  # amber
        "order": 2,
    },
    "near_normal": {
        "label_en": "Near Normal",
        "label_ne": "सामान्य नजिक",
        "color": "#22c55e",  # green
        "order": 3,
    },
    "moderate_wet": {
        "label_en": "Moderately Wet",
        "label_ne": "मध्यम भिजेको",
        "color": "#38bdf8",  # light blue
        "order": 4,
    },
    "severe_wet": {
        "label_en": "Severely Wet",
        "label_ne": "गम्भीर भिजेको",
        "color": "#2563eb",  # blue
        "order": 5,
    },
    "extreme_wet": {
        "label_en": "Extremely Wet",
        "label_ne": "अत्यधिक भिजेको",
        "color": "#1e3a8a",  # dark blue
        "order": 6,
    },
    "no_data": {
        "label_en": "No Data",
        "label_ne": "तथ्याङ्क छैन",
        "color": "#9ca3af",  # gray
        "order": 7,
    },
}


def classify(spi: float | None) -> str:
    """SPI मानबाट वर्ग निर्धारण गर्ने (McKee 1993 का सीमाहरू)।

    सीमा नियम: -2.0 भन्दा कम वा बराबर = अत्यधिक सुक्खा, आदि।
    """
    if spi is None:
        return "no_data"
    if spi <= -2.0:
        return "extreme_dry"
    if spi <= -1.5:
        return "severe_dry"
    if spi <= -1.0:
        return "moderate_dry"
    if spi < 1.0:
        return "near_normal"
    if spi < 1.5:
        return "moderate_wet"
    if spi < 2.0:
        return "severe_wet"
    return "extreme_wet"
