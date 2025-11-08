"""
Kannada-focused demo seed data.

Run after the base seed scripts:
    python seed_data.py
    python seed_demo_kannada.py

This script only inserts new rows (does not update existing data) and favors
Kannada-first content with English context where helpful.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List

from app.core.database import SessionLocal
from app.models.budget import BudgetTransaction, DepartmentBudget, WardBudget
from app.models.citizen_engagement import (
    CitizenFeedback,
    FeedbackPriority,
    FeedbackStatus,
    FeedbackType,
    VideoConference,
    VideoConferenceStatus,
    VideoConferenceType,
)
from app.models.complaint import Complaint, ComplaintPriority, ComplaintStatus
from app.models.constituency import Constituency
from app.models.department import Department
from app.models.faq import FAQSolution
from app.models.news import (
    MLASchedule,
    News,
    NewsCategory,
    NewsPriority,
    ScheduleStatus,
    ScheduleType,
    TickerItem,
)
from app.models.poll import Poll, PollOption, Vote
from app.models.social_feed import PostStatus, PostType, SocialPost
from app.models.user import User, UserRole
from app.models.ward import Ward
from app.models.forum import ForumTopic, ForumPost, ForumCategory, TopicStatus


KANNADA_CITIZENS: Dict[str, List[Dict[str, str]]] = {
    "Puttur": [
        {"name_kn": "ಶೈಲಜಾ ದೇವಿ", "name_en": "Shailaja Devi", "phone": "+919861010201"},
        {"name_kn": "ನಾಗರಾಜ್ ಕಲ್ಲೂರಾಯ", "name_en": "Nagaraj Kalluraya", "phone": "+919861010202"},
        {"name_kn": "ಅರವಿಂದ ಶೆಟ್ಟಿ", "name_en": "Aravinda Shetty", "phone": "+919861010203"},
    ],
    "Mangalore North": [
        {"name_kn": "ವಿಶಾಲಾ ಪಾಂಡೆ", "name_en": "Vishala Pandey", "phone": "+919861010301"},
        {"name_kn": "ಚೈತನ್ಯ ರೈ", "name_en": "Chaitanya Rai", "phone": "+919861010302"},
        {"name_kn": "ಹರ್ಷಿತಾ ಕೋಟ್ಯಾನ್", "name_en": "Harshitha Kotian", "phone": "+919861010303"},
    ],
    "Udupi": [
        {"name_kn": "ಸುಮಂಗಲಾ ಆನಂದ", "name_en": "Sumangala Anand", "phone": "+919861010401"},
        {"name_kn": "ಮಧುಸೂಧನ ಬೆಳ್ಳೂರ", "name_en": "Madhusudhana Bellur", "phone": "+919861010402"},
        {"name_kn": "ಪೂರ್ಣಿಮಾ ಹೆಗ್ಡೆ", "name_en": "Poornima Hegde", "phone": "+919861010403"},
    ],
}


KANNADA_COMPLAINTS: Dict[str, List[Dict[str, object]]] = {
    "Puttur": [
        {
            "title": "ಪುತ್ತೂರು ಮಾರುಕಟ್ಟೆ ರಸ್ತೆಯ ಗುಂಡಿಗಳು - Market road potholes",
            "description_kn": "ಮಾರುಕಟ್ಟೆ ಪ್ರದೇಶದ ಮುಖ್ಯ ರಸ್ತೆಯಲ್ಲಿ ದೀಪಾವಳಿ ಮಳೆ ನಂತರ ಗಂಭೀರ ಗುಂಡಿಗಳು ಉಂಟಾಗಿವೆ.",
            "description_en": "Severe potholes after monsoon showers are disrupting market access.",
            "category": "roads",
            "priority": ComplaintPriority.URGENT,
            "ward_number": 1,
            "lat": Decimal("12.7685"),
            "lng": Decimal("75.2012"),
        },
        {
            "title": "ನೆಹರೂ ನಗರದಲ್ಲಿ ಕುಡಿಯುವ ನೀರಿನ ದುರ್ಗಂಧ - Odour in drinking water",
            "description_kn": "ವಾರ್ಡ್ 3 ನಲ್ಲಿ ಮನೆಗಳಿಗೆ ಬರುವ ನೀರಿಗೆ ದುರ್ಗಂಧ ಹಾಗೂ ಬಣ್ಣ ಬದಲಾವಣೆ ಕಂಡುಬರುತ್ತಿದೆ.",
            "description_en": "Residents report foul smell and discoloration in piped water.",
            "category": "water",
            "priority": ComplaintPriority.HIGH,
            "ward_number": 3,
            "lat": Decimal("12.7643"),
            "lng": Decimal("75.2054"),
        },
    ],
    "Mangalore North": [
        {
            "title": "ಹಂಪನಕಟ್ಟೆ ಕಸದ ಸಂಗ್ರಹ - Hampankatta waste overflow",
            "description_kn": "ವಾಣಿಜ್ಯ ವಲಯದಲ್ಲಿ ಕಸದ ದೊಡ್ಡ ದಿಬ್ಬಗಳಿಗಾಗಿ ದುರ್ವಾಸನೆ ಮತ್ತು ಗಾಳಿ ಕೀಟಗಳ ಸಮಸ್ಯೆ.",
            "description_en": "Uncollected garbage mounds attracting pests near commercial stretch.",
            "category": "sanitation",
            "priority": ComplaintPriority.HIGH,
            "ward_number": 3,
            "lat": Decimal("12.8739"),
            "lng": Decimal("74.8426"),
        },
        {
            "title": "ಕದ್ರಿ ಉದ್ಯಾನ ಪ್ರದೇಶದಲ್ಲಿ ದೀಪಗಳು ನ ಹೊರಳು - Park lights not working",
            "description_kn": "ಸಂಜೆ ವೇಳೆಯಲ್ಲಿಯೂ ಕದ್ರಿ ಉದ್ಯಾನದಲ್ಲಿ ಬೆಳಕು ಇಲ್ಲದೆ ಕುಟುಂಬಗಳಿಗೆ ಭದ್ರತೆಯ ಸಮಸ್ಯೆ.",
            "description_en": "Lack of lighting in Kadri park poses safety risk after dusk.",
            "category": "streetlight",
            "priority": ComplaintPriority.MEDIUM,
            "ward_number": 1,
            "lat": Decimal("12.8901"),
            "lng": Decimal("74.8563"),
        },
    ],
    "Udupi": [
        {
            "title": "ಕಾರ್ ಸ್ಟ್ರೀಟ್ ಬಳಿ ಮಳೆ ನೀರಿನ ಹರಿವು - Rainwater choking near Car Street",
            "description_kn": "ಕಾರ್ ಸ್ಟ್ರೀಟ್ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಮಳೆಗೆ ಒಳಚರಂಡಿ ಬಂದ್ ಆಗಿದ್ದು, ಶ್ರೀಕೃಷ್ಣ ದೇವಸ್ಥಾನದ ಪ್ರವೇಶದ ಬಳಿ ನೀರು ತುಂಬುತ್ತಿದೆ.",
            "description_en": "Blocked drains causing waterlogging near the temple approach.",
            "category": "drainage",
            "priority": ComplaintPriority.URGENT,
            "ward_number": 1,
            "lat": Decimal("13.3401"),
            "lng": Decimal("74.7463"),
        },
        {
            "title": "ಮಾಲ್ಪೆ ಬೀಚ್ ಸ್ವಚ್ಛತಾ ವಿನಂತಿ - Malpe beach cleanliness",
            "description_kn": "ವಾರಿ ಪರಿಸ್ಥಿತಿ ನಂತರ ಕಡಲತೀರದಲ್ಲಿ ಪ್ಲಾಸ್ಟಿಕ್ ಕಸ ಮತ್ತು ಮೀನು ಬಿಡಿಸಿದ ಕುಡುಕುಗಳು ಅವ್ಯವಸ್ಥೆ ಸೃಷ್ಟಿಸುತ್ತಿವೆ.",
            "description_en": "Post-storm debris and plastic litter need urgent attention at Malpe beach.",
            "category": "sanitation",
            "priority": ComplaintPriority.HIGH,
            "ward_number": 5,
            "lat": Decimal("13.3529"),
            "lng": Decimal("74.7034"),
        },
    ],
}


KANNADA_NEWS: Dict[str, List[Dict[str, object]]] = {
    "Puttur": [
        {
            "title": "ಪುತ್ತೂರು ನಗರಪಾಲಿಕೆಯ 'ಸ್ವಚ್ಛ ವಾರ' ಘೋಷಣೆ",
            "summary": "ವಾರ್ಡ್ ಮಟ್ಟದಲ್ಲಿ ಕಸದ ವರ್ಗೀಕರಣ ತಳ ಮಟ್ಟದವರಿಗೆ ತರಬೇತಿ ಆರಂಭ.",
            "content": (
                "ಪುತ್ತೂರು ನಗರಪಾಲಿಕೆ ವಾರ್ಡ್ ಮಟ್ಟದಲ್ಲಿ 'ಸ್ವಚ್ಛ ವಾರ' ಅಭಿಯಾನ ಪ್ರಾರಂಭಿಸಿದೆ. "
                "ಕನ್ನಡದಲ್ಲಿಯೇ ಮಾಹಿತಿ ಪತ್ರಿಕೆಗಳು ಹಂಚಿಕೆ ಆಗಲಿದ್ದು, ಪ್ರತಿ ಮನೆಗೆ ಒಬ್ಬ ಸ್ವಯಂಸೇವಕರನ್ನು ನೇಮಿಸಲಾಗುತ್ತಿದೆ."
            ),
            "category": NewsCategory.PUBLIC_SERVICE,
            "priority": NewsPriority.HIGH,
            "tags": "ಸ್ವಚ್ಛತೆ,ಸಮುದಾಯ",
        },
        {
            "title": "ಪುತ್ತೂರು ಬಸ್ ನಿಲ್ದಾಣ ಆವರಣದಲ್ಲಿ ಪುಷ್ಪ ಮಾರುಕಟ್ಟೆ",
            "summary": "ಸ್ಥಳೀಯ ಮಹಿಳಾ ಸ್ವಸಹಾಯ ಸಂಘಗಳಿಗೆ ಆದಾಯದ ನೂತನ ಮಾರ್ಗ.",
            "content": (
                "ಬಸ್ ನಿಲ್ದಾಣ ಆವರಣದಲ್ಲಿ ವಾರಪರಿತೆಯಾಗಿ ಕನ್ನಡಭಾಷೆಯಲ್ಲಿ ಕಾರ್ಯಾಗಾರಗಳೊಂದಿಗೆ ಪಾಕೃತಿಕ ಪುಷ್ಪ ಮೇಳವನ್ನು "
                "MLA ಕಚೇರಿ ಆರಂಭಿಸಿದೆ."
            ),
            "category": NewsCategory.LOCAL_DEVELOPMENT,
            "priority": NewsPriority.MEDIUM,
            "tags": "ಉದ್ಯಮ,ಮಹಿಳಾ ಶಕ್ತಿ",
        },
    ],
    "Mangalore North": [
        {
            "title": "ಮಂಗಳೂರು ಉತ್ತರದಲ್ಲಿ 'ಸ್ಮಾರ್ಟ್ ಡಿಜಿಟಲ್ ಗ್ರಂಥಾಲಯ' ಶುಭಾರಂಭ",
            "summary": "ಕನ್ನಡ ಆಡಿಯೊ ಪುಸ್ತಕಗಳಿಗೂ ವಿಶೇಷ ವರ್ಗ.",
            "content": (
                "ಹೊಸ ಡಿಜಿಟಲ್ ಗ್ರಂಥಾಲಯದಲ್ಲಿ 800 ಕ್ಕೂ ಹೆಚ್ಚು ಕನ್ನಡ ಆಡಿಯೊ ಮತ್ತು ಇ-ಪುಸ್ತಕಗಳು ಲಭ್ಯ. "
                "ಪೌರರು ಪಾಸ್ ಮೂಲಕ ಪ್ರವೇಶ ಪಡೆಯಬಹುದು."
            ),
            "category": NewsCategory.ANNOUNCEMENT,
            "priority": NewsPriority.MEDIUM,
            "tags": "ಗ್ರಂಥಾಲಯ,ಕನ್ನಡ",
        },
        {
            "title": "ಎಮ್-ನೆಟ್ ಮೊಬೈಲ್ ಆಪ್ ಮೂಲಕ ಕುಡಿಯುವ ನೀರಿನ ಸಂಪ್ರೇಷಣೆ",
            "summary": "ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ನೋಟಿಫಿಕೇಶನ್ ಹಾಗೂ ಸ್ಥಿತಿ ವರದಿ.",
            "content": (
                "ಮೈಸೂರು ರಸ್ತೆ ವಾರ್ಡ್‌ಗಳಲ್ಲಿ ನೀರಿನ ಪೂರೈಕೆ ವೇಳಾಪಟ್ಟಿಯನ್ನು 'ಎಮ್-ನೆಟ್' ಆಪ್ ಮೂಲಕ ಕನ್ನಡದಲ್ಲಿ ಅಧಿಸೂಚನೆ "
                "ಮಾಡಲಾಗುತ್ತದೆ."
            ),
            "category": NewsCategory.GOVERNMENT_INITIATIVE,
            "priority": NewsPriority.MEDIUM,
            "tags": "ನೀರಿನ ಪೂರೈಕೆ,ಡಿಜಿಟಲ್",
        },
    ],
    "Udupi": [
        {
            "title": "ಉಡುಪಿ ಶ್ರೀಕೃಷ್ಣ ಕ್ಷೇತ್ರದಲ್ಲಿ ಪರಿಸರ ಸ್ನೇಹಿ ಬೆಳಕು",
            "summary": "ಸೌರ ದೀಪಗಳು ಹಾಗೂ ಕನ್ನಡ ಘೋಷವಾಕ್ಯಗಳು.",
            "content": (
                "ಶ್ರೀಕೃಷ್ಣ ಕ್ಷೇತ್ರದಲ್ಲಿ ಹೊಸದಾಗಿ ಅಳವಡಿಸಿದ ಸೌರ ದೀಪಗಳಲ್ಲಿ ಕನ್ನಡದಲ್ಲಿ 'ಪರಿಸರ ಕಾಯೋಣ' ಮುಂತಾದ ಘೋಷಣೆಗಳು "
                "ಪ್ರಜ್ಞೆ ಮೂಡಿಸುತ್ತವೆ."
            ),
            "category": NewsCategory.ACHIEVEMENT,
            "priority": NewsPriority.HIGH,
            "tags": "ಸೌರಶಕ್ತಿ,ಪರಿಸರ",
        },
        {
            "title": "ಮಾಲ್ಪೆ ಮೀನುಗಾರರಿಗೆ ಕನ್ನಡ ತರಬೇತಿ ಕೇಂದ್ರ",
            "summary": "ಹವಾಮಾನ ಮಾಹಿತಿ ಓದಲು ಕನ್ನಡ-ಐಕಾನ್ ಪಾಠಗಳು.",
            "content": (
                "ಮಾಲ್ಪೆ ಬಂದರು ಪ್ರದೇಶದಲ್ಲಿ ಮೀನುಗಾರರಿಗೆ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆಗಳನ್ನು ಕನ್ನಡದಲ್ಲಿ ಓದಲು ವಿಶೇಷ ತರಬೇತಿ "
                "ಕೇಂದ್ರ ಆರಂಭಿಸಲಾಗಿದೆ."
            ),
            "category": NewsCategory.PUBLIC_SERVICE,
            "priority": NewsPriority.MEDIUM,
            "tags": "ಮೀನುಗಾರಿಕೆ,ತರಬೇತಿ",
        },
    ],
}


KANNADA_TICKERS: Dict[str, List[str]] = {
    "Puttur": [
        "ವಾರ್ಡ್ 2 ರಲ್ಲಿ 15 ನವೆಂಬರ್ ಬೆಳಿಗ್ಗೆ 10 ರಿಂದ ನೀರು ಪೂರೈಕೆ ನಿಲ್ಲಿಕೆ (Maintenance shutdown).",
        "ಅಂಗನವಾಡಿ ಮಕ್ಕಳಿಗಾಗಿ ಉಚಿತ ಆರೋಗ್ಯ ತಪಾಸಣೆ ಶಿಬಿರ 18 ನವೆಂಬರ್, ನಗರಸಭೆ ಕಚೇರಿ.",
    ],
    "Mangalore North": [
        "ಕದ್ರಿ ಉದ್ಯಾನದ ಬೆಳಕುಗಳ ದುರಸ್ತಿ 12-14 ನವೆಂಬರ್ ನಡುವೆ ನಡೆಯಲಿದೆ.",
        "ಡ್ರೈವರ್ ಗಳಿಗೆ ಕನ್ನಡ ರೋಲ್ ನಂಬರ್ ತರಬೇತಿ ಶಿಬಿರ 16 ನವೆಂಬರ್, ಪಾಂಡೇಶ್ವರ."
    ],
    "Udupi": [
        "ಮಾಲ್ಪೆ ಬೀಚ್‌ನಲ್ಲಿ ಸ್ವಚ್ಛತಾ ಅಭಿಯಾನಕ್ಕೆ 120 ಸ್ವಯಂಸೇವಕರು ಅಗತ್ಯ, 19 ನವೆಂಬರ್.",
        "ಅಟಲ್ ಯೋಚನೆ ವೇದಿಕೆ: ಗ್ರಾಮೀಣ ಯುವಕರಿಗಾಗಿ ಕನ್ನಡ ಮಾರ್ಗದರ್ಶನ, 20 ನವೆಂಬರ್.",
    ],
}


KANNADA_POLLS: Dict[str, List[Dict[str, object]]] = {
    "Puttur": [
        {
            "title": "ಪುತ್ತೂರಿನಲ್ಲಿ ಕಸದ ಸಂಗ್ರಹಕ್ಕೆ ಸೂಕ್ತ ಸಮಯ ಯಾವದು? (Best trash collection window)",
            "description": "ಸ್ಥಿರ ವೇಳಾಪಟ್ಟಿಗೆ ನಿಮ್ಮ ಅಭಿಪ್ರಾಯ ನೀಡಿ.",
            "options": [
                "ಬೆಳಿಗ್ಗೆ 7 ಗಂಟೆಗೆ (7 AM)",
                "ಮಧ್ಯಾಹ್ನ 1 ಗಂಟೆಗೆ (1 PM)",
                "ಸಂಜೆ 6 ಗಂಟೆಗೆ (6 PM)",
                "ವಾರಕ್ಕೆ ಎರಡು ಬಾರಿ ಮಾತ್ರ",
            ],
        }
    ],
    "Mangalore North": [
        {
            "title": "ಮಹಿಳಾ ಸುರಕ್ಷತೆಗಾಗಿ ಯಾವ ಕ್ರಮ ತ್ವರಿತ ಅಗತ್ಯ? (Priority safety action)",
            "description": "ರಾತ್ರಿ ತಪಾಸಣೆ ಹಾಗೂ ಬೆಳಕು ವಿತರಣೆ ವಿಷಯದಲ್ಲಿ ನಿಮ್ಮ ಸಲಹೆ ತಿಳಿಸಿ.",
            "options": [
                "ಹೆಚ್ಚುವರಿ ಪೊಲೀಸ್ ಪ ಪರೀಕ್ಷಾ ಗಸ್ತು",
                "ಪಾದಚಾರಿಗಳಿಗಾಗಿ ಸೆಕ್ಯೂರಿಟಿ ಅಲಾರ್ಮ್",
                "ಸ್ಮಾರ್ಟ್ ಲೈಟಿಂಗ್ ಸೆನ್ಸರ್",
                "ಮಹಿಳಾ ಸಹಾಯ ಕ್ಯಾಂಪ್",
            ],
        }
    ],
    "Udupi": [
        {
            "title": "ಯುವಕರಿಗೆ ಇಷ್ಟವಾದ ಕೌಶಲ್ಯ ತರಬೇತಿ ಯಾವುದು? (Popular skill track)",
            "description": "ಮಾಲ್ಪೆ ಮತ್ತು ಕಾರ್ ಸ್ಟ್ರೀಟ್ ಪ್ರದೇಶದ ಯುವಕರಿಗಾಗಿ.",
            "options": [
                "ಮೊಬೈಲ್ ರಿಪೇರಿ",
                "ಮಲ್ಟಿಮೀಡಿಯ ಕ್ರಿಯೇಷನ್",
                "ಉತ್ಪನ್ನ ಮಾರಾಟ ನಿರ್ವಹಣೆ",
                "ತಂತ್ರಜ్ఞಾನ ಆಧಾರಿತ ಮೀನುಗಾರಿಕೆ",
            ],
        }
    ],
}


KANNADA_FAQS: Dict[str, List[Dict[str, object]]] = {
    "Puttur": [
        {
            "title": "ರಸ್ತೆಯ ಗುಂಡಿ ತುರ್ತು ದುರಸ್ತಿ (Emergency pothole fix)",
            "question_keywords": "ಗುದಿಬಿಲಿ, ರಸ್ತೆ ದುರಸ್ತಿ, pothole",
            "solution_kn": (
                "1) ಪೂರೈಸಿದ ಆನ್‌ಲೈನ್ ನಮೂನೆ KN-ROADS портал್ಗೆ ಅಪ್ಲೋಡ್ ಮಾಡಿ.\n"
                "2) ವಾರ್ಡ್ ಕಚೇರಿಗೆ ಕೆಲಸದ ಫೋಟೋಗಳನ್ನು ಕಳುಹಿಸಿ.\n"
                "3) 48 ಗಂಟೆಯೊಳಗೆ ಪ್ರತಿಕ್ರಿಯೆ ಸಿಗದಿದ್ದರೆ MLA ಕೇರ್ ಲೈನ್ +918242226666 ಗೆ ಕರೆ ಮಾಡಿ."
            ),
            "solution_en": (
                "1) Submit the filled form on the KN-ROADS portal.\n"
                "2) Share geotagged photos with the ward office.\n"
                "3) Escalate to MLA care line if unattended for 48 hours."
            ),
            "category": "roads",
        }
    ],
    "Mangalore North": [
        {
            "title": "ಮನೆ ಕಸದ ವಿಂಗಡಣೆ ಹೇಗೆ? (Bin segregation guide)",
            "question_keywords": "ಕಸ, ವಿಂಗಡಣೆ, dry wet waste",
            "solution_kn": (
                "ಹಸಿರು ಡಬ್ಬಿ = ತೇವ ಕಸ, ನೀಲಿ ಡಬ್ಬಿ = ಒಣ ಕಸ, ಕೆಂಪು ಡಬ್ಬಿ = ವೈದ್ಯಕೀಯ ಕಸ.\n"
                "ಎಲ್ಲಾ ಡಬ್ಬಿಗಳಿಗೆ ಕನ್ನಡ ಲೇಬಲ್ ನಕಲುಗಳನ್ನು ನಗರಸಭೆಯಿಂದ ಉಚಿತವಾಗಿ ಪಡೆಯಬಹುದು."
            ),
            "solution_en": (
                "Green bin for wet waste, blue for dry waste, red for bio-medical disposables.\n"
                "Request Kannada bin stickers from MCC helpdesk for free."
            ),
            "category": "sanitation",
        }
    ],
    "Udupi": [
        {
            "title": "ಮಾಲ್ಪೆ ಬೀಚ್ ಸ್ವಯಂಸೇವಕರ ಹಾದಿ (Beach volunteer flow)",
            "question_keywords": "ಬೀಚ್, volunteer, ಸ್ವಚ್ಛತೆ",
            "solution_kn": (
                "1) ಉಡುಪಿ ನಗರಸಭೆ ವೆಬ್‌ಸೈಟ್‌ನಲ್ಲಿ 'ಸ್ವಚ್ಛ ಮಾಲ್ಪೆ' ವಿಭಾಗಕ್ಕೆ ಹೋಗಿ.\n"
                "2) ಕನ್ನಡ ಫಾರ್ಮ್ ತುಂಬಿಸಿ ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ.\n"
                "3) ಆಯ್ಕೆ ಮಾಡಿರುವ ದಿನ ಬೆಳಿಗ್ಗೆ 6:30ಕ್ಕೆ ಬ್ರಿಫಿಂಗ್‌ಗಾಗಿ ಹಾಜರಾಗಿರಿ."
            ),
            "solution_en": (
                "1) Open the 'Clean Malpe' section on the Udupi ULB portal.\n"
                "2) Fill the Kannada volunteer form and choose the slot.\n"
                "3) Report by 6:30 AM for briefing on the selected day."
            ),
            "category": "community",
        }
    ],
}


KANNADA_FEEDBACK: Dict[str, List[Dict[str, object]]] = {
    "Puttur": [
        {
            "title": "ನಗರ ಬಸ್ ವೇಳಾಪಟ್ಟಿ ಕನ್ನಡ ಡಿಜಿಟಲ್ ಬೋರ್ಡ್",
            "content": "ಕನ್ನಡ ಡಿಸ್ಪ್ಲೇ ಬೋರ್ಡ್‌ನಲ್ಲಿ ಮಧ್ಯಾಹ್ನ ಸಮಯಗಳು ಕಾಣಿಸುತ್ತಿಲ್ಲ.",
            "category": "transport",
            "priority": FeedbackPriority.MEDIUM,
        }
    ],
    "Mangalore North": [
        {
            "title": "ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆ ಕನ್ನಡ ಮಾರ್ಗದರ್ಶನ",
            "content": "ವಿಶೇಷ ಚಿಕಿತ್ಸಾ ಕೌಂಟರ್ ಗಳಲ್ಲಿ ಕನ್ನಡ ಸೂಚನ ಫಲಕ ಬೇಕಿದೆ.",
            "category": "health",
            "priority": FeedbackPriority.HIGH,
        }
    ],
    "Udupi": [
        {
            "title": "ಪಾರಂಪರಿಕ ಮೇಳಕ್ಕೆ ಯುವಕರ ಡಿಜಿಟಲ್ ಸೂಚನೆ",
            "content": "ಯುವಕರಿಗೆ ಕನ್ನಡ ಆವರ್ತ ನೋಟಿಫಿಕೇಶನ್ ನೀಡಬೇಕು.",
            "category": "culture",
            "priority": FeedbackPriority.MEDIUM,
        }
    ],
}


KANNADA_SOCIAL_POSTS: Dict[str, List[str]] = {
    "Puttur": [
        "#ಜನಸಂಪರ್ಕ 🚜 ಇಂದು ಪುತ್ತೂರು ವಾರ್ಡ್ 1ರಲ್ಲಿ ರೈತರೊಂದಿಗೆ ಸಂವಾದ ನಡೆಸಿದೆವು. ಕನ್ನಡದಲ್ಲಿ ದಾಖಲೆಗಳ ಡಿಜಿಟಲೀಕರಣ ಚರ್ಚಿಸಲಾಯಿತು.",
    ],
    "Mangalore North": [
        "#ಸ್ವಚ್ಛಮಂಗಳೂರು 💡 ಕದ್ರಿ ಉದ್ಯಾನದಲ್ಲಿ ಹೊಸ ಸ್ಮಾರ್ಟ್ ಲೈಟಿಂಗ್ ಪ್ರಾರಂಭ. ಕನ್ನಡ ಆಡಿಯೊ ಘೋಷಣೆಗಳು ಸೇರಿವೆ!",
    ],
    "Udupi": [
        "#ಸಮುದ್ರಸ್ನೇಹಿ 🌊 ಮಾಲ್ಪೆ ಬೀಚ್ ಸ್ವಯಂಸೇವಕರಿಗೆ ಅಭಿನಂದನೆಗಳು. bilingual ಸೂಚನೆಗಳು ಜಾರಿ.",
    ],
}


KANNADA_FORUM_TOPICS: Dict[str, List[Dict[str, str]]] = {
    "Puttur": [
        {
            "title": "ರಸ್ತೆ ದುರಸ್ತಿಗೆ ಉತ್ತಮ ತಂತ್ರಜ್ಞಾನ | Best Technology for Road Repair",
            "description": "ಪುತ್ತೂರು ತಾಲ್ಲೂಕಿನಲ್ಲಿ ರಸ್ತೆ ಗುಂಡಿ ಸಮಸ್ಯೆಗೆ ಶಾಶ್ವತ ಪರಿಹಾರ ಹುಡುಕುತ್ತಿದ್ದೇವೆ. ಯಾವ ತಂತ್ರಜ್ಞಾನ ಹೆಚ್ಚು ದೀರ್ಘಕಾಲೀನ? ನಿಮ್ಮ ಅನುಭವ ಹಂಚಿಕೊಳ್ಳಿ.",
            "category": "best_practices",
            "tags": "ರಸ್ತೆ,ದುರಸ್ತಿ,ತಂತ್ರಜ್ಞಾನ",
        }
    ],
    "Mangalore North": [
        {
            "title": "ಡಿಜಿಟಲ್ ಶಿಕ್ಷಣ ಯೋಜನೆಗಳು | Digital Education Initiatives",
            "description": "ಮಂಗಳೂರು ಉತ್ತರ ಕ್ಷೇತ್ರದಲ್ಲಿ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಕನ್ನಡ ಮತ್ತು ಇಂಗ್ಲಿಷ್ ಭಾಷೆಗಳಲ್ಲಿ ಡಿಜಿಟಲ್ ಕಲಿಕೆಯ ಸಂಪನ್ಮೂಲಗಳು ಹೇಗೆ ಸುಧಾರಿಸಬಹುದು?",
            "category": "development_ideas",
            "tags": "ಶಿಕ್ಷಣ,ಡಿಜಿಟಲ್,ಕನ್ನಡ",
        }
    ],
    "Udupi": [
        {
            "title": "ಸಮುದ್ರ ಸಂರಕ್ಷಣಾ ಯೋಜನೆಗಳು | Coastal Conservation Plans",
            "description": "ಉಡುಪಿ ತೀರದಲ್ಲಿ ಮಾಲಿನ್ಯ ತಡೆಗೆ ಸಮುದಾಯ ಆಧಾರಿತ ಪರಿಹಾರಗಳು. ಸ್ಥಳೀಯ ಮೀನುಗಾರರು ಮತ್ತು ನಾಗರಿಕರ ಸಹಕಾರ ಹೇಗೆ?",
            "category": "citizen_issues",
            "tags": "ಸಮುದ್ರ,ಪರಿಸರ,ಸಂರಕ್ಷಣೆ",
        }
    ],
}


KANNADA_FORUM_POSTS: Dict[str, List[str]] = {
    "Puttur": [
        "ನಮ್ಮ ವಾರ್ಡ್‌ನಲ್ಲಿ ಹೊಸ ಪ್ರಿಕಾಸ್ಟ್ ಕಾಂಕ್ರೀಟ್ ತಂತ್ರಜ್ಞಾನ ಬಳಸಿದ್ದೇವೆ. 5 ವರ್ಷಗಳ ಖಾತರಿ ಇದೆ. ವೆಚ್ಚ ಕಡಿಮೆ ಮತ್ತು ಗುಣಮಟ್ಟ ಉತ್ತಮ.",
        "ಧನ್ಯವಾದಗಳು! ಈ ತಂತ್ರಜ್ಞಾನದ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ನೀಡಬಹುದೇ? ಯಾವ ಕಂಪನಿ?",
    ],
    "Mangalore North": [
        "ಮಕ್ಕಳಿಗೆ ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ಕೋಡಿಂಗ್ ಕಲಿಸುವ ಆನ್‌ಲೈನ್ ವೇದಿಕೆಗಳಿವೆಯೇ? ದಯವಿಟ್ಟು ಸಲಹೆ ನೀಡಿ.",
        "ನಮ್ಮ ಶಾಲೆಯಲ್ಲಿ Scratch ಬಳಸುತ್ತೇವೆ. ಅದು bilingual interface ಹೊಂದಿದೆ. ವಿದ್ಯಾರ್ಥಿಗಳು ಚೆನ್ನಾಗಿ ಕಲಿಯುತ್ತಿದ್ದಾರೆ.",
    ],
    "Udupi": [
        "ಪ್ಲಾಸ್ಟಿಕ್ ತ್ಯಾಜ್ಯ ಸಂಗ್ರಹಣೆಗೆ ಮೀನುಗಾರರ ಸಹಕಾರ ಅತ್ಯಗತ್ಯ. ಯಾವ ಪ್ರೋತ್ಸಾಹ ಯೋಜನೆಗಳು ಸಾಧ್ಯ?",
        "ಪ್ರತಿ ಕೆಜಿ ಪ್ಲಾಸ್ಟಿಕ್‌ಗೆ ₹10 ನೀಡುವ ಯೋಜನೆ ಅಮಲು ಮಾಡಬಹುದು. ಸ್ಥಳೀಯ ಪಂಚಾಯತಿ ಬಜೆಟ್ ಹಂಚಿಕೆ ಮಾಡಬೇಕು.",
    ],
}


def seed_kannada_demo_data() -> None:
    session = SessionLocal()
    created = {
        "citizens": 0,
        "complaints": 0,
        "news": 0,
        "schedules": 0,
        "tickers": 0,
        "polls": 0,
        "poll_options": 0,
        "votes": 0,
        "faqs": 0,
        "feedback": 0,
        "conferences": 0,
        "ward_budgets": 0,
        "dept_budgets": 0,
        "transactions": 0,
        "social_posts": 0,
        "forum_topics": 0,
        "forum_posts": 0,
    }

    try:
        constituencies = session.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found. Run seed_data.py first.")
            return

        admin_user = session.query(User).filter(User.role == UserRole.ADMIN).first()
        mla_by_constituency = {
            user.constituency_id: user
            for user in session.query(User).filter(User.role == UserRole.MLA).all()
        }
        wards_by_constituency = {
            constituency.id: session.query(Ward)
            .filter(Ward.constituency_id == constituency.id)
            .order_by(Ward.ward_number)
            .all()
            for constituency in constituencies
        }
        departments_by_constituency = {
            constituency.id: session.query(Department)
            .filter(Department.constituency_id == constituency.id)
            .order_by(Department.name)
            .all()
            for constituency in constituencies
        }

        citizens_by_constituency: Dict[str, List[User]] = {}
        now = datetime.utcnow()

        # 1. Citizens
        for constituency in constituencies:
            citizens_by_constituency[constituency.id] = []
            ward_list = wards_by_constituency.get(constituency.id, [])
            citizen_templates = KANNADA_CITIZENS.get(constituency.name, [])
            for index, template in enumerate(citizen_templates):
                existing = session.query(User).filter(User.phone == template["phone"]).first()
                if existing:
                    citizens_by_constituency[constituency.id].append(existing)
                    continue

                ward = ward_list[index % len(ward_list)] if ward_list else None
                citizen = User(
                    id=uuid.uuid4(),
                    name=f"{template['name_kn']} ({template['name_en']})",
                    phone=template["phone"],
                    role=UserRole.CITIZEN,
                    constituency_id=constituency.id,
                    ward_id=ward.id if ward else None,
                    locale_pref="kn",
                    is_active=True,
                )
                session.add(citizen)
                session.flush()
                citizens_by_constituency[constituency.id].append(citizen)
                created["citizens"] += 1

        # 2. Complaints
        for constituency in constituencies:
            ward_list = wards_by_constituency.get(constituency.id, [])
            departments = departments_by_constituency.get(constituency.id, [])
            citizen_pool = citizens_by_constituency.get(constituency.id, [])
            complaint_templates = KANNADA_COMPLAINTS.get(constituency.name, [])
            for template in complaint_templates:
                existing = (
                    session.query(Complaint)
                    .filter(
                        Complaint.constituency_id == constituency.id,
                        Complaint.title == template["title"],
                    )
                    .first()
                )
                if existing:
                    continue

                ward = next(
                    (w for w in ward_list if getattr(w, "ward_number", None) == template["ward_number"]),
                    ward_list[0] if ward_list else None,
                )
                citizen = citizen_pool[0] if citizen_pool else None
                if not citizen:
                    continue

                department = departments[0] if departments else None
                complaint = Complaint(
                    id=uuid.uuid4(),
                    title=template["title"],
                    description=f"{template['description_kn']}\n\nEnglish: {template['description_en']}",
                    category=template["category"],
                    priority=template["priority"],
                    status=ComplaintStatus.SUBMITTED,
                    constituency_id=constituency.id,
                    user_id=citizen.id,
                    ward_id=ward.id if ward else None,
                    dept_id=department.id if department else None,
                    lat=template["lat"],
                    lng=template["lng"],
                    location_description=f"{ward.name if ward else constituency.name} - ಕನ್ನಡ ವರದಿ",
                    assignment_type="ward",
                    created_at=now - timedelta(days=3),
                    updated_at=now - timedelta(days=2),
                    last_activity_at=now - timedelta(days=1),
                    citizen_selected_dept=False,
                )
                session.add(complaint)
                created["complaints"] += 1

        # 3. News + Schedules + Tickers
        for constituency in constituencies:
            mla = mla_by_constituency.get(constituency.id)
            if not mla:
                continue

            news_templates = KANNADA_NEWS.get(constituency.name, [])
            for template in news_templates:
                existing = (
                    session.query(News)
                    .filter(
                        News.constituency_id == constituency.id,
                        News.title == template["title"],
                    )
                    .first()
                )
                if existing:
                    continue

                news = News(
                    id=uuid.uuid4(),
                    title=template["title"],
                    summary=template["summary"],
                    content=template["content"],
                    category=template["category"],
                    priority=template["priority"],
                    constituency_id=constituency.id,
                    mla_id=mla.id,
                    created_by=mla.id,
                    is_published=True,
                    is_featured=True,
                    show_in_ticker=True,
                    published_at=now - timedelta(days=5),
                    tags=template["tags"],
                    source="ನಗರಸಭೆ ಪ್ರಕಟಣೆ",
                    author=mla.name,
                )
                session.add(news)
                created["news"] += 1

            # MLA schedules (single highlight per constituency)
            schedule_title = f"{constituency.name} ಜನಸಂಪರ್ಕ ಶಿಬಿರ"
            existing_schedule = (
                session.query(MLASchedule)
                .filter(
                    MLASchedule.constituency_id == constituency.id,
                    MLASchedule.title == schedule_title,
                )
                .first()
            )
            if not existing_schedule:
                schedule = MLASchedule(
                    id=uuid.uuid4(),
                    title=schedule_title,
                    description="ಪೌರರ ಕನ್ನಡ ದೂರು ಪರಿಹಾರ ಕುಂದುಕೊರತೆ ಸಭೆ.",
                    mla_id=mla.id,
                    constituency_id=constituency.id,
                    created_by=mla.id,
                    schedule_type=ScheduleType.PUBLIC_EVENT,
                    status=ScheduleStatus.SCHEDULED,
                    venue=f"{constituency.name} MLA ಕಛೇರಿ",
                    address=f"{constituency.name} ನಗರಸಭೆ ಸಭಾಂಗಣ",
                    start_datetime=now + timedelta(days=2, hours=10),
                    end_datetime=now + timedelta(days=2, hours=12),
                    expected_attendees=150,
                    max_attendees=250,
                    contact_person="ಪ್ರಗತಿ ಸಮಿತಿ",
                    contact_phone="+918000000111",
                    agenda="ಕನ್ನಡ ಸರ್ವಿಸ್ ಡೆಸ್ಕ್ ಪರಿಚಯ",
                )
                session.add(schedule)
                created["schedules"] += 1

            ticker_messages = KANNADA_TICKERS.get(constituency.name, [])
            for message in ticker_messages:
                existing_ticker = (
                    session.query(TickerItem)
                    .filter(
                        TickerItem.constituency_id == constituency.id,
                        TickerItem.content == message,
                    )
                    .first()
                )
                if existing_ticker:
                    continue

                ticker = TickerItem(
                    id=uuid.uuid4(),
                    content=message,
                    content_type="text",
                    constituency_id=constituency.id,
                    mla_id=mla.id,
                    created_by=mla.id,
                    priority=3,
                    is_active=True,
                    start_time=now - timedelta(hours=1),
                    end_time=now + timedelta(days=7),
                    background_color="#8B5CF6",
                    text_color="#FFFFFF",
                    icon="📢",
                )
                session.add(ticker)
                created["tickers"] += 1

        # 4. Polls
        for constituency in constituencies:
            mla = mla_by_constituency.get(constituency.id)
            poll_templates = KANNADA_POLLS.get(constituency.name, [])
            citizen_pool = citizens_by_constituency.get(constituency.id, [])
            for template in poll_templates:
                existing = (
                    session.query(Poll)
                    .filter(
                        Poll.constituency_id == constituency.id,
                        Poll.title == template["title"],
                    )
                    .first()
                )
                if existing:
                    continue

                poll = Poll(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    title=template["title"],
                    description=template["description"],
                    start_date=now - timedelta(days=1),
                    end_date=now + timedelta(days=14),
                    is_active=True,
                    created_by=mla.id if mla else (admin_user.id if admin_user else uuid.uuid4()),
                )
                session.add(poll)
                session.flush()
                created["polls"] += 1

                for option_text in template["options"]:
                    existing_option = (
                        session.query(PollOption)
                        .filter(PollOption.poll_id == poll.id, PollOption.option_text == option_text)
                        .first()
                    )
                    if existing_option:
                        continue
                    option = PollOption(
                        id=uuid.uuid4(),
                        poll_id=poll.id,
                        option_text=option_text,
                    )
                    session.add(option)
                    session.flush()
                    created["poll_options"] += 1

                # Cast a single vote from the first available Kannada citizen
                poll_options = (
                    session.query(PollOption)
                    .filter(PollOption.poll_id == poll.id)
                    .order_by(PollOption.created_at)
                    .all()
                )
                voter = citizen_pool[0] if citizen_pool else None
                if voter and poll_options:
                    existing_vote = (
                        session.query(Vote)
                        .filter(Vote.poll_id == poll.id, Vote.user_id == voter.id)
                        .first()
                    )
                    if not existing_vote:
                        vote = Vote(
                            id=uuid.uuid4(),
                            poll_id=poll.id,
                            option_id=poll_options[0].id,
                            user_id=voter.id,
                        )
                        session.add(vote)
                        created["votes"] += 1

        # 5. FAQs
        for constituency in constituencies:
            templates = KANNADA_FAQS.get(constituency.name, [])
            creator_id = (
                mla_by_constituency.get(constituency.id).id
                if mla_by_constituency.get(constituency.id)
                else (admin_user.id if admin_user else None)
            )
            if not creator_id:
                continue

            for template in templates:
                existing = (
                    session.query(FAQSolution)
                    .filter(
                        FAQSolution.constituency_id == constituency.id,
                        FAQSolution.title == template["title"],
                    )
                    .first()
                )
                if existing:
                    continue

                faq = FAQSolution(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    title=template["title"],
                    kannada_title=template["title"],
                    question_keywords=template["question_keywords"],
                    solution_text=template["solution_en"],
                    kannada_solution=template["solution_kn"],
                    solution_steps=template["solution_kn"],
                    category=template["category"],
                    created_by=creator_id,
                )
                session.add(faq)
                created["faqs"] += 1

        # 6. Citizen feedback and conferences
        for constituency in constituencies:
            mla = mla_by_constituency.get(constituency.id)
            ward_list = wards_by_constituency.get(constituency.id, [])
            departments = departments_by_constituency.get(constituency.id, [])
            citizen_pool = citizens_by_constituency.get(constituency.id, [])
            templates = KANNADA_FEEDBACK.get(constituency.name, [])
            for idx, template in enumerate(templates):
                reference = f"KNF-{constituency.code}-{idx + 1}" if constituency.code else f"KNF-{idx + 1}"
                existing = (
                    session.query(CitizenFeedback)
                    .filter(CitizenFeedback.reference_number == reference)
                    .first()
                )
                if existing:
                    continue

                citizen = citizen_pool[idx % len(citizen_pool)] if citizen_pool else None
                if not citizen:
                    continue

                ward = ward_list[idx % len(ward_list)] if ward_list else None
                department = departments[0] if departments else None
                feedback = CitizenFeedback(
                    id=uuid.uuid4(),
                    title=template["title"],
                    content=template["content"],
                    feedback_type=FeedbackType.SUGGESTION,
                    status=FeedbackStatus.UNDER_REVIEW,
                    priority=template["priority"],
                    citizen_id=citizen.id,
                    constituency_id=constituency.id,
                    assigned_to=mla.id if mla else None,
                    department_id=department.id if department else None,
                    category=template["category"],
                    ward_id=ward.id if ward else None,
                    reference_number=reference,
                    response_required=True,
                    response_deadline=now + timedelta(days=5),
                    created_at=now - timedelta(days=2),
                )
                session.add(feedback)
                created["feedback"] += 1

            conference_code = f"KN-CONNECT-{constituency.code}" if constituency.code else f"KN-CONNECT-{constituency.id}"[:8]
            existing_conf = (
                session.query(VideoConference)
                .filter(VideoConference.meeting_id == conference_code)
                .first()
            )
            if not existing_conf and mla:
                conference = VideoConference(
                    id=uuid.uuid4(),
                    title=f"{constituency.name} ಕನ್ನಡ ಜನಸಂಪರ್ಕ ಸಂವಾದ",
                    description="ಪೌರರ Kannada-first grievance redressal townhall.",
                    conference_type=VideoConferenceType.TOWN_HALL,
                    status=VideoConferenceStatus.SCHEDULED,
                    host_id=mla.id,
                    constituency_id=constituency.id,
                    scheduled_start=now + timedelta(days=3, hours=9),
                    scheduled_end=now + timedelta(days=3, hours=11),
                    max_participants=500,
                    is_public=True,
                    requires_registration=True,
                    platform="zoom",
                    meeting_id=conference_code,
                    meeting_url=f"https://zoom.example.com/{conference_code}",
                    meeting_password="KN2025",
                    host_url=f"https://zoom.example.com/host/{conference_code}",
                    venue=f"{constituency.name} MLA ಆಫೀಸ್",
                    address=f"{constituency.name} ಕನ್ನಡ ಸೇವಾ ಕೇಂದ್ರ",
                    allowed_roles="citizen,mla,moderator",
                    attachment_urls="",
                )
                session.add(conference)
                created["conferences"] += 1

        # 7. Budgets and transactions
        for constituency in constituencies:
            wards = wards_by_constituency.get(constituency.id, [])
            departments = departments_by_constituency.get(constituency.id, [])
            if not wards or not departments:
                continue

            ward_budget_existing = (
                session.query(WardBudget)
                .filter(
                    WardBudget.ward_id == wards[0].id,
                    WardBudget.financial_year == "2024-2025",
                    WardBudget.category == "roads",
                )
                .first()
            )
            if not ward_budget_existing:
                ward_budget = WardBudget(
                    id=uuid.uuid4(),
                    ward_id=wards[0].id,
                    financial_year="2024-2025",
                    category="roads",
                    allocated=1_200_000,
                    spent=480_000,
                    committed=300_000,
                    notes="ಪುತ್ತೂರು ವಾರ್ಡ್ ರಸ್ತೆ ಗುಂಡಿ ಸಮಗ್ರ ಯೋಜನೆ (Kannada priority).",
                )
                session.add(ward_budget)
                session.flush()
                created["ward_budgets"] += 1
            else:
                ward_budget = ward_budget_existing

            dept_budget_existing = (
                session.query(DepartmentBudget)
                .filter(
                    DepartmentBudget.department_id == departments[0].id,
                    DepartmentBudget.financial_year == "2024-2025",
                    DepartmentBudget.category == "water",
                )
                .first()
            )
            if not dept_budget_existing:
                dept_budget = DepartmentBudget(
                    id=uuid.uuid4(),
                    department_id=departments[0].id,
                    constituency_id=constituency.id,
                    financial_year="2024-2025",
                    category="water",
                    allocated=2_500_000,
                    spent=900_000,
                    committed=600_000,
                    notes="ಕನ್ನಡ ನೀರು ಪೂರೈಕೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಯೋಜನೆ.",
                )
                session.add(dept_budget)
                session.flush()
                created["dept_budgets"] += 1
            else:
                dept_budget = dept_budget_existing

            if admin_user:
                existing_txn = (
                    session.query(BudgetTransaction)
                    .filter(
                        BudgetTransaction.department_budget_id == dept_budget.id,
                        BudgetTransaction.description == "Kannada water alert campaign",
                    )
                    .first()
                )
                if not existing_txn:
                    transaction = BudgetTransaction(
                        id=uuid.uuid4(),
                        department_budget_id=dept_budget.id,
                        transaction_type="expense",
                        amount=150_000,
                        description="Kannada water alert campaign",
                        performed_by=admin_user.id,
                    )
                    session.add(transaction)
                    created["transactions"] += 1

        # 8. Social posts
        for constituency in constituencies:
            mla = mla_by_constituency.get(constituency.id)
            if not mla:
                continue

            posts = KANNADA_SOCIAL_POSTS.get(constituency.name, [])
            for content in posts:
                existing = (
                    session.query(SocialPost)
                    .filter(
                        SocialPost.author_id == mla.id,
                        SocialPost.content == content,
                    )
                    .first()
                )
                if existing:
                    continue

                post = SocialPost(
                    id=uuid.uuid4(),
                    author_id=mla.id,
                    author_name=mla.name,
                    author_role=mla.role.value,
                    content=content,
                    post_type=PostType.TEXT,
                    status=PostStatus.PUBLISHED,
                    constituency_id=constituency.id,
                    is_featured=True,
                    is_pinned=True,
                    tags="ಕನ್ನಡ,ಸಮುದಾಯ",
                    published_at=now - timedelta(days=1),
                )
                session.add(post)
                created["social_posts"] += 1

        # 9. Forum topics and posts
        citizens_by_constituency = {}
        for constituency in constituencies:
            citizens_by_constituency[constituency.id] = (
                session.query(User)
                .filter(
                    User.role == UserRole.CITIZEN,
                    User.constituency_id == constituency.id,
                )
                .limit(3)
                .all()
            )

        for constituency in constituencies:
            mla = mla_by_constituency.get(constituency.id)
            citizens = citizens_by_constituency.get(constituency.id, [])
            
            topics_data = KANNADA_FORUM_TOPICS.get(constituency.name, [])
            posts_data = KANNADA_FORUM_POSTS.get(constituency.name, [])
            
            for topic_data in topics_data:
                # Check if topic already exists
                existing_topic = (
                    session.query(ForumTopic)
                    .filter(
                        ForumTopic.title == topic_data["title"],
                        ForumTopic.constituency_id == constituency.id,
                    )
                    .first()
                )
                if existing_topic:
                    continue

                # Create forum topic
                author = mla if mla else citizens[0] if citizens else admin_user
                if not author:
                    continue

                topic = ForumTopic(
                    id=uuid.uuid4(),
                    title=topic_data["title"],
                    description=topic_data["description"],
                    category=ForumCategory(topic_data["category"]),
                    author_id=author.id,
                    author_name=author.name,
                    author_role=author.role.value,
                    constituency_id=constituency.id,
                    status=TopicStatus.OPEN,
                    is_public=True,
                    tags=topic_data["tags"],
                    views_count=15,
                    created_at=now - timedelta(days=3),
                    last_activity_at=now - timedelta(hours=12),
                )
                session.add(topic)
                session.flush()
                created["forum_topics"] += 1

                # Add posts to the topic
                for idx, post_content in enumerate(posts_data[:2]):  # Max 2 posts per topic
                    # Alternate between MLA and citizens
                    post_author = citizens[idx % len(citizens)] if citizens else author
                    
                    existing_post = (
                        session.query(ForumPost)
                        .filter(
                            ForumPost.topic_id == topic.id,
                            ForumPost.content == post_content,
                        )
                        .first()
                    )
                    if existing_post:
                        continue

                    forum_post = ForumPost(
                        id=uuid.uuid4(),
                        topic_id=topic.id,
                        content=post_content,
                        author_id=post_author.id,
                        author_name=post_author.name,
                        author_role=post_author.role.value,
                        is_approved=True,
                        likes_count=3 + idx,
                        created_at=now - timedelta(days=2, hours=idx * 6),
                    )
                    session.add(forum_post)
                    created["forum_posts"] += 1

                # Update topic reply count
                topic.replies_count = len(posts_data[:2])

        session.commit()
        print("✅ Kannada demo data seed complete.")
        print(
            "Summary:" +
            " | ".join(f" {key}: {value}" for key, value in created.items() if value > 0)
        )
    except Exception as exc:  # pragma: no cover - CLI helper
        session.rollback()
        print(f"❌ Error seeding Kannada demo data: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_kannada_demo_data()
