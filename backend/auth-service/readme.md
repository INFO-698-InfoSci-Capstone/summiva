# **Auth Service - Summiva**

## 📌 Overview
The **Auth Service** is responsible for **user authentication, authorization, and token management** in the Summiva system. It provides secure **JWT-based authentication** with **access and refresh tokens**.

---

## 🚀 **API Endpoints**

### **1️⃣ Register User**
- **Endpoint:** `POST /api/v1/auth/register`
- **Description:** Creates a new user account.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true
  }
  ```
- **Possible Errors:**
  - `400 Bad Request` → Email already registered.

---

### **2️⃣ Login User**
- **Endpoint:** `POST /api/v1/auth/login`
- **Description:** Authenticates a user and provides an **access token** and **refresh token**.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "<JWT_ACCESS_TOKEN>",
    "refresh_token": "<JWT_REFRESH_TOKEN>",
    "token_type": "bearer"
  }
  ```
- **Possible Errors:**
  - `401 Unauthorized` → Invalid credentials.

---

### **3️⃣ Refresh Access Token**
- **Endpoint:** `POST /api/v1/auth/refresh`
- **Description:** Generates a **new access token** using a **valid refresh token**.
- **Request Body:**
  ```json
  {
    "refresh_token": "<JWT_REFRESH_TOKEN>"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "<NEW_JWT_ACCESS_TOKEN>",
    "token_type": "bearer"
  }
  ```
- **Possible Errors:**
  - `401 Unauthorized` → Invalid or expired refresh token.

---

### **4️⃣ Get Current User Info**
- **Endpoint:** `GET /api/v1/auth/users/me`
- **Description:** Retrieves **authenticated user details**.
- **Headers:**
  ```
  Authorization: Bearer <JWT_ACCESS_TOKEN>
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true
  }
  ```
- **Possible Errors:**
  - `401 Unauthorized` → Invalid or missing token.
  - `404 Not Found` → User does not exist.

---

## ⚙️ **Setup and Running Locally**
### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```
### **2️⃣ Run the Service**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8004
```
### **3️⃣ Run Tests**
```bash
pytest tests
```

---

## 🔥 **Next Steps**
Would you like to **add API rate-limiting or role-based access control (RBAC) next?** 😊