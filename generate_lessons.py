import os
import json
import asyncio
import edge_tts
from openai import OpenAI

# جلب المفتاح السري تلقائياً من إعدادات غيت هاب الآمنة
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

# إعداد الاتصال بالخادم السحابي لـ Ollama
client = OpenAI(
    base_url="https://ollama.com",
    api_key=OLLAMA_API_KEY
)


# جدول المناهج لليوم (7 مواد أساسية لصف التاسع كمثال)
today_lessons = {
    "اللغة العربية": "المفعول المطلق - الصف التاسع",
    "الرياضيات": "حل معادلة من الدرجة الثانية - التاسع",
    "الفيزياء": "الحركة والسكون - التاسع",
    "الكيمياء": "الروابط الكيميائية - التاسع",
    "علم الأحياء": "الخلية وبنيتها - التاسع",
    "اللغة الإنجليزية": "Present Perfect Tense - التاسع",
    "الدراسات الاجتماعية": "الحضارات القديمة في سوريا - التاسع"
}

def get_ai_text(subject, title):
    prompt = f"""
    أنت معلم محترف في المنهاج السوري. اكتب درس تعليمي مبسط وموجه للطلاب في مادة {subject} لدرس: {title}.
    يجب أن يتضمن الشرح:
    1. مقدمة ترحيبية مشوقة من المعلم الافتراضي للمنصة.
    2. الشرح العلمي المبسط في نقاط واضحة وقصيرة جداً.
    3. خاتمة تشجيعية سريعة.
    ملاحظة: اكتب النص بشكل سردي ليكون مناسباً جداً للقراءة الصوتية وبدون رموز معقدة.
    """
    try:
        # استخدام نموذج Llama 3 المدعوم سحابياً من Ollama
        response = client.chat.completions.create(
            model="llama3", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices.message.content
    except Exception as e:
        print(f"خطأ في توليد النص لمادة {subject}: {e}")
        return f"مرحباً بكم في درس {title}. يرجى مراجعة فقرات الكتاب الرسمية لهذه المادة."

async def text_to_speech(text, filename):
    try:
        # تحويل النص إلى صوت عربي بشري طبيعي بالكامل مجاناً
        communicate = edge_tts.Communicate(text, "ar-EG-ShakirNeural")
        await communicate.save(filename)
    except Exception as e:
        print(f"خطأ في توليد الصوت: {e}")

async main():
    # إنشاء مجلد لحفظ الحصص اليومية (الملفات الصوتية والبيانات)
    os.makedirs("data", exist_ok=True)
    lessons_data = []
    
    for subject, title in today_lessons.items():
        print(f"🔄 جاري إنتاج حصة: {subject}...")
        
        text = get_ai_text(subject, title)
        audio_file = f"data/{subject}.mp3"
        
        # توليد الصوت وحفظه
        await text_to_speech(text, audio_file)
        
        # تجهيز البيانات لواجهة الموقع وتحويل السطور البرمجية لـ HTML
        lessons_data.append({
            "subject": subject,
            "title": title,
            "content": text.replace("\n", "<br>"),
            "audio": audio_file
        })
        
    # حفظ كل الحصص في ملف json ذكي لتقرأه واجهة الموقع فوراً
    with open("data/lessons.json", "w", encoding="utf-8") as f:
        json.dump(lessons_data, f, ensure_ascii=False, indent=4)
    print("🎉 تم تحديث بيانات الحصص الـ 7 بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
