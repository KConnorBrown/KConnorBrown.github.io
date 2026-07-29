# Photo Journal left-rail filter tags and palette.
JOURNAL_FILTER_TAGS = [
    {
        "name": "Florals",
        "slug": "florals",
        "color": "#566E3D",
        "selected": "#3d4f2b",
    },
    {
        "name": "Architecture",
        "slug": "architecture",
        "color": "#92AFD7",
        "selected": "#6a8bb8",
    },
    {
        "name": "Humor",
        "slug": "humor",
        "color": "#43C59E",
        "selected": "#2f9a7a",
    },
    {
        "name": "Cat",
        "slug": "cat",
        "color": "#FF7F11",
        "selected": "#cc660e",
    },
    {
        "name": "San Francisco",
        "slug": "san-francisco",
        "color": "#3D314A",
        "selected": "#2a2235",
    },
]


def filter_tag_by_slug(slug):
    return next((tag for tag in JOURNAL_FILTER_TAGS if tag["slug"] == slug), None)
