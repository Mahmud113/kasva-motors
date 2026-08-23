# Kasva Motors — Vercel və Supabase quraşdırması

## 1. Supabase PostgreSQL bazası

1. [Supabase](https://supabase.com/dashboard) hesabınızda **New project** seçin və layihəni yaradın.
2. Layihə açıldıqdan sonra **Connect** bölməsinə keçin.
3. **Session pooler** və ya birbaşa PostgreSQL bağlantısının URI sətrini kopyalayın. Dəyər `postgresql://...` ilə başlamalıdır; bu, `DATABASE_URL`-dır.

## 2. Lokal mühit

Layihə qovluğunda virtual mühit və asılılıqları yaradın:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY='uzun-ve-tesadufi-gizli-acar'
export DATABASE_URL='postgresql://istifadeci:sifre@host:5432/postgres'
```

Alternativ olaraq layihə qovluğunda `.env.local` (və ya `env.local`) faylı yaradın. Tətbiq bu faylı lokal mühitdə avtomatik oxuyur; Vercel-in environment variables dəyərlərini əvəz etmir:

```env
SECRET_KEY="uzun-ve-tesadufi-gizli-acar"
DATABASE_URL="postgresql://istifadeci:sifre@host:5432/postgres"
DEBUG=False
```

`DATABASE_URL` verilməzsə, tətbiq yalnız lokal yoxlama üçün `db.sqlite3` istifadə edir.

## 3. Cədvəlləri yaratmaq və admin

Supabase bağlantısı aktiv ikən aşağıdakıları bir dəfə icra edin:

```bash
python manage.py makemigrations shop
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin paneli `http://127.0.0.1:8000/admin/` ünvanındadır. Məhsulları və sifariş statuslarını buradan idarə edin.

## 4. Vercel dəyişənləri

Vercel Dashboard → layihəniz → **Settings → Environment Variables** bölməsində bunları əlavə edin:

| Ad | Dəyər |
| --- | --- |
| `SECRET_KEY` | Güclü, təsadüfi gizli açar |
| `DATABASE_URL` | Supabase-dən kopyalanan PostgreSQL URI |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.vercel.app,sizin-domaininiz.az` |

## 5. Vercel-ə yerləşdirmə

### Vercel CLI ilə

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

İlk `vercel` sorğularında mövcud qovluğu layihə kimi təsdiqləyin. Vercel `manage.py` faylını tanıyır, Django WSGI tətbiqini avtomatik işə salır və statik faylları CDN üzərindən təqdim edir. Bu səbəbdən `vercel.json`-də köhnə `builds` və ya catch-all `routes` qaydaları əlavə etməyin.

### GitHub inteqrasiyası ilə

1. Bu qovluğu GitHub repozitoriyasına göndərin.
2. Vercel Dashboard-da **Add New → Project** seçin və repozitoriyanı import edin.
3. Yuxarıdakı dörd environment dəyişənini əlavə edin.
4. **Deploy** düyməsini seçin.

Qeyd: Vercel serverless mühitində miqrasiya avtomatik işləmir. Məlumat bazası miqrasiyalarını lokal terminaldan, `DATABASE_URL` Supabase-ə yönəlmiş halda icra edin.
