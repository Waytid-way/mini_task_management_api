# Mini Task Management API

REST API สำหรับจัดการ Task พร้อมระบบ Authentication ด้วย JWT  
พัฒนาด้วย Python + Flask สำหรับวิชา Backend Development

---

## 🌐 Deployed URL

> [https://mini-task-management-api-pu60.onrender.com](https://mini-task-management-api-pu60.onrender.com)

---

## ⚙️ ติดตั้งและรันโปรเจกต์

```bash
# 1. Clone repo
git clone https://github.com/Waytid-way/mini_task_management_api.git
cd mini_task_management_api

# 2. สร้าง virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. รัน development server
python app.py
```

Server จะรันที่ `http://127.0.0.1:5000`

---

## 📋 รายการ Endpoint ทั้งหมด

| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/` | ไม่ต้อง | Health check |
| POST | `/auth/register` | ไม่ต้อง | สมัคร user ใหม่ |
| POST | `/login` | ไม่ต้อง | Login รับ JWT Token |
| GET | `/me` | ✅ Bearer | ดู profile ตัวเอง |
| GET | `/tasks` | ✅ Bearer | ดูรายการ task ของตัวเอง |
| POST | `/tasks` | ✅ Bearer | สร้าง task ใหม่ |
| PATCH | `/tasks/<id>` | ✅ Bearer | อัปเดต status ของ task |
| DELETE | `/tasks/<id>` | ✅ Bearer | ลบ task |
| GET | `/external-tasks` | ✅ Bearer | ดู task ของเราและของ API เพื่อน |

---

## 🔑 วิธีใช้งาน JWT Token

1. เรียก `POST /login` เพื่อรับ token
2. นำ token ไปใส่ใน Header ของทุก request ที่ต้องการ auth:

```
Authorization: Bearer <your_token_here>
```

Token มีอายุ 1 ชั่วโมง หลังหมดอายุต้อง login ใหม่

---

## 📡 ตัวอย่าง Request / Response

### POST /login

**Request**
```json
{
  "username": "waytid",
  "password": "1234"
}
```

**Response 200**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### GET /tasks

**Header**
```
Authorization: Bearer <token>
```

**Response 200**
```json
[
  { "id": 1, "title": "First task", "status": "pending" }
]
```

---

### POST /tasks

**Header**
```
Authorization: Bearer <token>
```

**Request**
```json
{
  "title": "Finish assignment"
}
```

**Response 201**
```json
{ "id": 2, "title": "Finish assignment", "status": "pending" }
```

---

### PATCH /tasks/1

**Header**
```
Authorization: Bearer <token>
```

**Request**
```json
{
  "status": "completed"
}
```

**Response 200**
```json
{ "id": 1, "title": "First task", "status": "completed" }
```

---

### GET /external-tasks

**Header**
```
Authorization: Bearer <token>
```

**Response 200**
```json
{
  "my_tasks": [
    { "id": 1, "title": "First task", "status": "pending" }
  ],
  "external_tasks": [
    { "id": 1, "title": "Friend task", "status": "done" }
  ]
}
```

---

## ❌ ตัวอย่าง Error Response

**400 — Missing field**
```json
{ "msg": "title is required" }
```

**401 — Unauthorized**
```json
{ "msg": "Invalid username or password" }
```

**404 — Not found**
```json
{ "msg": "Task not found" }
```

**500 — External API error**
```json
{ "msg": "Cannot reach friend API: ..." }
```

---

## 🛠️ Tech Stack

| Package | Version |
|---------|---------|
| Python | 3.x |
| Flask | 3.0.1 |
| flask-jwt-extended | 4.7.1 |
| requests | 2.32.3 |
| gunicorn | 23.0.0 |
