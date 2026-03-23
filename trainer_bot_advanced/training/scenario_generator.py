import random
from typing import Dict, List
from datetime import datetime

class ScenarioGenerator:
    """
    توليد سيناريوهات محاكاة واقعية
    """
    
    def __init__(self):
        self.scenario_templates = self.load_templates()
        self.generated_scenarios = []
    
    def load_templates(self) -> Dict:
        """تحميل قوالب السيناريوهات"""
        return {
            "security": [
                {
                    "name": "هجوم تصيد مستهدف",
                    "description": "محاولة اختراق عبر بريد مزيف يبدو رسمياً",
                    "difficulty": 7,
                    "duration": 15,
                    "required_skills": ["تحليل", "كشف", "استجابة"],
                    "steps": 4
                },
                {
                    "name": "هجوم DDoS متعدد المراحل",
                    "description": "هجوم منسق لإسقاط النظام",
                    "difficulty": 9,
                    "duration": 25,
                    "required_skills": ["تحليل متقدم", "استجابة سريعة", "تنسيق"],
                    "steps": 6
                },
                {
                    "name": "اختراق داخلي",
                    "description": "موظف يحاول سرقة بيانات حساسة",
                    "difficulty": 8,
                    "duration": 20,
                    "required_skills": ["مراقبة", "تحقيق", "احتواء"],
                    "steps": 5
                }
            ],
            "logistics": [
                {
                    "name": "تأخير 10 شحنات حرجة",
                    "description": "عطل مفاجئ في نظام التبريد لشاحنات طبية",
                    "difficulty": 8,
                    "duration": 30,
                    "required_skills": ["تخطيط", "حل أزمات", "سرعة قرار"],
                    "steps": 5
                },
                {
                    "name": "إضراب عمالي مفاجئ",
                    "description": "توقف 50% من السائقين عن العمل",
                    "difficulty": 9,
                    "duration": 40,
                    "required_skills": ["تفاوض", "تنسيق", "إيجاد بدائل"],
                    "steps": 7
                }
            ],
            "customer_service": [
                {
                    "name": "عميل غاضب جداً",
                    "description": "عميل يهدد بمقاضاة الشركة",
                    "difficulty": 8,
                    "duration": 20,
                    "required_skills": ["تهدئة", "تفاوض", "حل مشكلات"],
                    "steps": 4
                },
                {
                    "name": "شكوى فيروسية",
                    "description": "شكوى عميل انتشرت على وسائل التواصل",
                    "difficulty": 9,
                    "duration": 35,
                    "required_skills": ["إدارة أزمات", "تواصل", "سرعة استجابة"],
                    "steps": 6
                }
            ]
        }
    
    async def generate_scenarios(self, specialization: str, level: str, course_topics: List[str]) -> List[Dict]:
        """
        توليد سيناريوهات مخصصة حسب التخصص والمستوى
        """
        templates = self.scenario_templates.get(specialization.value, [])
        scenarios = []
        
        # تعديل الصعوبة حسب المستوى
        level_factor = {
            'مبتدئ': 0.6,
            'متوسط': 0.8,
            'متقدم': 1.0,
            'خبير': 1.2,
            'معلم': 1.5
        }.get(level, 1.0)
        
        for template in random.sample(templates, min(3, len(templates))):
            # تخصيص السيناريو
            scenario = template.copy()
            
            # تعديل الصعوبة
            scenario['difficulty'] = min(10, int(template['difficulty'] * level_factor))
            
            # إضافة عناصر من مواضيع الدورة
            scenario['related_topics'] = random.sample(course_topics, min(2, len(course_topics)))
            
            # توليد خطوات تفصيلية
            scenario['steps'] = self.generate_steps(scenario)
            
            # إضافة وقت محاكاة
            scenario['simulation_time'] = datetime.now().isoformat()
            
            scenarios.append(scenario)
        
        self.generated_scenarios.extend(scenarios)
        return scenarios
    
    def generate_steps(self, scenario: Dict) -> List[Dict]:
        """توليد خطوات تفصيلية للسيناريو"""
        steps = []
        num_steps = scenario.get('steps', 4)
        
        for i in range(num_steps):
            step = {
                'step_number': i + 1,
                'description': f"الخطوة {i + 1}: {self.get_step_description(scenario, i)}",
                'expected_response': self.get_expected_response(scenario, i),
                'time_limit': scenario['duration'] // num_steps,
                'points': 100 // num_steps
            }
            steps.append(step)
        
        return steps
    
    def get_step_description(self, scenario: Dict, step_num: int) -> str:
        """وصف الخطوة حسب نوع السيناريو"""
        descriptions = {
            "هجوم تصيد مستهدف": [
                "استلام بريد إلكتروني مشبوه",
                "تحليل مرفقات البريد",
                "اكتشاف الرابط الخبيث",
                "الإبلاغ وعزل التهديد"
            ],
            "هجوم DDoS": [
                "ارتفاع مفاجئ في حركة المرور",
                "تحليل مصدر الهجوم",
                "تفعيل نظام الحماية",
                "تصفية الحركة الضارة",
                "استعادة الخدمة"
            ],
            "تأخير شحنات": [
                "استلام إنذار تأخير",
                "تحديد الشحنات المتأثرة",
                "إبلاغ العملاء",
                "إيجاد حلول بديلة",
                "تحديث الجدولة"
            ]
        }
        
        default = [
            "بداية الحدث",
            "تحليل الموقف",
            "اتخاذ إجراء",
            "إنهاء الموقف"
        ]
        
        steps = descriptions.get(scenario['name'], default)
        return steps[step_num] if step_num < len(steps) else default[step_num % len(default)]
    
    def get_expected_response(self, scenario: Dict, step_num: int) -> str:
        """الاستجابة المتوقعة في كل خطوة"""
        responses = {
            "هجوم تصيد": [
                "فحص البريد والتأكد من المصدر",
                "تشغيل برنامج مكافحة الفيروسات",
                "عزل الملفات المشبوهة",
                "تحديث قواعد الكشف"
            ],
            "هجوم DDoS": [
                "تفعيل نظام الإنذار المبكر",
                "تحديد نمط الهجوم",
                "توجيه الحركة لمرشحات",
                "التواصل مع مزود الخدمة",
                "تأكيد عودة الخدمة"
            ]
        }
        
        return responses.get(scenario['name'], ["الاستجابة المناسبة"])[step_num]
