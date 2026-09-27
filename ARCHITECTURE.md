# Architecture

## Nega Django REST Framework

Admin panel, ORM, migration tizimi va auth infratuzilmasi tayyor holda
keladi — CRUD-og'ir loyihada boilerplate kamayadi. ViewSet + Router
kombinatsiyasi standart REST amallarni (list/create/retrieve/update/delete)
juda kam kod bilan beradi, shu bilan birga `@action` orqali status change
kabi maxsus business-action'larni ham toza qo'shish mumkin.

## Loyiha strukturasi

Har bir Django app o'z domenini boshqaradi:
- `accounts` — foydalanuvchi autentifikatsiyasi (register/login/refresh/me)
- `leads` — CRM'ning asosiy biznes logikasi (Lead, LeadActivity, filtering, dashboard)

Bu ajratish domenlar orasidagi bog'liqlikni kamaytiradi va loyihani
kengaytirishni osonlashtiradi (masalan kelajakda `companies` yoki
`notifications` app qo'shish oson bo'ladi).

## Nega status alohida endpoint

`PATCH /leads/{id}/status/` ni oddiy `PATCH /leads/{id}/` dan ajratdim,
chunki bu funnel harakati va har safar `LeadActivity` ga log yoziladi —
CRM'ning eng muhim business logikasi shu yerda. Status uchun alohida
`LeadStatusUpdateSerializer` ishlatiladi, shunda noto'g'ri status qiymati
darhol 400 bilan rad etiladi, boshqa maydonlar bilan aralashmaydi.

## Validation

Validatsiya ikki darajada amalga oshirilgan:
1. **Serializer darajasida** (`validate()`) — API orqali kirgan ma'lumot
   uchun, phone yoki email kamida bittasi talab qilinadi.
2. **Model darajasida** (`clean()` + `save()` ichida `full_clean()`) —
   API orqali emas, admin panel yoki boshqa yo'l bilan (masalan Django
   shell orqali to'g'ridan-to'g'ri `Lead.objects.create(...)`) ham
   noto'g'ri ma'lumot kira olmasligi uchun qo'shimcha himoya qatlami.

## Activity log (audit trail)

`LeadActivity` alohida jadval sifatida ishlatilgan — statusni leadning
o'ziga JSON sifatida yozish o'rniga, to'liq audit trail beradi. Har bir
`CREATED`, `UPDATED`, `STATUS_CHANGED`, `DELETED` harakati yoziladi.

Lead o'chirilganda (`DELETE`) uning `LeadActivity` yozuvlari yo'qolib
ketmasligi uchun `lead_id_snapshot` va `lead_name_snapshot` maydonlari
qo'shilgan — bu orqali "kim, qachon, qaysi leadni o'chirdi" tarixi
lead o'zi o'chirilgandan keyin ham saqlanib qoladi.

## Response konventsiyasi

Har bir endpoint `{success, data, meta?}` yoki `{success, error}`
formatida qaytadi — frontend uchun bashorat qilinadigan interfeys.
Bu uch joy orqali ta'minlangan:
1. `StandardResultsPagination` — `list` endpoint uchun
2. `LeadViewSet`da `create`/`retrieve`/`update`/`destroy` metodlarining
   override qilinishi — DRF standart holatda faqat `list`ni pagination
   orqali o'raydi, qolganlarini o'z holicha qaytaradi
3. Markazlashgan `custom_exception_handler` — barcha 400/401/403/404
   xatolarni bir xil formatga keltiradi

## Auth

Stateless JWT (`simplejwt`) — session storage shart emas, horizontal
scaling uchun qulay. Access token 12 soat, refresh token 7 kun amal
qiladi, `ROTATE_REFRESH_TOKENS=True` orqali har safar refresh qilinganda
yangi refresh token ham beriladi.

## Ma'lumotlar bazasi

`UUIDField` PK sifatida ishlatilgan (auto-increment integer emas) —
tashqi API'ga xavfsiz chiqariladi, chunki UUID orqali "nechta lead
borligini" yoki "keyingi ID qaysi" ekanini hisoblab bo'lmaydi.

`DATABASE_URL` environment o'zgaruvchisi bo'lmasa avtomatik SQLite
ishlatiladi (local dev uchun hech narsa o'rnatmasdan darhol `runserver`
qilish imkonini beradi), Postgres esa Docker/production uchun `.env`
orqali ulanadi.

## AI Usage

- Model/serializer/viewset boilerplate'ini AI yordamida tez yozdim,
  keyin har bir fieldni tekshirib, validation qoidalarini (phone/email
  kamida bittasi, status enum) o'zim qattiqlashtirdim.
- Markazlashgan exception handlerni AI taklif etdi, DRF-specific va
  Django ValidationError case'larini o'zim test qilib to'g'riladim.
- `full_clean()` chaqirilmagani sababli model darajasidagi validatsiya
  ishlamayotganini o'zim payqab, `save()` metodini AI yordamida tuzatdim.