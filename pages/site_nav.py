SITE_SECTIONS = [
    {
        "key": "about",
        "label": "About Me",
        "label_lines": ["About", "Me"],
        "url": "/about/",
        "intro": "A bit about Connor.",
    },
    {
        "key": "development",
        "label": "Software Development",
        "label_lines": ["Software", "Development"],
        "url": "/development/",
        "intro": "Software projects and experiments.",
    },
    {
        "key": "photography",
        "label": "Photography",
        "label_lines": ["Photography"],
        "url": "/photography/",
        "intro": "Photos tagged photography.",
    },
    {
        "key": "interior-design",
        "label": "Interior Design",
        "label_lines": ["Interior", "Design"],
        "url": "/interior-design/",
        "intro": "Spaces, objects, and interior studies.",
    },
    {
        "key": "gardening-design",
        "label": "Gardening Design",
        "label_lines": ["Gardening", "Design"],
        "url": "/gardening-design/",
        "intro": "Planted spaces, containers, and growing experiments.",
    },
    {
        "key": "my-art",
        "label": "My Art",
        "label_lines": ["My Art"],
        "url": "/my-art/",
        "intro": "Art I've made.",
    },
    {
        "key": "photo-journal",
        "label": "Photo Journal",
        "label_lines": ["Photo", "Journal"],
        "url": "/photo-journal/",
        "intro": "The full archive — filter by tag to narrow the stream.",
    },
]


def site_nav_context(active_key=None, title=None, intro=None):
    """Shared chrome for the cartographic site map."""
    active = next((section for section in SITE_SECTIONS if section["key"] == active_key), None)
    return {
        "site_sections": SITE_SECTIONS,
        "nav_sections": SITE_SECTIONS,
        "active_section_key": active_key,
        "active_section": active,
        "title": title or (active["label"] if active else "Connor Brown"),
        "intro": intro or (active["intro"] if active else "Code, images, words, and spaces."),
        "show_page_indicator": bool(active_key),
    }
