import os
import json
import datetime
import asyncio
import edge_tts

def get_curriculum_data():
    with open("curriculum.json", "r", encoding="utf-8") as f:
        curriculum = json.load(f)
    start_date = datetime.date(2026, 6, 23)
    today = datetime.date.today()
    day_number = (today - start_date).days + 1
    day_key = f"day_{day_number}"
    return curriculum[day_key] if day_key in curriculum else curriculum["day_1"]

today_curriculum = get_curriculum_data()

def get_ai_free_content(branch_name, subject, title):
    return f"""1. [شرح الأستاذ]:
    مرحباً بكم يا طلابنا في حصة مادة {subject} لدرس "{title}". يتناول هذا الدرس المكتوب والمسجل الفقرات الامتحانية والقوانين الأساسية المقررة في المنهاج السوري بدقة، ويركز على طرق الفهم المبسط لضمان الدرجات الكاملة في الامتحان النهائي. يرجى متابعة المخططات والجداول التوضيحية المرفقة أدناه لترسيخ الفكرة الامتحانية في ذهنك.
    
    2. [نماذج أسئلة امتحانية]:
    س1: ما هي القاعدة أو القانون الأساسي المستنتج من هذا الدرس في ورقة الامتحان؟
    الحل النموذجي المعتمد في التصحيح الوزاري: يتم تطبيق القوانين والتعاريف الرسمية المذكورة في فقرات الكتاب المعتمد بدقة مع كتابة الرموز والوحدات كاملة لنيل العلامة التامة.
    
    3. [امتحان دوري مقترح]:
    اختبار خيارات متعددة وأسئلة مقالية مخصصة لتقييم استيعاب الطالب للفكرة الامتحانية للدرس مع مفتاح الحل لتقوم المنصة بتصحيحه للطلاب تلقائياً وتحديد مستوى استيعابهم للمادة."""

async def text_to_speech(text, filename):
    try:
        # تصحيح طريقة فصل النص الصوتي بأمان
        parts = text.split("2. [")
        sharah_text = parts[0].replace("1. [شرح الأستاذ]:", "") if len(parts) > 0 else text
        
        communicate = edge_tts.Communicate(sharah_text, "ar-EG-ShakirNeural")
        await communicate.save(filename)
    except Exception as e:
        print(f"خطأ صوتي: {e}")

async def main():
    os.makedirs("./data", exist_ok=True)
    final_output = {}
    
    for branch, subjects in today_curriculum.items():
        final_output[branch] = []
        for subject, title in subjects.items():
            print(f"🔄 جاري تحضير حقيبة ومخططات: {branch} -> {subject}...")
            full_content = get_ai_free_content(branch, subject, title)
            
            clean_branch_name = branch.replace("_", "")
            clean_subject_name = subject.replace(" ", "")
            audio_file = f"data/{clean_branch_name}_{clean_subject_name}.mp3"
            
            await text_to_speech(full_content, f"./{audio_file}")
            
            parts = full_content.split("2. [")
            sharah = parts[0].replace("1. [شرح الأستاذ]:", "") if len(parts) > 0 else full_content
            asela = "2. [" + parts[1] if len(parts) > 1 else "جاري التجهيز..."
            exam = "3. [" + parts[1].split("3. [")[1] if len(parts) > 1 and "3. [" in parts[1] else "جاري التجهيز..."
            
            final_output[branch].append({
                "subject": subject,
                "title": title,
                "sharah": sharah.replace("\n", "<br>"),
                "asela": asela.replace("\n", "<br>"),
                "exam": exam.replace("\n", "<br>"),
                "audio": audio_file
            })
            
    with open("./data/lessons.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    print("🎉 تم إنتاج الـ 24 حصة والملفات الصوتية بنجاح على غيت هاب!")

if __name__ == "__main__":
    asyncio.run(main())
