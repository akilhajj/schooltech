import os
import json
import datetime
import asyncio
import edge_tts
from openai import OpenAI

OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

# إعداد الاتصال بالمسار البرمجي السحابي المحدث لـ Ollama
client = OpenAI(
    base_url="https://ollama.com",
    api_key=OLLAMA_API_KEY
)

# دالة ذكية لقرائة جدول المناهج أوتوماتيكياً حسب اليوم الحالي
def get_curriculum_data():
    with open("curriculum.json", "r", encoding="utf-8") as f:
        curriculum = json.load(f)
    start_date = datetime.date(2026, 6, 23)
    today = datetime.date.today()
    day_number = (today - start_date).days + 1
    day_key = f"day_{day_number}"
    return curriculum[day_key] if day_key in curriculum else curriculum["day_1"]

today_curriculum = get_curriculum_data()

def get_ai_content(branch_name, subject, title):
    prompt = f"""
    أنت موجه تربوي وخبير في المنهاج السوري لمرحلة ({branch_name}). اكتب محتوى تعليمي متكامل لمادة {subject} درس: {title}.
    يجب أن تقسم المحتوى بدقة إلى الأقسام التالية وبشكل واضح:

    1. [شرح الأستاذ]: شرح مبسط وسردي جداً وفقرات واضحة وممتعة للفقرة الأساسية من الدرس (مناسب للقراءة الصوتية).
    ملاحظة بصرية هامة: إذا كان الدرس علمياً، أو يحتوي على مقارنات، أو معادلات وقوانين، استخدم الجداول النصية المنسقة (Markdown Tables) والمخططات السهمية الرمزية لتبسيط الفكرة بصرياً للطالب داخل الشرح هنا.
    
    2. [نماذج أسئلة امتحانية]: اذكر أهم 3 أسئلة متوقعة وكيف تأتي في الامتحان النهائي حول هذا الدرس مع طريقة حلها النموذجية لتضمن للطلاب العلامة التامة.
    
    3. [امتحان دوري مقترح]: وضع اختباراً دورياً قصيراً لهذا الدرس يتكون من (سؤالين اختيار من متعدد، وسؤال مقالي أو مسألة) مع مفتاح الحل لتقوم المنصة الأساسية بتصحيحه للطلاب.
    """
    try:
        response = client.chat.completions.create(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response.choices.message.content
    except Exception as e:
        return f"خطأ في توليد المحتوى: {e}"

async def text_to_speech(text, filename):
    try:
        sharah_text = text.split("2. [نماذج أسئلة امتحانية]")[0].replace("1. [شرح الأستاذ]:", "")
        communicate = edge_tts.Communicate(sharah_text, "ar-EG-ShakirNeural")
        await communicate.save(filename)
    except Exception as e:
        print(f"خطأ في توليد الصوت: {e}")

# تصحيح السطر المفقود بإضافة كلمة def وتحديد المسار النسبي الصحيح لـ data
async def main():
    os.makedirs("./data", exist_ok=True)
    final_output = {}
    
    for branch, subjects in today_curriculum.items():
        final_output[branch] = []
        for subject, title in subjects.items():
            print(f"🔄 جاري تحضير حقيبة ومخططات: {branch} -> {subject}...")
            full_content = get_ai_content(branch, subject, title)
            
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
    print("🎉 تم إنتاج الحصص بالمخططات البصرية والملفات الصوتية بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
