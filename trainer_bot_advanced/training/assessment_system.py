# Placeholder for AssessmentSystem
import random
class AssessmentSystem:
    def __init__(self):
        print("AS initialized")
    async def run_basic_test(self, bot):
        return {
            "overall_score": random.uniform(50, 85),
            "skills": {"تحليل البيانات": random.uniform(40,90)}
        }
    async def run_course_test(self, bot, course):
            return {"score": random.uniform(65, 95)}
