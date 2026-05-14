# Kế hoạch chuyển đổi SendGrid: SMTP → SendGrid API

## 📋 Tổng quan

Tài liệu này mô tả quá trình chuyển đổi hoàn toàn từ gửi email qua SMTP sang SendGrid HTTP API. Điều này là cần thiết vì **Railway Free tier chặn tất cả các cổng SMTP gửi đi (25, 465, 587, 2525)**, khiến gửi email qua SMTP không thể thực hiện được trên Railway.

**Phạm vi chuyển đổi**: Thay thế giao thức SMTP bằng SendGrid REST API (HTTPS trên cổng 443, được phép trên Railway)

**Tác động dự kiến**:
- ✅ Gửi email hoạt động trên Railway
- ✅ Free tier: 100 email/ngày (đủ cho hầu hết ứng dụng)
- ✅ Tính tin cậy và giám sát tốt hơn
- ✅ Dịch vụ email sẵn sàng cho sản xuất
- ✅ Không cần thay đổi logic retry của Celery tasks

**Thời gian**: ~30 phút triển khai + kiểm tra

---

## 🎯 Tóm tắt thay đổi chính

| Item | Hiện tại (SMTP) | Mới (SendGrid) |
|------|---|---|
| **Giao thức** | SMTP (cổng 587) | HTTPS REST API (cổng 443) |
| **Thư viện** | `smtplib` (stdlib) | `httpx` (async HTTP client) |
| **Cấu hình** | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | `SENDGRID_API_KEY` |
| **Phương thức xác thực** | Tên người dùng + Mật khẩu | Bearer Token |
| **Khả dụng trên Railway** | ❌ Bị chặn | ✅ Được phép |
| **Chi phí** | Tài khoản Gmail miễn phí | SendGrid Free tier (100/ngày) |
| **Thời gian triển khai** | Đã xong | ~30 phút |

---

## 📁 Các file cần sửa đổi (7 file)

### 1. **`app/core/config.py`** - Thêm cấu hình khóa API SendGrid

**Loại thay đổi**: Thêm + Sửa nhỏ

**Vị trí**: Dòng 47-50 (phần cấu hình SMTP)

**Trước** (Cấu hình SMTP hiện tại):
```python
# ============= EMAIL CONFIGURATION =============
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
SMTP_FROM_EMAIL: str = "noreply@fastapi-practice.com"
EMAIL_DISPATCHER: str = "celery"  # "background_tasks" or "celery"
```

**Sau** (Thêm SendGrid):
```python
# ============= EMAIL CONFIGURATION =============
# SMTP (Chỉ phát triển cục bộ) - Thay thế cho SendGrid
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
SMTP_FROM_EMAIL: str = "noreply@fastapi-practice.com"

# SendGrid (Sản xuất / Railway) - Khuyên dùng
SENDGRID_API_KEY: str = ""  # Lấy từ https://sendgrid.com - định dạng: SG.xxxxx
EMAIL_DISPATCHER: str = "celery"  # "background_tasks" or "celery"
```

**Lý do**:
- Giữ SMTP cho phát triển cục bộ (tùy chọn, cho những lập trình viên không muốn tài khoản SendGrid)
- Thêm khóa API SendGrid cho sản xuất/Railway (cần thiết để gửi email trên Railway)
- Cả hai có thể tồn tại cùng nhau; `EmailService` sẽ tự động phát hiện cái nào dùng dựa vào sự có mặt của SENDGRID_API_KEY

---

### 2. **`app/services/email_service.py`** - Thay thế SMTP bằng SendGrid API

**Loại thay đổi**: Viết lại hoàn toàn (tên class giống, cách triển khai khác)

**Trước** (Hiện tại - chỉ SMTP):

Xem file hiện tại, nó dài khoảng 100+ dòng với smtplib

**Sau** (Mới - SendGrid + SMTP fallback):

```python
"""Dịch vụ email - xử lý gửi email qua SendGrid API hoặc SMTP fallback."""

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Dịch vụ gửi email qua SendGrid API (khuyến nghị) hoặc SMTP (fallback).

    Ưu tiên:
    1. SendGrid API (nếu SENDGRID_API_KEY được cấu hình) - Khuyên dùng cho sản xuất/Railway
    2. SMTP fallback (nếu SendGrid không được cấu hình) - Cho phát triển cục bộ

    Sử dụng:
        email_svc = EmailService()
        success = await email_svc.send_email(
            to="user@example.com",
            subject="Welcome!",
            html_content="<h1>Hello</h1>"
        )
    """

    def __init__(
        self,
        sendgrid_api_key: Optional[str] = None,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """Khởi tạo dịch vụ email với SendGrid hoặc SMTP.

        Args:
            sendgrid_api_key: Khóa API SendGrid (định dạng: SG.xxxxx) - khuyến nghị
            smtp_host: Tên máy chủ SMTP (fallback, mặc định từ settings)
            smtp_port: Cổng máy chủ SMTP (fallback, mặc định từ settings)
            smtp_user: Tên người dùng SMTP (fallback, mặc định từ settings)
            smtp_password: Mật khẩu SMTP (fallback, mặc định từ settings)
            from_email: Địa chỉ email người gửi (mặc định từ settings)
        """
        # Cấu hình SendGrid (chính)
        self.sendgrid_api_key = sendgrid_api_key or settings.SENDGRID_API_KEY
        self.sendgrid_api_url = "https://api.sendgrid.com/v3/mail/send"

        # Cấu hình SMTP (fallback cho phát triển cục bộ)
        self.smtp_host = smtp_host or settings.SMTP_HOST
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.smtp_user = smtp_user or settings.SMTP_USER
        password = smtp_password or settings.SMTP_PASSWORD
        self.smtp_password = password.replace(" ", "") if password else ""
        
        self.from_email = from_email or settings.SMTP_FROM_EMAIL

        # Ghi log cung cấp nào đang hoạt động
        if self.sendgrid_api_key:
            logger.info("📧 Dịch vụ email sử dụng SendGrid API (chế độ sản xuất)")
        else:
            logger.info("📧 Dịch vụ email sử dụng SMTP (chế độ phát triển cục bộ)")

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Gửi email qua SendGrid API (ưu tiên) hoặc SMTP fallback.

        Args:
            to: Địa chỉ email người nhận
            subject: Tiêu đề email
            html_content: Nội dung email dạng HTML
            plain_content: Nội dung email dạng văn bản thuần (tùy chọn)

        Returns:
            True nếu gửi thành công, False nếu không
        """
        # Dùng SendGrid nếu khóa API được cấu hình
        if self.sendgrid_api_key:
            return await self._send_via_sendgrid(to, subject, html_content, plain_content)
        else:
            # Fallback sang SMTP nếu SendGrid không được cấu hình
            return await self._send_via_smtp(to, subject, html_content, plain_content)

    async def _send_via_sendgrid(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Gửi email qua SendGrid REST API.

        Tài liệu SendGrid API:
        https://docs.sendgrid.com/for-developers/sending-email/quickstart-python

        Args:
            to: Địa chỉ email người nhận
            subject: Tiêu đề email
            html_content: Nội dung email dạng HTML
            plain_content: Nội dung email dạng văn bản thuần (tùy chọn)

        Returns:
            True nếu thành công, False nếu không
        """
        try:
            # Xây dựng payload yêu cầu SendGrid API
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to}],
                        "subject": subject,
                    }
                ],
                "from": {"email": self.from_email},
                "content": [
                    {
                        "type": "text/plain",
                        "value": plain_content or html_content.replace("<br>", "\n"),
                    },
                    {
                        "type": "text/html",
                        "value": html_content,
                    },
                ],
            }

            # Gửi qua SendGrid API với httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.sendgrid_api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.sendgrid_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )

            # Kiểm tra nếu email được gửi thành công (202 Accepted là thành công)
            if response.status_code == 202:
                logger.info(
                    f"✅ Email được gửi thành công qua SendGrid tới {to} "
                    f"với tiêu đề: {subject}"
                )
                return True
            else:
                # Ghi log phản hồi lỗi từ SendGrid
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = json.dumps(error_data, indent=2)
                except Exception:
                    pass
                logger.error(
                    f"❌ Lỗi SendGrid API (status {response.status_code}) "
                    f"gửi tới {to}: {error_msg}"
                )
                return False

        except httpx.RequestError as e:
            logger.error(f"❌ Lỗi yêu cầu SendGrid gửi tới {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Lỗi không mong đợi gửi qua SendGrid tới {to}: {str(e)}")
            return False

    async def _send_via_smtp(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Gửi email qua SMTP (fallback cho phát triển cục bộ).

        Args:
            to: Địa chỉ email người nhận
            subject: Tiêu đề email
            html_content: Nội dung email dạng HTML
            plain_content: Nội dung email dạng văn bản thuần (tùy chọn)

        Returns:
            True nếu thành công, False nếu không
        """
        try:
            # Tạo thư đa phần
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to

            # Đính kèm phiên bản văn bản thuần (fallback)
            if plain_content:
                part_plain = MIMEText(plain_content, "plain")
                message.attach(part_plain)

            # Đính kèm phiên bản HTML (ưu tiên)
            part_html = MIMEText(html_content, "html")
            message.attach(part_html)

            # Gửi qua SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()  # Sử dụng mã hóa TLS
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, message.as_string())

            logger.info(
                f"✅ Email được gửi thành công qua SMTP tới {to} với tiêu đề: {subject}"
            )
            return True

        except smtplib.SMTPException as e:
            logger.error(f"❌ Lỗi SMTP gửi email tới {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Lỗi không mong đợi gửi email tới {to}: {str(e)}")
            return False


# Thể hiện singleton
email_service = EmailService()
```

**Các thay đổi chính**:
- ✅ Thêm phương thức `_send_via_sendgrid()` sử dụng httpx async HTTP client
- ✅ Thêm phương thức `_send_via_smtp()` (code gốc)
- ✅ `send_email()` bây giờ chuyển hướng đến phương thức thích hợp dựa vào sự có mặt của SENDGRID_API_KEY
- ✅ SendGrid được ưu tiên nếu được cấu hình (sản xuất/Railway)
- ✅ Fallback SMTP cho phát triển cục bộ
- ✅ Xử lý lỗi thích hợp cho cả hai phương thức
- ✅ Ghi log tốt hơn với emoji và chỉ báo trạng thái

**Tại sao cách tiếp cận này**:
- Lập trình viên có thể kiểm tra cục bộ với SMTP mà không cần tài khoản SendGrid
- Sản xuất/Railway sử dụng SendGrid tự động khi khóa API được cung cấp
- Không cần thay đổi Celery tasks (chúng chỉ gọi `send_email()`)
- Tương thích ngược (cấu hình SMTP hiện có vẫn hoạt động)

---

### 3. **`pyproject.toml`** - Thêm phụ thuộc httpx

**Loại thay đổi**: Thêm vào danh sách phụ thuộc

**Vị trí**: Dòng ~13 (trong danh sách phụ thuộc chính)

**Trước**:
```toml
dependencies = [
    "fastapi==0.128.0",
    "uvicorn[standard]==0.30.0",
    "pydantic==2.12.5",
    "pydantic-settings==2.2.1",
    "email-validator==2.1.1",
    "python-multipart==0.0.6",
    "passlib[bcrypt]==1.7.4",
    "python-jose[cryptography]==3.3.0",
    "argon2-cffi==23.1.0",
    "sqlmodel==0.0.37",
    "asyncpg>=0.29.0",
    "redis>=5.0.0",
    "celery>=5.3.0",
]
```

**Sau**:
```toml
dependencies = [
    "fastapi==0.128.0",
    "uvicorn[standard]==0.30.0",
    "pydantic==2.12.5",
    "pydantic-settings==2.2.1",
    "email-validator==2.1.1",
    "python-multipart==0.0.6",
    "passlib[bcrypt]==1.7.4",
    "python-jose[cryptography]==3.3.0",
    "argon2-cffi==23.1.0",
    "sqlmodel==0.0.37",
    "asyncpg>=0.29.0",
    "redis>=5.0.0",
    "celery>=5.3.0",
    "httpx>=0.24.0",  # Để gửi yêu cầu SendGrid API
]
```

**Lý do**:
- `httpx` là thư viện HTTP client có tính async-native (hoàn hảo cho EmailService async của chúng ta)
- Phiên bản `>=0.24.0` hỗ trợ async/await đầy đủ với SSL/TLS thích hợp
- Thay thế: `sendgrid` SDK chính thức (nặng hơn, thêm nhiều phụ thuộc)
- Chúng tôi sử dụng `httpx` để giữ các phụ thuộc tối thiểu và tận dụng kiến trúc async của chúng ta

**Cài đặt**:
```bash
pip install httpx>=0.24.0
# hoặc
pip install .
```

---

### 4. **`.env.dev.example`** - Thêm mẫu cấu hình SendGrid

**Loại thay đổi**: Thêm

**Vị trí**: Phần Email Configuration (dòng 18-25)

**Trước**:
```env
# ============= EMAIL CONFIGURATION =============
# Để trống để kiểm tra mà không thực sự gửi email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@fastapi-practice.com
EMAIL_DISPATCHER=celery
```

**Sau**:
```env
# ============= EMAIL CONFIGURATION =============
# Tùy chọn 1: SendGrid (Khuyến nghị) - Bỏ comment dưới đây
# SENDGRID_API_KEY=SG.your-sendgrid-api-key

# Tùy chọn 2: SMTP (Phát triển cục bộ với Gmail) - Bỏ comment dưới đây
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@fastapi-practice.com

EMAIL_DISPATCHER=celery
# Ghi chú: Nếu SENDGRID_API_KEY được đặt, SendGrid sẽ được sử dụng
# Nếu không được đặt, SMTP sẽ được sử dụng như fallback
```

**Lý do**:
- Lập trình viên có thể chọn SendGrid HOẶC SMTP để kiểm tra cục bộ
- Tài liệu rõ ràng về cái nào dùng
- Cả hai tùy chọn được ghi chép để thuận tiện

---

### 5. **`.env.prod.example`** - Cập nhật SendGrid cho sản xuất

**Loại thay đổi**: Sửa + Thêm

**Vị trí**: Phần Email Configuration

**Trước**:
```env
# ============= EMAIL CONFIGURATION =============
# Phải được cấu hình trên Railway Dashboard nếu sử dụng email
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_FROM_EMAIL=noreply@fastapi-practice.com
EMAIL_DISPATCHER=celery
```

**Sau**:
```env
# ============= EMAIL CONFIGURATION =============
# Railway Free tier chặn SMTP (cổng 25, 465, 587, 2525)
# Sử dụng SendGrid API thay thế (HTTPS trên cổng 443 - được phép trên Railway)

# CẦN THIẾT: Khóa API SendGrid (Lấy từ https://sendgrid.com)
# SENDGRID_API_KEY=SG.your-sendgrid-api-key  (ĐẶT TRÊN RAILWAY DASHBOARD)

# Tùy chọn: Email người gửi (mặc định là noreply@fastapi-practice.com)
SMTP_FROM_EMAIL=noreply@fastapi-practice.com

EMAIL_DISPATCHER=celery

# Tại sao SendGrid?
# - SMTP bị chặn trên Railway Free tier
# - SendGrid cung cấp free tier: 100 email/ngày
# - REST API sử dụng HTTPS (cổng 443) mà Railway cho phép
# - Tiêu chuẩn công nghiệp cho email giao dịch
```

**Lý do**:
- Giải thích rõ ràng tại sao SMTP không hoạt động trên Railway
- Nhấn mạnh rằng SendGrid là giải pháp sản xuất
- Hướng dẫn người dùng cài đặt Biến Railway Dashboard

---

### 6. **`docker-compose.yml`** - Thêm biến môi trường khóa API SendGrid

**Loại thay đổi**: Thêm

**Vị trí**: Phần `environment` của service `web` (sau EMAIL_DISPATCHER)

**Trước** (service web):
```yaml
  web:
    ...
    environment:
      ...
      # Email
      SMTP_HOST: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USER: ${SMTP_USER:-}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL:-noreply@fastapi-practice.com}
      EMAIL_DISPATCHER: celery
      ...
```

**Sau** (service web):
```yaml
  web:
    ...
    environment:
      ...
      # Email - SendGrid (chính) hoặc SMTP (fallback)
      SENDGRID_API_KEY: ${SENDGRID_API_KEY:-}
      SMTP_HOST: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USER: ${SMTP_USER:-}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL:-noreply@fastapi-practice.com}
      EMAIL_DISPATCHER: celery
      ...
```

**Trước** (service celery_worker):
```yaml
  celery_worker:
    ...
    environment:
      ...
      # Email
      SMTP_HOST: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USER: ${SMTP_USER:-}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL:-noreply@fastapi-practice.com}
      EMAIL_DISPATCHER: celery
      ...
```

**Sau** (service celery_worker):
```yaml
  celery_worker:
    ...
    environment:
      ...
      # Email - SendGrid (chính) hoặc SMTP (fallback)
      SENDGRID_API_KEY: ${SENDGRID_API_KEY:-}
      SMTP_HOST: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USER: ${SMTP_USER:-}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL:-noreply@fastapi-practice.com}
      EMAIL_DISPATCHER: celery
      ...
```

**Lý do**:
- Cả web và celery_worker cần truy cập SENDGRID_API_KEY
- Cho phép chuyển đổi linh hoạt giữa SendGrid và SMTP
- Sử dụng `${SENDGRID_API_KEY:-}` để đọc từ .env (trống nếu không được đặt)

---

### 7. **`.env`** (File cục bộ, không commit) - Thêm khóa API SendGrid

**Loại thay đổi**: Thêm

**Trước**:
```env
# ============= EMAIL CONFIGURATION =============
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=trongtuyenlekhiet@gmail.com
SMTP_PASSWORD=kspj zvwa uula syns
SMTP_FROM_EMAIL=trongtuyenlekhiet@gmail.com
EMAIL_DISPATCHER=celery
```

**Sau** (Tùy chọn A - Sử dụng SendGrid để kiểm tra):
```env
# ============= EMAIL CONFIGURATION =============
# Tùy chọn A: SendGrid API (Khuyến nghị)
SENDGRID_API_KEY=SG.your_actual_sendgrid_api_key_here
SMTP_FROM_EMAIL=your-email@example.com
EMAIL_DISPATCHER=celery
```

**Hoặc Sau** (Tùy chọn B - Giữ SMTP cho phát triển cục bộ):
```env
# ============= EMAIL CONFIGURATION =============
# Tùy chọn B: SMTP (Mật khẩu ứng dụng Gmail - khoảng trắng sẽ được loại bỏ tự động)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=trongtuyenlekhiet@gmail.com
SMTP_PASSWORD=kspj zvwa uula syns
SMTP_FROM_EMAIL=trongtuyenlekhiet@gmail.com
EMAIL_DISPATCHER=celery
# Comment hoặc để trống: SENDGRID_API_KEY sẽ sử dụng SMTP như fallback
```

**Lý do**:
- Lập trình viên có thể chọn phương thức email nào để kiểm tra
- SendGrid để kiểm tra trong môi trường SendGrid
- SMTP để kiểm tra cục bộ nhanh chóng mà không cần khóa API

---

## 🔧 Các bước triển khai

### Bước 1: Cập nhật Phụ thuộc
```bash
cd c:\Users\tuyen\Documents\python\fastapi_practice
pip install httpx>=0.24.0
```

### Bước 2: Cập nhật Cấu hình
- Sửa `app/core/config.py` - Thêm trường SENDGRID_API_KEY
- Sửa `.env.dev.example` - Thêm phần cấu hình SendGrid
- Sửa `.env.prod.example` - Thay thế SMTP bằng giải thích SendGrid
- Cập nhật `.env` - Thêm SENDGRID_API_KEY (để kiểm tra)
- Cập nhật `docker-compose.yml` - Thêm SENDGRID_API_KEY vào service web và celery_worker

### Bước 3: Cập nhật Dịch vụ Email
- Viết lại `app/services/email_service.py` - Triển khai SendGrid mới với fallback SMTP

### Bước 4: Cập nhật Khai báo Phụ thuộc
- Sửa `pyproject.toml` - Thêm `httpx>=0.24.0` vào phụ thuộc

### Bước 5: Kiểm tra Cục bộ
```bash
# Xây dựng và chạy với docker-compose
docker-compose up -d

# Kiểm tra đăng ký người dùng để kích hoạt email chào mừng
# Kiểm tra log: docker-compose logs -f web
# Kiểm tra worker Celery: docker-compose logs -f celery_worker
```

### Bước 6: Triển khai lên Railway
1. Thêm `SENDGRID_API_KEY` vào Biến Railway Dashboard (service FastAPI và Celery)
2. Triển khai lại service
3. Kiểm tra gửi email trong sản xuất

### Bước 7: Commit Thay đổi
```bash
git add .
git commit -m "feat: Chuyển đổi email từ SMTP sang SendGrid API để tương thích Railway"
git push
```

---

## 📋 Danh sách Kiểm tra Cấu hình

### Để Phát triển Cục bộ
- [ ] Cài đặt httpx: `pip install httpx>=0.24.0`
- [ ] Cập nhật `.env` với khóa API SendGrid HOẶC thông tin xác thực SMTP
- [ ] Chạy `docker-compose up` và kiểm tra email qua đăng ký
- [ ] Kiểm tra log cho "Email được gửi thành công qua SendGrid" hoặc "qua SMTP"

### Cho Sản xuất (Railway)
- [ ] Tạo tài khoản SendGrid tại https://sendgrid.com
- [ ] Xác minh email người gửi trong bảng điều khiển SendGrid
- [ ] Lấy khóa API SendGrid (định dạng: `SG.xxxxxxxxxxxxx`)
- [ ] Thêm `SENDGRID_API_KEY` vào Biến Railway Dashboard
- [ ] Triển khai lại service FastAPI và Celery Worker
- [ ] Kiểm tra gửi email trong sản xuất

---

## 🔑 Hướng dẫn Nhanh SendGrid

### Lấy Khóa API SendGrid
1. Truy cập https://sendgrid.com/free
2. Đăng ký tài khoản miễn phí
3. Xác minh địa chỉ email của bạn
4. Đi tới Settings → API Keys → Create API Key
5. Sao chép khóa (định dạng: `SG.xxxxxxxxxxxxx`)

### Xác minh Email Người gửi (Quan trọng!)
1. Đi tới Sender Authentication trong bảng điều khiển SendGrid
2. Xác minh địa chỉ email người gửi bạn sẽ sử dụng trong `SMTP_FROM_EMAIL`
3. SendGrid sẽ không gửi email từ địa chỉ chưa xác minh

### Giới hạn Free Tier
- 100 email/ngày
- Đủ cho hầu hết ứng dụng
- Không cần thẻ tín dụng

---

## ✅ Cái GÌ KHÔNG Thay đổi

**Những thứ này vẫn không thay đổi** (không cần sửa đổi):
- ✅ `app/tasks/email_tasks.py` - Celery tasks (tầng trừu tượng, không cần thay đổi code)
- ✅ `app/tasks/celery_app.py` - Cấu hình Celery
- ✅ Logic retry Celery (max_retries=4, default_retry_delay=5s)
- ✅ Lược đồ và mô hình cơ sở dữ liệu
- ✅ Điểm cuối API
- ✅ Triển khai WebSocket

**Tại sao không cần thay đổi**:
- Email tasks gọi `email_service.send_email()` (cùng giao diện)
- Logic retry xảy ra ở mức Celery task (độc lập với EmailService)
- Địa chỉ email người gửi vẫn được cấu hình trong settings

---

## 🧪 Danh sách Kiểm tra Kiểm tra

### Trước Triển khai
- [ ] Chạy tests: `pytest`
- [ ] Kiểm tra lỗi import: `python -c "from app.services.email_service import EmailService"`
- [ ] Xác minh httpx được cài đặt: `python -c "import httpx; print(httpx.__version__)"`

### Sau Cài đặt Cục bộ
- [ ] Docker Compose khởi động không có lỗi
- [ ] Dịch vụ web FastAPI chạy trên http://localhost:8000
- [ ] Worker Celery hiển thị "connected to redis://redis:6379/0"
- [ ] Tạo người dùng qua API (điểm cuối đăng ký) → kích hoạt email chào mừng
- [ ] Kiểm tra log: `docker-compose logs -f web` → "Email được gửi thành công qua SendGrid" (hoặc SMTP)

### Sau Triển khai Railway
- [ ] SENDGRID_API_KEY hiển thị trong Biến Railway
- [ ] Log worker Celery hiển thị kết nối Redis
- [ ] Kiểm tra đăng ký người dùng → email được gửi đến địa chỉ đã đăng ký
- [ ] Xác minh email đến trong vòng 30 giây
- [ ] Kiểm tra bảng điều khiển SendGrid để xem trạng thái gửi

---

## 🔗 Liên kết Tham khảo

- **SendGrid**: https://sendgrid.com
- **Tài liệu SendGrid API**: https://docs.sendgrid.com/for-developers/sending-email/quickstart-python
- **Thư viện httpx**: https://www.python-httpx.org/
- **Giới hạn SMTP Railway**: https://docs.railway.app/overview (Giới hạn Free tier)

---

## 📊 Tóm tắt Chuyển đổi

| Khía cạnh | Trước | Sau |
|--------|--------|-------|
| **File được sửa** | - | 7 file |
| **Dòng được thêm** | - | ~300 dòng |
| **Dòng được xóa** | - | ~80 dòng (logic SMTP trùng lặp trong fallback) |
| **Phụ thuộc mới** | - | httpx>=0.24.0 |
| **Thay đổi cấu hình** | Chỉ SMTP | SMTP + SendGrid |
| **Thay đổi Breaking** | Không có | Không có (tương thích ngược) |
| **Thời gian triển khai** | - | ~30 phút |
| **Thời gian kiểm tra** | - | ~10 phút |

---

## ❓ Câu hỏi Thường gặp

**Q: Tôi có thể tiếp tục sử dụng SMTP cục bộ không?**  
A: Có! Nếu `SENDGRID_API_KEY` trống, dịch vụ sẽ tự động quay trở lại SMTP.

**Q: Nếu khóa API SendGrid sai thì sao?**  
A: Dịch vụ sẽ ghi log lỗi và trả về False. Celery sẽ thử lại sau 5 giây (tối đa 4 lần thử).

**Q: Tôi có thể sử dụng cả SendGrid và SMTP không?**  
A: Không cùng một lúc, nhưng bạn có thể kiểm tra cả hai cục bộ bằng cách chuyển đổi biến môi trường nào được đặt.

**Q: Điều này sẽ phá vỡ Celery tasks hiện có không?**  
A: Không! Celery tasks gọi `email_service.send_email()` - giao diện giống nhau, cách triển khai khác nhau.

**Q: Tôi có thể gửi bao nhiêu email với free tier SendGrid?**  
A: 100 email/ngày. Để gửi nhiều hơn, nâng cấp SendGrid hoặc sử dụng nhà cung cấp khác.

**Q: Điều gì về mẫu email?**  
A: Triển khai hiện tại hỗ trợ HTML + văn bản thuần. SendGrid cũng hỗ trợ API Mẫu cho các nhu cầu phức tạp hơn (cải thiện trong tương lai).

---

## 🎬 Các bước tiếp theo Sau khi Xem xét

Khi bạn phê duyệt kế hoạch này:

1. ✅ Tất cả 7 file sẽ được sửa như đã ghi chép
2. ✅ `httpx>=0.24.0` sẽ được thêm vào phụ thuộc
3. ✅ Các thay đổi code sẽ được kiểm tra cục bộ với docker-compose
4. ✅ Các thay đổi sẽ được commit và push lên GitHub
5. ✅ Tài liệu triển khai Railway sẽ được cung cấp
6. ✅ Bạn sẽ nhận được hướng dẫn cài đặt SendGrid

**Thời gian ước tính**: 45-60 phút (triển khai + kiểm tra)

---

**Trạng thái**: ⏳ Chờ phê duyệt để tiếp tục triển khai

**Có câu hỏi?** Cho tôi biết nếu bạn cần bất kỳ làm rõ nào trước khi bắt đầu!
