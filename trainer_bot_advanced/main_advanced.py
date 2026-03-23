# main_advanced.py

import asyncio
import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.trainer_bot import TrainerBot, BotSpecialization, TrainingLevel

async def main():
    """
    تشغيل نظام التدريب المتقدم
    """
    print("=" * 70)
    print("           🤖 GTS Advanced Training Center")
    print("=" * 70)
    
    # إنشاء المدرب
    trainer = TrainerBot()
    
    # 1. تسجيل بوت الأمن للتدريب
    security_bot = await trainer.register_bot({
        'name': 'Security Guard Pro',
        'specialization': 'security',
        'version': '2.5',
        'level': 'متوسط'
    })
    
    # 2. تقييم قدراته
    assessment = await trainer.assess_bot_capabilities(security_bot.bot_id)
    print(f"\n📊 تقييم القدرات:")
    print(f"   النتيجة الكلية: {assessment['overall_score']}%")
    print(f"   نقاط القوة: {', '.join(assessment['strengths'])}")
    print(f"   نقاط الضعف: {', '.join(assessment['weaknesses'])}")
    
    # 3. إنشاء خطة تدريب
    training_plan = await trainer.create_training_plan(
        bot_id=security_bot.bot_id,
        goal="الوصول لمستوى خبير أمني خلال أسبوعين"
    )
    
    print(f"\n📋 خطة التدريب:")
    print(f"   المدة: {training_plan['duration_days']} أيام")
    print(f"   إجمالي الساعات: {training_plan['total_hours']} ساعة")
    print(f"\n   الدورات المقررة:")
    for course in training_plan['courses']:
        print(f"   • {course['name']} ({course['level']}) - {course['duration']} ساعات")
    
    # 4. بدء التدريب
    print(f"\n🎯 بدء تنفيذ الخطة...")
    plan_id = list(trainer.active_sessions.keys())[-1]
    results = await trainer.start_training(plan_id)
    
    # 5. عرض النتائج
    print("\n" + "=" * 70)
    print("📈 نتائج التدريب النهائية")
    print("=" * 70)
    
    print(f"\n🏆 النتيجة النهائية: {results['final_score']:.1f}%")
    
    print("\n📊 تفاصيل الدورات:")
    for course in results['courses_completed']:
        print(f"   • {course['course_name']}:")
        print(f"     - نظري: {course['theory_score']:.1f}%")
        print(f"     - عملي: {course['practical_score']:.1f}%")
        print(f"     - اختبار: {course['test_score']:.1f}%")
        print(f"     - النتيجة: {course['score']:.1f}%")
    
    if results['certificates']:
        cert = results['certificates'][0]
        print(f"\n🏅 الشهادة:")
        print(f"   رقم: {cert['certificate_id']}")
        print(f"   المستوى المحقق: {cert['level_achieved']}")
    
    # 6. إحصائيات المركز
    print("\n" + "=" * 70)
    print("📊 إحصائيات مركز التدريب")
    print("=" * 70)
    
    stats = trainer.training_stats
    print(f"\nإجمالي الجلسات: {stats['total_sessions']}")
    print(f"إجمالي ساعات التدريب: {stats['total_hours']}")
    print(f"نسبة النجاح: {stats['success_rate']}%")

if __name__ == "__main__":
    asyncio.run(main())
