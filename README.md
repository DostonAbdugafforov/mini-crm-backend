# Mini CRM — Backend (Django REST Framework)

Kichik CRM tizimi uchun backend API: lead (potentsial mijoz) larni boshqarish,
status bo'yicha kuzatish, activity tarixi va dashboard statistikasi.

## Tech stack

- **Backend:** Django 5 + Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **DB:** PostgreSQL (Docker/production), SQLite (local dev)
- **Filtering:** django-filter
- **API Docs:** drf-spectacular (Swagger UI)
- **CORS:** django-cors-headers

## Setup (local, SQLite)

\`\`\`bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# .env faylida SECRET_KEY ni real qiymat bilan to'ldiring

python manage.py migrate
python manage.py createsuperuser   # admin panel uchun (ixtiyoriy)
python manage.py runserver
\`\`\`

Server manzili: `http://127.0.0.1:8000/`

## Docker orqali ishga tushirish (PostgreSQL bilan)

\`\`\`bash
docker compose up --build
\`\`\`

Backend `http://localhost:8000/` da ishga tushadi, PostgreSQL konteynerda avtomatik ko'tariladi.

## API Docs (Swagger)

\`\`\`
http://localhost:8000/api-docs/
\`\`\`

Barcha endpointlar interaktiv tarzda shu yerda sinab ko'rilishi mumkin.

## Asosiy endpointlar

### Auth
\`\`\`
POST /api/v1/auth/register/   — ro'yxatdan o'tish
POST /api/v1/auth/login/      — login (access + refresh token)
POST /api/v1/auth/refresh/    — access tokenni yangilash
GET  /api/v1/auth/me/         — joriy foydalanuvchi ma'lumoti
\`\`\`

### Leads
\`\`\`
GET    /api/v1/leads/                  — ro'yxat (pagination, filter, search, ordering)
POST   /api/v1/leads/                  — yangi lead yaratish
GET    /api/v1/leads/{id}/             — bitta lead
PATCH  /api/v1/leads/{id}/             — leadni yangilash
DELETE /api/v1/leads/{id}/             — leadni o'chirish
PATCH  /api/v1/leads/{id}/status/      — status o'zgartirish (activity log bilan)
GET    /api/v1/leads/{id}/activity/    — lead tarixi
GET    /api/v1/dashboard/stats/        — umumiy statistika
\`\`\`

### Filter/search parametrlari (GET /api/v1/leads/)
\`\`\`
?status=WON
?source=WEBSITE
?search=Ali
?ordering=-created_at
?created_after=2026-01-01&created_before=2026-12-31
?page=1&limit=10
\`\`\`

## Javob formati

Muvaffaqiyatli:
\`\`\`json
{ "success": true, "data": { ... }, "meta": { "page": 1, "limit": 10, "total": 42, "totalPages": 5 } }
\`\`\`

Xato:
\`\`\`json
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "..." } }
\`\`\`

## Autentifikatsiya

Barcha `leads` va `dashboard` endpointlari JWT token talab qiladi:
\`\`\`
Authorization: Bearer <access_token>
\`\`\`

## Ma'lumot modeli

**Lead:** name, phone, email (kamida bittasi shart), source, status, note, owner, created_at, updated_at

**Status qiymatlari:** NEW, CONTACTED, QUALIFIED, WON, LOST
**Source qiymatlari:** WEBSITE, REFERRAL, ADS, COLD_CALL, OTHER

**LeadActivity:** har bir lead uchun avtomatik yoziladigan audit tarix (CREATED, UPDATED, STATUS_CHANGED, DELETED)

## Loyiha strukturasi

Qo'shimcha tafsilotlar uchun [ARCHITECTURE.md](./ARCHITECTURE.md) ga qarang.