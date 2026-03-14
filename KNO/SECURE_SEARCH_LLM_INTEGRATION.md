# نظام البحث الدلالي الآمن مع تكامل LLMCoordinator
# Secure Semantic Search System with LLMCoordinator Integration
# ============================================================================

## 📋 نظرة عامة / Overview

هذا النظام يوفر **بحث دلالي آمن** في ملفات KNO مع:
- ✅ تصفية الملفات الحساسة (مفاتيح مشفرة، ملفات .env، إلخ)
- ✅ تكامل كامل مع LLMCoordinator كـ Function Calling
- ✅ تدقيق أمني شامل مع تتبع الملفات المحظورة
- ✅ دعم Pydantic للأمان الموجه للأنواع (Type Safety)

---

## 🏗️ البنية المعمارية / Architecture

```
┌─────────────────────────────────────────────────────┐
│           LLM / User Query                          │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │ LLMCoordinator     │
        │ (Function Caller)  │
        └─────────┬──────────┘
                  │
    ┌─────────────▼───────────────────┐
    │ llm_coordinator_secure.py       │
    │ - SemanticSearchTool            │
    │ - Function Schema               │
    │ - Pydantic Models               │
    └─────────────┬───────────────────┘
                  │
    ┌─────────────▼───────────────────┐
    │ secure_semantic_search.py       │
    │ - SecureSemanticSearchEngine    │
    │ - Security Audit Trail          │
    │ - File Verification             │
    └─────────────┬───────────────────┘
                  │
    ┌─────────────┼───────────────────┐
    │             │                   │
┌───▼────────┐ ┌─▼──────────────┐ ┌──▼─────────┐
│ Security   │ │ File Analyzer  │ │ Search     │
│ Filter     │ │                │ │ Engine     │
├────────────┤ ├────────────────┤ ├────────────┤
│- Ignore    │ │- Type detect   │ │- Embeddin  │
│  Lists     │ │- Content read  │ │  gs        │
│- Patterns  │ │- Summary       │ │- Vector DB │
└────────────┘ └────────────────┘ └────────────┘
```

---

## 📁 الملفات الجديدة / New Files

### 1. **secure_semantic_search.py** (المحرك الآمن)
```python
# الفئات الرئيسية:
- SecureFileAnalyzerEnhanced      # محلل ملفات آمن
- SecureSemanticSearchEngine       # محرك البحث الآمن
- SecureKNOSemanticSearch          # النظام المتكامل
```

**الميزات:**
- ✅ تكامل SecurityFilter من security_filter.py
- ✅ تدقيق أمني شامل (audit trail)
- ✅ تصفية الملفات المحظورة
- ✅ دعم verbose security logging

### 2. **llm_coordinator_secure.py** (تكامل LLM)
```python
# Pydantic Models (Type Safety):
- SearchQuery                      # نموذج استعلام البحث
- SearchResultModel                # نموذج النتيجة
- SearchResponse                   # نموذج الاستجابة

# Function Calling:
- SemanticSearchTool               # أداة البحث
- SemanticSearchLLMIntegration    # منسق التكامل
```

**الميزات:**
- ✅ مخطط OpenAI compatible function calling
- ✅ التحقق من صحة المدخلات باستخدام Pydantic
- ✅ معالجة الأخطاء مع re-tries
- ✅ تنسيق النتائج للاستجابة السريعة للـ LLM

### 3. **ignore_list.json** (قائمة التجاهل)
```json
{
  "ignore_list": {
    "system_files": [".git", ".github", "__pycache__", ...],
    "encrypted_keys": ["*.key", "*.pem", "private_key", ...],
    "credentials": [".aws/credentials", "secrets.json", ...],
    "build_artifacts": ["build/", "dist/", ...],
    "cache_files": [".cache/", ".pytest_cache/", ...]
  },
  "sensitivity_levels": {
    "restricted": [...],
    "sensitive": [...],
    "internal": [...]
  },
  "allowed_extensions": [".py", ".js", ".json", ...],
  "scan_limits": { ... }
}
```

**المستويات الأمنية:**
- 🔴 **restricted**: محظور تماماً (مفاتيح مشفرة، بيانات اعتماد)
- 🟠 **sensitive**: يحتاج موافقة (ملفات DB، ملفات AWS)
- 🟡 **internal**: ملفات داخلية (cache، build)

---

## 🚀 البدء السريع / Quick Start

### التثبيت
```bash
pip install -r requirements-semantic-search.txt
pip install pydantic  # للتحقق من صحة الأنواع
```

### 1️⃣ استخدام البحث الآمن البسيط

```python
import asyncio
from secure_semantic_search import SecureKNOSemanticSearch

async def main():
    # إنشاء النظام
    search = SecureKNOSemanticSearch(
        base_directory="./KNO",
        model_name="all-MiniLM-L6-v2"
    )
    
    # تهيئة
    await search.initialize()
    
    # فهرسة آمنة
    await search.index_directory(verbose=True)
    
    # البحث
    results = await search.search(
        query="authentication user",
        max_results=5
    )
    
    # الحصول على تقرير الأمان
    report = search.search_engine.get_security_status()
    print(f"Files blocked: {report['audit']['restricted_files_blocked']}")

asyncio.run(main())
```

### 2️⃣ استخدام LLM Coordinator

```python
from llm_coordinator_secure import SemanticSearchLLMIntegration
from secure_semantic_search import SecureKNOSemanticSearch

async def setup_llm_tool():
    # إعداد المحرك الآمن
    search = SecureKNOSemanticSearch()
    await search.initialize()
    
    # إنشاء تكامل LLM
    integration = SemanticSearchLLMIntegration(
        search_engine=search.search_engine,
        ignore_manager=search.ignore_manager
    )
    
    # الحصول على مخطط الدالة
    tools = integration.get_available_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")
    
    return integration
```

### 3️⃣ استدعاء من LLM

```python
# يقوم LLM بإنشاء استدعاء دالة:
llm_call = {
    "name": "semantic_search",
    "arguments": {
        "query": "كيفية معالجة الخطأ",
        "max_results": 5,
        "min_relevance": 0.4,
        "scope": "entire_system",
        "include_restricted": False
    }
}

# معالجة الاستدعاء:
result = await integration.process_llm_call(
    llm_call["name"],
    llm_call["arguments"]
)

print(result)
# {
#   "success": True,
#   "query": "كيفية معالجة الخطأ",
#   "total_results": 3,
#   "results": [
#     {
#       "file_path": "agent.py",
#       "relevance_score": 0.89,
#       ...
#     }
#   ]
# }
```

---

## 🔐 الأمان / Security

### 📋 قائمة التجاهل الحالية

**مستوى Restricted (🔴):**
```
- .git/               → مثل التحكم بالإصدار
- .env*               → متغيرات البيئة
- *.key, *.pem        → مفاتيح التشفير
- private_key         → المفاتيح الخاصة
- secrets.json        → أسرار التطبيق
- api_key, token      → بيانات اعتماد API
```

**مستوى Sensitive (🟠):**
```
- .aws/credentials    → مفاتيح AWS
- database_files      → ملفات قواعد البيانات
- config_secrets.yaml → إعدادات سرية
```

**مستوى Internal (🟡):**
```
- __pycache__/        → ملفات Python مجمعة
- build/, dist/       → مواد البناء
- .cache/             → ملفات مؤقتة
- node_modules/       → مكتبات npm
```

### 🎯 كيفية تخصيص القائمة

**خيار 1: تحرير ignore_list.json**
```json
{
  "ignore_list": {
    "my_custom_patterns": [
      "confidential/",
      "*.secret",
      "internal_api/*"
    ]
  }
}
```

**خيار 2: البرمجة**
```python
from security_filter import IgnoreListManager

manager = IgnoreListManager("./KNO")

# إضافة أنماط مخصصة
manager.add_pattern(
    pattern="my_project/secrets/*",
    sensitivity="restricted"
)

# حفظ
manager.save_config()
```

### 🔍 التدقيق / Auditing

```python
# الحصول على تقرير التدقيق
audit = search_engine.get_security_audit()

print(f"""
Audit Report:
- Total scanned: {audit['total_files_scanned']}
- Files filtered: {audit['files_filtered']}
- Restricted blocked: {audit['restricted_files_blocked']}
- Suspicious patterns: {len(audit['suspicious_patterns'])}
""")
```

---

## 🔧 التكامل مع LLMCoordinator

### الخطوة 1: إنشاء الأداة
```python
from llm_coordinator_secure import SemanticSearchLLMIntegration

integration = SemanticSearchLLMIntegration(
    search_engine=my_search_engine,
    ignore_manager=my_ignore_manager
)
```

### الخطوة 2: تسجيل مع منسق LLM
```python
# في LLMCoordinator:
coordinator.register_tool(
    name="semantic_search",
    schema=integration.get_available_tools()[0],
    executor=integration.process_llm_call
)
```

### الخطوة 3: استدعاء من الاستعلام الطبيعي
```
المستخدم: "ابحث عن ملفات معالجة الخطأ"
↓
LLM: "استخدم semantic_search tool" 
↓
LLMCoordinator: يستدعي integration.process_llm_call()
↓
النتائج: ملفات ذات صلة بمعالجة الخطأ
```

---

## 📊 مثال تفاعلي / Interactive Example

```python
import asyncio
from secure_semantic_search import SecureKNOSemanticSearch
from llm_coordinator_secure import SemanticSearchLLMIntegration

async def demo():
    print("🔒 Secure Semantic Search Demo")
    print("=" * 50)
    
    # 1. إنشاء النظام
    search = SecureKNOSemanticSearch(base_directory="./KNO")
    print("\n✅ System created")
    
    # 2. التهيئة
    await search.initialize()
    print("✅ Initialized")
    
    # 3. الفهرسة
    print("\n📁 Indexing...")
    await search.index_directory(verbose=True)
    
    # 4. إعداد LLM
    integration = SemanticSearchLLMIntegration(
        search_engine=search.search_engine,
        ignore_manager=search.ignore_manager
    )
    print("\n🔧 LLM Integration ready")
    
    # 5. البحث عبر LLM
    llm_args = {
        "query": "user authentication login",
        "max_results": 5,
        "min_relevance": 0.4
    }
    
    print(f"\n🔍 Searching: {llm_args['query']}")
    result = await integration.tool.execute(**llm_args)
    
    # 6. عرض النتائج
    print(f"\n📊 Found {result['total_results']} files")
    for r in result['results'][:3]:
        print(f"   - {r['file_path']} ({int(r['relevance_score']*100)}%)")
    
    # 7. تقرير الأمان
    report = search.get_security_report()
    print(f"\n🔐 Security Report")
    print(f"   - Total ignore rules: {report['ignore_rules']['total_rules']}")
    print(f"   - Files blocked: {report['security_audit']['restricted_files_blocked']}")

asyncio.run(demo())
```

---

## 📈 المقاييس والأداء / Metrics

### Pydantic Validation

```python
from llm_coordinator_secure import SearchQuery

# هذا سيفشل - query فارغة
try:
    SearchQuery(query="")
except ValueError as e:
    print(f"❌ Validation failed: {e}")

# هذا سيفشل - max_results خارج النطاق
try:
    SearchQuery(query="test", max_results=100)
except ValueError as e:
    print(f"❌ Validation failed: {e}")

# هذا سينجح
query = SearchQuery(
    query="authentication",
    max_results=10,
    min_relevance=0.5
)
print(f"✅ Valid query: {query.dict()}")
```

### Security Metrics

```python
# تتبع الملفات المحظورة
audit = search_engine.get_security_audit()

blocked_percentage = (
    audit['restricted_files_blocked'] / audit['total_files_scanned']
) * 100

print(f"""
Security Metrics:
- Files Scanned: {audit['total_files_scanned']}
- Files Filtered: {audit['files_filtered']}
- Restricted Blocked: {audit['restricted_files_blocked']}
- Block Rate: {blocked_percentage:.1f}%
""")
```

---

## 🐛 استكشاف الأخطاء / Troubleshooting

### المشكلة: "Pydantic not available"
**الحل:**
```bash
pip install pydantic
```

### المشكلة: "Base engine not initialized"
**الحل:**
```python
await search.initialize()  # قبل البحث
```

### المشكلة: "File marked as restricted"
**الحل:** تحقق من ignore_list.json
```python
report = search.get_security_report()
print(report['ignore_rules'])
```

---

## 📚 المراجع / References

- `semantic_search_advanced.py` - المحرك الأساسي
- `security_filter.py` - نظام الأمان
- `llm_coordinator_secure.py` - تكامل LLM
- `ignore_list.json` - قائمة التجاهل

---

## ✅ قائمة التحقق / Checklist

- [ ] تثبيت المتطلبات
- [ ] إنشاء النظام
- [ ] فهرسة الدليل
- [ ] اختبار البحث الأساسي
- [ ] إعداد LLM Coordinator
- [ ] اختبار استدعاء الدالة
- [ ] مراجعة تقرير الأمان
- [ ] تخصيص ignore_list.json (إن لزم)

---

**نسخة آمنة محسنة | Enhanced Secure Version**
**الإصدار: 2.0 | Version: 2.0**
**التاريخ: 2025 | Date: 2025**
