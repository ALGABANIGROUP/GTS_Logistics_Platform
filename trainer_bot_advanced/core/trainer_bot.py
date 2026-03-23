# core/trainer_bot.py

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import random  # للمحاكاة

# استيراد المكونات الأخرى
from core.knowledge_base import KnowledgeBase
from core.learning_paths import LearningPathManager
from training.course_manager import CourseManager
from training.scenario_generator import ScenarioGenerator
from training.assessment_system import AssessmentSystem
from integration.bot_connector import BotConnector
from reports.report_generator import ReportGenerator


class BotSpecialization(Enum):
    """تخصصات البوتات"""
    SECURITY = "security"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    CUSTOMER_SERVICE = "customer_service"
    LEGAL = "legal"
    MAINTENANCE = "maintenance"
    OPERATIONS = "operations"
    SALES = "sales"
    MARKETING = "marketing"

class TrainingLevel(Enum):
    """مستويات التدريب"""
    BEGINNER = "مبتدئ"
    INTERMEDIATE = "متوسط"
    ADVANCED = "متقدم"
    EXPERT = "خبير"
    MASTER = "معلم"

@dataclass
class BotProfile:
    """ملف البوت المتدرب"""
    bot_id: str
    name: str
    specialization: BotSpecialization
    version: str
    current_level: TrainingLevel
    experience_points: int = 0
    skills: Dict[str, float] = None
    training_history: List[Dict] = None
    weak_points: List[str] = None
    strengths: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = {}
        if self.training_history is None:
            self.training_history = []
        if self.weak_points is None:
            self.weak_points = []
        if self.strengths is None:
            self.strengths = []

class TrainerBot:
    """
    المدرب الرئيسي لجميع البوتات في المنصة
    """
    
    def __init__(self, name: str = "المدرب الذكي GTS"):
        self.name = name
        self.bots_in_training: Dict[str, BotProfile] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.training_stats = {
            'total_sessions': 0,
            'total_hours': 0,
            'success_rate': 0,
            'top_students': []
        }
        
        # تحميل المكونات
        self.knowledge_base = KnowledgeBase()
        self.learning_paths = LearningPathManager()
        self.course_manager = CourseManager()
        self.scenario_generator = ScenarioGenerator()
        self.assessment_system = AssessmentSystem()
        self.bot_connector = BotConnector()
        self.report_generator = ReportGenerator()
        
        print(f"✅ {self.name} جاهز للعمل")
    
    async def register_bot(self, bot_data: Dict) -> BotProfile:
        """
        تسجيل بوت جديد للتدريب
        """
        bot_id = hashlib.md5(f"{bot_data['name']}_{datetime.now()}".encode()).hexdigest()[:8]
        
        profile = BotProfile(
            bot_id=bot_id,
            name=bot_data['name'],
            specialization=BotSpecialization(bot_data['specialization']),
            version=bot_data.get('version', '1.0'),
            current_level=TrainingLevel(bot_data.get('level', 'مبتدئ'))
        )
        
        self.bots_in_training[bot_id] = profile
        print(f"📝 تم تسجيل بوت جديد: {bot_data['name']} (ID: {bot_id})")
        
        return profile
    
    async def assess_bot_capabilities(self, bot_id: str) -> Dict:
        """
        تقييم قدرات البوت الحالية
        """
        bot = self.bots_in_training.get(bot_id)
        if not bot:
            return {"error": "البوت غير مسجل"}
        
        print(f"
🔍 تقييم قدرات {bot.name}...")
        
        # اختبار المعرفة الأساسية
        basic_test = await self.assessment_system.run_basic_test(bot)
        
        # تحليل نقاط القوة والضعف
        strengths, weaknesses = await self.analyze_skills(bot)
        
        bot.strengths = strengths
        bot.weak_points = weaknesses
        
        # تحديث ملف البوت
        bot.skills = basic_test['skills']
        
        return {
            'bot_name': bot.name,
            'overall_score': basic_test['overall_score'],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommended_level': self.determine_recommended_level(basic_test['overall_score']),
            'skills_breakdown': basic_test['skills']
        }
    
    async def create_training_plan(self, bot_id: str, goal: str = None) -> Dict:
        """
        إنشاء خطة تدريب مخصصة للبوت
        """
        bot = self.bots_in_training.get(bot_id)
        if not bot:
            return {"error": "البوت غير مسجل"}
        
        print(f"
📋 إنشاء خطة تدريب لـ {bot.name}...")
        
        # تحليل احتياجات التدريب
        needs_analysis = await self.analyze_training_needs(bot)
        
        # تحديد مسار التعلم المناسب
        learning_path = self.learning_paths.get_path(
            specialization=bot.specialization,
            current_level=bot.current_level,
            goal=goal or needs_analysis['primary_goal']
        )
        
        # اختيار الدورات المناسبة
        courses = await self.course_manager.select_courses(
            learning_path=learning_path,
            weak_points=bot.weak_points,
            target_level=needs_analysis['target_level']
        )
        
        # إنشاء الجدول الزمني
        schedule = self.create_training_schedule(courses, bot)
        
        training_plan = {
            'bot_id': bot_id,
            'bot_name': bot.name,
            'goal': goal or needs_analysis['primary_goal'],
            'duration_days': schedule['total_days'],
            'total_hours': schedule['total_hours'],
            'courses': courses,
            'schedule': schedule['daily_schedule'],
            'milestones': self.define_milestones(courses),
            'estimated_completion': (datetime.now() + timedelta(days=schedule['total_days'])).isoformat()
        }
        
        # حفظ الخطة
        plan_id = f"plan_{bot_id}_{datetime.now().timestamp()}"
        self.active_sessions[plan_id] = training_plan
        
        return training_plan
    
    async def start_training(self, plan_id: str) -> Dict:
        """
        بدء تنفيذ خطة التدريب
        """
        plan = self.active_sessions.get(plan_id)
        if not plan:
            return {"error": "خطة التدريب غير موجودة"}
        
        bot_id = plan['bot_id']
        bot = self.bots_in_training.get(bot_id)
        
        print(f"
🎯 بدء تدريب {bot.name}")
        print("=" * 50)
        
        results = {
            'courses_completed': [],
            'total_score': 0,
            'improvements': {},
            'certificates': []
        }
        
        # تنفيذ الدورات حسب الجدول
        for day, day_courses in enumerate(plan['schedule'], 1):
            print(f"
📅 اليوم {day}:")
            
            for course in day_courses:
                print(f"  📚 دورة: {course['name']}")
                
                # تدريب نظري
                theory_result = await self.conduct_theoretical_training(bot, course)
                
                # تدريب عملي (محاكاة)
                practical_result = await self.conduct_practical_training(bot, course)
                
                # اختبار نهائي
                final_test = await self.assessment_system.run_course_test(bot, course)
                
                # حساب النتيجة
                course_score = (theory_result['score'] * 0.3 + 
                              practical_result['score'] * 0.4 + 
                              final_test['score'] * 0.3)
                
                results['courses_completed'].append({
                    'course_name': course['name'],
                    'score': course_score,
                    'theory_score': theory_result['score'],
                    'practical_score': practical_result['score'],
                    'test_score': final_test['score']
                })
                
                results['total_score'] += course_score
                
                # تحديث مهارات البوت
                await self.update_bot_skills(bot, course, course_score)
                
                print(f"    ✅ النتيجة: {course_score:.1f}%")
        
        # حساب المعدل النهائي
        avg_score = results['total_score'] / len(results['courses_completed'])
        results['final_score'] = avg_score
        
        # تحديد التحسن
        results['improvements'] = await self.calculate_improvements(bot, plan)
        
        # منح الشهادات
        if avg_score >= 70:
            certificate = await self.issue_certificate(bot, plan, avg_score)
            results['certificates'].append(certificate)
        
        # تحديث مستوى البوت
        await self.update_bot_level(bot, avg_score)
        
        return results
    
    async def conduct_theoretical_training(self, bot: BotProfile, course: Dict) -> Dict:
        """
        تدريب نظري مع محتوى تفاعلي
        """
        # محاكاة وقت التدريب
        await asyncio.sleep(1)
        
        # إنشاء محتوى تعليمي مخصص
        content = self.generate_training_content(bot, course)
        
        # اختبار فهم المحتوى
        comprehension = random.uniform(70, 95)
        
        return {
            'content': content,
            'score': comprehension,
            'duration': course.get('theory_hours', 2),
            'topics_covered': course.get('topics', [])
        }
    
    async def conduct_practical_training(self, bot: BotProfile, course: Dict) -> Dict:
        """
        تدريب عملي عبر محاكاة سيناريوهات واقعية
        """
        # توليد سيناريوهات مناسبة
        scenarios = await self.scenario_generator.generate_scenarios(
            specialization=bot.specialization,
            level=bot.current_level,
            course_topics=course.get('topics', [])
        )
        
        total_score = 0
        results = []
        
        for scenario in scenarios:
            print(f"    🎮 محاكاة: {scenario['name']}")
            
            # تنفيذ السيناريو
            result = await self.run_simulation(bot, scenario)
            total_score += result['score']
            results.append(result)
            
            print(f"      النتيجة: {result['score']}% - {result['feedback']}")
        
        avg_score = total_score / len(scenarios) if scenarios else 0
        
        return {
            'score': avg_score,
            'scenarios_completed': len(scenarios),
            'details': results
        }
    
    async def run_simulation(self, bot: BotProfile, scenario: Dict) -> Dict:
        """
        تنفيذ سيناريو محاكاة واحد
        """
        # محاكاة أداء البوت حسب مهاراته
        base_performance = random.uniform(60, 95)
        
        # تعديل الأداء حسب نقاط القوة والضعف
        if any(skill in scenario['required_skills'] for skill in bot.strengths):
            base_performance += 10
        
        if any(skill in scenario['required_skills'] for skill in bot.weak_points):
            base_performance -= 15
        
        final_score = max(0, min(100, base_performance))
        
        # توليد تقييم
        if final_score >= 90:
            feedback = "أداء استثنائي! تعامل مع السيناريو باحترافية"
        elif final_score >= 75:
            feedback = "أداء جيد جداً مع بعض الملاحظات البسيطة"
        elif final_score >= 60:
            feedback = "أداء مقبول يحتاج تحسين في سرعة الاستجابة"
        else:
            feedback = "يحتاج تدريب مكثف على هذا النوع من السيناريوهات"
        
        return {
            'scenario_name': scenario['name'],
            'score': final_score,
            'feedback': feedback,
            'time_taken': scenario.get('duration', 5),
            'mistakes': self.analyze_mistakes(bot, scenario, final_score)
        }
    
    async def analyze_training_needs(self, bot: BotProfile) -> Dict:
        """
        تحليل احتياجات التدريب للبوت
        """
        needs = {
            'primary_goal': None,
            'target_level': None,
            'priority_areas': [],
            'estimated_duration': 0
        }
        
        # تحديد الهدف الرئيسي حسب نقاط الضعف
        if bot.weak_points:
            needs['priority_areas'] = bot.weak_points[:3]
            
            if 'security' in str(bot.weak_points):
                needs['primary_goal'] = 'تعزيز الأمان'
            elif 'customer' in str(bot.weak_points):
                needs['primary_goal'] = 'تحسين خدمة العملاء'
            else:
                needs['primary_goal'] = 'تطوير المهارات الأساسية'
        
        # تحديد المستوى المستهدف
        level_scores = {
            TrainingLevel.BEGINNER: 1,
            TrainingLevel.INTERMEDIATE: 2,
            TrainingLevel.ADVANCED: 3,
            TrainingLevel.EXPERT: 4,
            TrainingLevel.MASTER: 5
        }
        
        current_level_score = level_scores[bot.current_level]
        if current_level_score < 5:
            needs['target_level'] = list(TrainingLevel)[current_level_score]
        
        # تقدير المدة
        needs['estimated_duration'] = len(needs['priority_areas']) * 3  # أيام
        
        return needs
    
    async def analyze_skills(self, bot: BotProfile) -> tuple[List[str], List[str]]:
        """
        تحليل مهارات البوت وتحديد نقاط القوة والضعف
        """
        # محاكاة تحليل المهارات
        all_skills = [
            'تحليل البيانات', 'اتخاذ القرارات', 'التواصل', 
            'حل المشكلات', 'الأمان', 'التخطيط', 'التنظيم',
            'المرونة', 'الدقة', 'السرعة'
        ]
        
        # توليد نقاط عشوائية للتوضيح
        import random
        strengths = random.sample(all_skills, 3)
        weaknesses = random.sample([s for s in all_skills if s not in strengths], 2)
        
        return strengths, weaknesses
    
    def determine_recommended_level(self, score: float) -> str:
        """تحديد المستوى المناسب حسب الدرجة"""
        if score >= 90:
            return "خبير"
        elif score >= 75:
            return "متقدم"
        elif score >= 60:
            return "متوسط"
        else:
            return "مبتدئ"
    
    def create_training_schedule(self, courses: List[Dict], bot: BotProfile) -> Dict:
        """
        إنشاء جدول تدريب
        """
        schedule = {
            'total_days': len(courses),
            'total_hours': sum(c.get('duration', 4) for c in courses),
            'daily_schedule': []
        }
        
        # توزيع الدورات على أيام
        for i, course in enumerate(courses):
            day_courses = [course]  # يمكن توزيع أكثر من دورة في اليوم
            schedule['daily_schedule'].append(day_courses)
        
        return schedule
    
    def define_milestones(self, courses: List[Dict]) -> List[Dict]:
        """
        تحديد مراحل التقدم
        """
        milestones = []
        for i, course in enumerate(courses, 1):
            milestones.append({
                'milestone': i,
                'course': course['name'],
                'expected_score': 70 + (i * 5),
                'reward': f'شهادة إتمام {course["name"]}'
            })
        return milestones
    
    async def update_bot_skills(self, bot: BotProfile, course: Dict, score: float):
        """
        تحديث مهارات البوت بعد الدورة
        """
        for skill in course.get('skills_improved', []):
            current = bot.skills.get(skill, 50)
            improvement = (score - current) * 0.3  # تحسن بنسبة 30% من الفرق
            bot.skills[skill] = min(100, current + improvement)
    
    async def calculate_improvements(self, bot: BotProfile, plan: Dict) -> Dict:
        """
        حساب نسبة التحسن
        """
        improvements = {}
        for skill in plan.get('target_skills', []):
            improvements[skill] = f"+{random.uniform(5, 20):.1f}%"
        return improvements
    
    async def issue_certificate(self, bot: BotProfile, plan: Dict, score: float) -> Dict:
        """
        إصدار شهادة إتمام التدريب
        """
        certificate = {
            'bot_name': bot.name,
            'specialization': bot.specialization.value,
            'completion_date': datetime.now().isoformat(),
            'final_score': f"{score:.1f}%",
            'level_achieved': self.determine_recommended_level(score),
            'courses_completed': [c['name'] for c in plan['courses']],
            'certificate_id': hashlib.md5(f"{bot.bot_id}_{datetime.now()}".encode()).hexdigest()[:12].upper()
        }
        
        print(f"
🏆 تم إصدار شهادة للبوت {bot.name}")
        print(f"   رقم الشهادة: {certificate['certificate_id']}")
        print(f"   المستوى: {certificate['level_achieved']}")
        
        return certificate
    
    async def update_bot_level(self, bot: BotProfile, final_score: float):
        """
        تحديث مستوى البوت بعد التدريب
        """
        new_level = self.determine_recommended_level(final_score)
        bot.current_level = TrainingLevel(new_level)
        print(f"
📈 تم ترقية {bot.name} إلى المستوى: {new_level}")
    
    def generate_training_content(self, bot: BotProfile, course: Dict) -> List[Dict]:
        """
        توليد محتوى تدريبي مخصص
        """
        content = []
        for topic in course.get('topics', []):
            content.append({
                'topic': topic,
                'materials': [
                    f'شرح مفصل لـ {topic}',
                    f'أمثلة عملية في {topic}',
                    f'تمارين تطبيقية على {topic}'
                ],
                'difficulty': bot.current_level.value
            })
        return content
    
    def analyze_mistakes(self, bot: BotProfile, scenario: Dict, score: float) -> List[str]:
        """
        تحليل الأخطاء في السيناريو
        """
        mistakes = []
        if score < 70:
            if 'سرعة' in bot.weak_points:
                mistakes.append("تأخر في الاستجابة للتهديد")
            if 'دقة' in bot.weak_points:
                mistakes.append("أخطاء في تحديد نوع التهديد")
            if 'تحليل' in bot.weak_points:
                mistakes.append("ضعف في تحليل الموقف")
        return mistakes
