"""
وحدة للتحليل الذكي باستخدام نموذج Gemini.
هذه الدالة منفصلة لضمان سهولة الصيانة والاستبدال بنموذج آخر لاحقًا.

الاستخدام:
    from gemini import analyze
    result = analyze(text)
"""

import requests

API_KEY = "AIzaSyCxHPp6zHCcWsUDLtHtGc2CTZP_zVJNzwg"


def analyze(text: str) -> str:
    """إرسال نص تقرير إلى Gemini والحصول على ملاحظات مختصرة.

    Args:
        text: نص التقرير المراد تحليله.

    Returns:
        سلسلة نصية تحتوي على تحليل النموذج، أو رسالة خطأ إذا لم يتوفر مفتاح أو حدث خطأ.
    """
    # تحقق من وجود مفتاح
    if not API_KEY:
        return " لم يتم وضع مفتاح Gemini"

    try:
        # إعداد الطلب للنموذج
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            f"?key={API_KEY}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "أنت مساعد تربوي. حلل التقرير التالي واكتب ملاحظات مختصرة "
                                "حول الطلاب المتغيبين وتوصيات للمعلم:\n" + text
                            )
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, json=payload)
        # عند النجاح إرجاع النص
        if response.ok:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        # عند عدم النجاح إرجاع رسالة خطأ
        return " فشل تحليل Gemini"
    except Exception as e:
        # عند حدوث استثناء إرجاع الخطأ
        return f" حدث خطأ في الاتصال بـ Gemini: {e}"