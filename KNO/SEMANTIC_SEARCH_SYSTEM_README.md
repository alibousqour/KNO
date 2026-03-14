# KNO Advanced Semantic Search System
# ====================================

## 📋 نظام البحث الدلالي المتقدم لـ KNO

### ✨ الميزات الأساسية

#### 1. البحث بالمعنى (Semantic Search)
- البحث عن الملفات بناءً على **المعنى** وليس فقط الكلمات المفتاحية
- استخدام نماذج التعلم العميق (Sentence Transformers) لفهم السياق
- دعم استعلامات طبيعية بصيغ متعددة

**أمثلة:**
```python
# بدلاً من البحث عن الكلمة "user"
# البحث يفهم الاستعلام الكامل
await search.search_files("كيفية توثيق المستخدمين؟")
# يجد ملفات عن Authentication, Login, Security حتى لو لم تحتوي على كلمة "user"
```

#### 2. تكامل eDEX-UI (Edge of eXecution Interface)
- شريط تقدم حي في الواجهة السينمائية
- تحديث تلقائي أثناء الفهرسة والبحث
- ألوان ديناميكية بناءً على النسبة المئوية
- عرض اسم الملف الحالي والوقت المنقضي

**ملف الحالة:** `edex_status.json`
```json
{
  "version": "3.0",
  "progress": {
    "operation": "searching",
    "current": 75,
    "total": 100,
    "percentage": 75.0,
    "status": "📊 Processing 5 results...",
    "elapsed_seconds": 2.34
  },
  "ui_elements": {
    "progress_bar": {
      "visible": true,
      "percentage": 75.0,
      "color": "#FFD700",
      "animated": true
    }
  }
}
```

---

### 🏗️ بنية النظام

```
Semantic Search System
├── semantic_search_advanced.py          [المحرك الأساسي]
│   ├── FileAnalyzer                     [تحليل الملفات]
│   ├── EDEXStatusManager                [إدارة شريط التقدم]
│   ├── SemanticSearchEngine             [محرك البحث]
│   └── KNOSemanticSearch                [الواجهة الرئيسية]
│
├── agent_semantic_search_integration.py [التكامل مع الوكيل]
│   ├── KNOAgentSemanticSearch           [واجهة الوكيل]
│   ├── EDEXCommandHandler               [معالج أوامر eDEX]
│   └── search_files()                   [دالة سريعة]
│
├── SEMANTIC_SEARCH_GUIDE.md             [الدليل الشامل]
├── test_semantic_search_advanced.py     [ملف الاختبار]
└── requirements-semantic-search.txt     [المتطلبات]
```

---

### 🚀 الاستخدام السريع

#### التثبيت
```bash
pip install -r requirements-semantic-search.txt
```

#### مثال بسيط
```python
import asyncio
from agent_semantic_search_integration import search_files

async def main():
    # البحث البسيط
    results = await search_files(
        "user authentication",
        directory="./KNO",
        max_results=10
    )
    
    for result in results:
        print(f"{result['file_path']}: {result['relevance_score']}%")

asyncio.run(main())
```

#### مثال متقدم
```python
import asyncio
from agent_semantic_search_integration import KNOAgentSemanticSearch

async def main():
    # إعداد النظام
    search = KNOAgentSemanticSearch(
        base_directory="./KNO",
        status_file="edex_status.json"
    )
    
    # تهيئة النماذج
    await search.initialize()
    
    # فهرسة المجلد (مع شريط تقدم في eDEX)
    await search.index_directory()
    
    # البحث المتكرر (محسّن بالتخزين المؤقت)
    results = await search.search_files("database operations", max_results=5)
    
    # الحصول على الإحصائيات
    metrics = search.get_metrics()
    print(f"Indexed: {metrics['indexed_files']} files")

asyncio.run(main())
```

---

### 📊 الميزات المتقدمة

#### 1. تخزين النتائج مؤقتاً
```python
# البحث الأول - قد يكون أبطأ
results1 = await search.search_files("authentication")

# البحث الثاني - سريع جداً (من الذاكرة المؤقتة)
results2 = await search.search_files("authentication")

# مسح الذاكرة المؤقتة
search.clear_cache()
```

#### 2. الحصول على نتائج مفصلة
```python
details = await search.search_with_details("database")

print(f"Query: {details['query']}")
print(f"Results: {details['result_count']}")
print(f"Metrics: {details['metrics']}")
```

#### 3. معالج أوامر eDEX
```python
from agent_semantic_search_integration import EDEXCommandHandler

handler = EDEXCommandHandler()

# من واجهة eDEX-UI
result = await handler.handle_search_command("websocket communication")
result = await handler.handle_index_command("./src")
```

---

### 📁 أنواع الملفات المدعومة

✓ **Python** (.py)
✓ **JavaScript/TypeScript** (.js, .ts)
✓ **Java** (.java)
✓ **C#** (.cs)
✓ **C++** (.cpp, .h)
✓ **JSON** (.json)
✓ **YAML** (.yml, .yaml)
✓ **XML** (.xml)
✓ **Markdown** (.md)
✓ **Text** (.txt)

**المجلدات المتجاهلة:**
- `__pycache__`, `node_modules`, `.git`, `dist`, `build`, `venv`

---

### 🔍 أمثلة الاستعلامات

#### استعلامات موجهة بالأسئلة
```
"كيفية التوثيق بكلمة مرور؟"
"أين يتم معالجة الأخطاء؟"
"ما الدوال التي تتعامل مع قاعدة البيانات؟"
```

#### استعلامات موجهة بالميزات
```
"تنفيذ توثيق المستخدم"
"إدارة اتصال قاعدة البيانات"
"تعريفات نقطة نهاية API"
```

#### استعلامات موجهة بالتكنولوجيا
```
"اتصالات WebSocket في الوقت الفعلي"
"تحليل وتحويل JSON"
"أنماط Async/Await"
```

---

### 📈 الأداء والتحسين

#### نصائح الأداء
1. **فهرسة واحدة، بحث متكرر**
   ```python
   await search.index_directory()  # مرة واحدة
   await search.search_files(query1)  # بحث متكرر سريع
   await search.search_files(query2)
   ```

2. **تحديد حد الحد الأقصى للنتائج**
   ```python
   # أفضل
   results = await search.search_files(query, max_results=10)
   
   # كثيف الموارد
   results = await search.search_files(query, max_results=1000)
   ```

3. **الاستفادة من التخزين المؤقت**
   - البحث عن نفس الاستعلام يُرجع النتائج من الذاكرة المؤقتة فوراً
   - مسح الذاكرة المؤقتة عند الحاجة فقط

#### متطلبات الموارد
- **ذاكرة RAM:** 4 GB الحد الأدنى، 8 GB موصى به
- **مساحة التخزين:** > 500 MB لتنزيل النموذج
- **معالج:** یُفضل معالج متعدد النوى

---

### 🔧 التكامل مع KNO Agent

```python
# في agent.py
async def on_search_command(query: str):
    from agent_semantic_search_integration import KNOAgentSemanticSearch
    
    search = KNOAgentSemanticSearch()
    if not search.search_system.initialized:
        await search.initialize()
    
    results = await search.search_files(query, max_results=10)
    return results

# الاستخدام
results = asyncio.run(on_search_command("user authentication"))
```

---

### 📋 مجموعات البيانات المرجعية

#### نتيجة بحث واحدة
```python
{
    'file_path': '/path/to/file.py',
    'file_type': 'python',
    'relevance_score': 87.5,          # 0-100
    'matched_content': 'def authenticate(user):',
    'line_numbers': [45],
    'keywords': ['authenticate', 'user', 'token'],
    'summary': 'def authenticate(user):'
}
```

#### إحصائيات الفهرسة
```python
{
    'total_files': 150,
    'indexed_files': 145,
    'failed_files': 5,
    'total_chunks': 3042,
    'indexing_time_seconds': 23.45,
    'average_chunk_size': 512,
    'last_indexing_date': '2026-03-09T10:30:45.123456'
}
```

---

### 🧪 الاختبار

#### تشغيل جميع الاختبارات
```bash
python test_semantic_search_advanced.py
```

#### تشغيل عرض توضيحي سريع
```bash
python test_semantic_search_advanced.py --quick
```

---

### 📝 الملفات الرئيسية

| الملف | الوصف |
|------|--------|
| `semantic_search_advanced.py` | محرك البحث الأساسي والمكونات |
| `agent_semantic_search_integration.py` | تكامل وكيل KNO |
| `SEMANTIC_SEARCH_GUIDE.md` | دليل شامل بصيغة Markdown |
| `test_semantic_search_advanced.py` | مجموعة اختبار شاملة |
| `requirements-semantic-search.txt` | المتطلبات والحزم |

---

### 🔐 الأمان والملاحظات

#### ملاحظات أمان
- النظام يقرأ الملفات من نظام الملفات المحلي فقط
- لا تُرسل البيانات إلى الإنترنت (كل شيء محلي)
- الملفات الحساسة يمكن استبعادها من الفهرسة

#### ملاحظات الخصوصية
- لا يوجد تتبع أو جمع بيانات
- جميع البيانات تُبقى محلياً
- كل عملية بحث مسجلة في `semantic_search.log`

---

### 🚨 استكشاف الأخطاء

#### السؤال: "لا توجد ملفات مفهرسة"
**الحل:**
```python
await search.initialize()
await search.index_directory()
```

#### السؤال: نتائج البحث فارغة
**الحل:** حاول صيغة استعلام مختلفة:
```python
# بدلاً من
search.search_files("user")

# جرب
search.search_files("user authentication and login")
```

#### السؤال: استهلاك ذاكرة عالي
**الحل:**
```python
# قلل النتائج
results = await search.search_files(query, max_results=5)

# امسح الذاكرة المؤقتة
search.clear_cache()
```

---

### 📚 الموارد الإضافية

- **الدليل الشامل**: [SEMANTIC_SEARCH_GUIDE.md](SEMANTIC_SEARCH_GUIDE.md)
- **الملف الرئيسي**: [semantic_search_advanced.py](semantic_search_advanced.py)
- **التكامل**: [agent_semantic_search_integration.py](agent_semantic_search_integration.py)
- **السجلات**: `semantic_search.log`

---

### ✅ ملخص الميزات

#### المُنجز ✨
- ✅ محرك بحث دلالي كامل
- ✅ دعم استعلامات طبيعية متقدمة
- ✅ تكامل eDEX-UI مع شريط تقدم
- ✅ تخزين مؤقت فعال للنتائج
- ✅ تحليل ملفات متعدد النوع
- ✅ تسجيل شامل
- ✅ معالجة أخطاء قوية
- ✅ مجموعة اختبار شاملة

#### الاستخدام الموصى به
- فهرسة المشاريع الكبيرة (آلاف الملفات)
- البحث عن الوظائف والمكونات في قاعدة الكود
- العثور على نمط الكود المشابه
- توثيق البحث والاكتشاف
- تحليل البنية المعمارية

---

## 🎯 الخطوات التالية

1. **التثبيت**: `pip install -r requirements-semantic-search.txt`
2. **الاختبار**: `python test_semantic_search_advanced.py`
3. **التكامل**: أضف إلى `agent.py` سطراً واحداً للبحث
4. **الاستخدام**: ابدأ بالبحث عن الملفات بالمعنى

---

**تم الإنشاء:** 2026-03-09  
**الإصدار:** 1.0.0  
**المرخص:** MIT License  
**المؤلف:** KNO Architecture  

---

**Happy Semantic Searching! 🔍**
