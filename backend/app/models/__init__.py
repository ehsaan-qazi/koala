"""Models package — import all models so Alembic can discover them."""

from app.models.user import User  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.roadmap_node import RoadmapNode  # noqa: F401
from app.models.topic import Topic  # noqa: F401
from app.models.topic_completion import TopicCompletion  # noqa: F401
from app.models.note import Note  # noqa: F401
from app.models.note_link import NoteLink  # noqa: F401
from app.models.self_assessment_log import SelfAssessmentLog  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.goal_course import GoalCourse  # noqa: F401
from app.models.streak import Streak  # noqa: F401
from app.models.streak_daily_log import StreakDailyLog  # noqa: F401
from app.models.gpa_entry import GpaEntry  # noqa: F401
