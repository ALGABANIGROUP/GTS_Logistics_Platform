from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class Course:
    """نموذج الدورة التدريبية"""
    id: str
    name: str
    description: str
    level: str
    duration_hours: int
    topics: List[str]
    skills_improved: List[str]
    prerequisites: List[str]
    practical_scenarios: int
    passing_score: int = 70

class CourseManager:
    """
    إدارة جميع الدورات التدريبية
    """
    
    def __init__(self):
        self.courses = self.load_courses()
        
    def load_courses(self) -> Dict[str, List[Course]]:
        """
        تحميل جميع الدورات
        """
        return {
            "security": [
                Course(
                    id="SEC-101",
                    name="أساسيات الأمن السيبراني",
                    description="مقدمة في مفاهيم الأمان الأساسية",
                    level="مبتدئ",
                    duration_hours=4,
                    topics=["التصيد", "كلمات المرور", "التشفير", "جدران الحماية"],
                    skills_improved=["وعي أمني", "كشف التهديدات", "استجابة أولية"],
                    prerequisites=[],
                    practical_scenarios=3
                ),
                Course(
                    id="SEC-201",
                    name="مكافحة الهجمات المتقدمة",
                    description="التصدي للهجمات المعقدة",
                    level="متقدم",
                    duration_hours=8,
                    topics=["DDoS", "اختراق", "هجمات اليوم صفر", "تحليل خبيث"],
                    skills_improved=["تحليل متقدم", "استجابة سريعة", "احتواء"],
                    prerequisites=["SEC-101"],
                    practical_scenarios=5
                ),
                Course(
                    id="SEC-301",
                    name="خبير أمن المعلومات",
                    description="أعلى مستويات الأمن السيبراني",
                    level="خبير",
                    duration_hours=12,
                    topics=["هندسة عكسية", "تحقيق جنائي", "اختبار اختراق", "إدارة أزمات"],
                    skills_improved=["خبرة متعمقة", "ابتكار حلول", "قيادة فرق"],
                    prerequisites=["SEC-201"],
                    practical_scenarios=7
                )
            ],
            "logistics": [
                Course(
                    id="LOG-101",
                    name="إدارة العمليات اللوجستية",
                    description="أساسيات إدارة الشحن والتوزيع",
                    level="مبتدئ",
                    duration_hours=4,
                    topics=["تخطيط مسارات", "إدارة مخزون", "تتبع شحنات"],
                    skills_improved=["تنظيم", "متابعة", "تخطيط"],
                    prerequisites=[],
                    practical_scenarios=3
                ),
                Course(
                    id="LOG-201",
                    name="إدارة الأزمات اللوجستية",
                    description="التعامل مع الطوارئ في سلسلة التوريد",
                    level="متقدم",
                    duration_hours=6,
                    topics=["تأخيرات", "أعطال", "ظروف قاهرة", "بدائل سريعة"],
                    skills_improved=["حل أزمات", "سرعة قرار", "مرونة"],
                    prerequisites=["LOG-101"],
                    practical_scenarios=4
                )
            ],
            "customer_service": [
                Course(
                    id="CS-101",
                    name="خدمة العملاء المتميزة",
                    description="أساسيات التعامل مع العملاء",
                    level="مبتدئ",
                    duration_hours=3,
                    topics=["تواصل فعال", "حل شكاوى", "لباقة"],
                    skills_improved=["تواصل", "صبر", "حل مشكلات"],
                    prerequisites=[],
                    practical_scenarios=4
                ),
                Course(
                    id="CS-201",
                    name="التعامل مع العملاء الصعبين",
                    description="تقنيات متقدمة لتهدئة العملاء",
                    level="متقدم",
                    duration_hours=5,
                    topics=["عملاء غاضبون", "تهديد بالمغادرة", "مطالب غير معقولة"],
                    skills_improved=["تفاوض", "تأثير", "إقناع"],
                    prerequisites=["CS-101"],
                    practical_scenarios=6
                )
            ]
        }
    
    async def select_courses(self, learning_path: Dict, weak_points: List[str], target_level: str) -> List[Dict]:
        """
        اختيار الدورات المناسبة حسب المسار ونقاط الضعف
        """
        selected = []
        specialization = learning_path['specialization']
        available = self.courses.get(specialization, [])
        
        # تصفية حسب المستوى
        level_courses = [c for c in available if c.level in self.get_levels_to_target(target_level)]
        
        # اختيار الدورات التي تعالج نقاط الضعف
        for course in level_courses:
            if any(skill in course.skills_improved for skill in weak_points):
                selected.append({
                    'id': course.id,
                    'name': course.name,
                    'level': course.level,
                    'duration': course.duration_hours,
                    'topics': course.topics,
                    'skills_improved': course.skills_improved,
                    'practical_scenarios': course.practical_scenarios,
                    'theory_hours': course.duration_hours // 2,
                    'practical_hours': course.duration_hours // 2
                })
        
        return selected[:5]  # حد أقصى 5 دورات
    
    def get_levels_to_target(self, target_level: str) -> List[str]:
        """تحديد المستويات المطلوبة للوصول للهدف"""
        levels = ['مبتدئ', 'متوسط', 'متقدم', 'خبير', 'معلم']
        try:
            target_index = levels.index(target_level)
            return levels[:target_index + 1]
        except:
            return ['مبتدئ', 'متوسط', 'متقدم']
