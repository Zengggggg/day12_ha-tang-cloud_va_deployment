# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcode API key trực tiếp trong source code
2. Hardcode database credentials (username/password)
3. Log ra thông tin nhạy cảm (API key) bằng print
4. Không sử dụng environment variables cho config
5. Không có config management (không tách dev/prod)
6. Dùng print thay vì hệ thống logging chuẩn
7. Không có health check endpoint
8. Hardcode port (8000)
9. Chỉ bind host="localhost" (không deploy được)
10. Không xử lý exception khi gọi LLM
11. Không có timeout/retry cho LLM request
12. Không có authentication hoặc rate limiting


### Exercise 1.3: Comparison table
| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| Config | Hardcode | Env vars | Tránh lộ secret, dễ deploy nhiều môi trường |
| Health check | Không có | Có `/health`, `/ready` | Giúp platform monitor và restart service khi cần |
| Logging | print() | Structured logging, không log secret | Debug tốt hơn, đảm bảo bảo mật |
| Shutdown | Đột ngột | Có lifespan, graceful shutdown | Đảm bảo ổn định khi start/stop service |
| Error Handling | Không xử lý lỗi | Dùng `HTTPException` | Tránh crash, trả lỗi rõ ràng |




## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: Base image trong Dockerfile là lớp nền tảng (image gốc) được chỉ định bởi câu lệnh FROM, đóng vai trò là hệ điều hành hoặc môi trường runtime cơ bản để xây dựng một Docker image mới. Ở đây là `python3.11`
2. Working directory: là một chỉ thị (instruction) được sử dụng để thiết lập thư mục làm việc hiện tại cho các lệnh tiếp theo như RUN, CMD, ENTRYPOINT, COPY, và ADD. Ở đây là `/app`
3. Why copy `requirements.txt` first: Để tận dụng cache của Docker. Nếu `requirements.txt` không thay đổi, Docker sẽ cache bước cài đặt dependencies, giúp build nhanh hơn khi chỉ thay đổi code. Và nếu không copy file `requirements.txt` trước, thì lệnh `pip install` sau sẽ không chạy được
4. CMD vs ENTRYPOINT: `CMD` cung cấp lệnh mặc định có thể bị ghi đè khi chạy container, trong khi `ENTRYPOINT` xác định lệnh cố định không thể bị thay đổi. Sử dụng `ENTRYPOINT` giúp đảm bảo rằng ứng dụng luôn chạy đúng cách, bất kể tham số nào được truyền vào khi khởi động container.


### Exercise 2.3: Image size comparison
- Develop: 1.67 GB
- Production: 262 MB
- Difference: 84.68%


## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Screenshot](/03-cloud-deployment/screenshot/image.png)

## Part 4: API Security

### 4.1 API Key authentication
```json
#  Không có key

{
    "detail": "Missing API key. Include header: X-API-Key: <your-key>"
}

#  Có key

{
    "question": "Hello",
    "answer": "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."
}
```

### 4.2 JWT authentication (Advanced)
```json
# Lấy token

{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZWFjaGVyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzc2NDE5NjQ0LCJleHAiOjE3NzY0MjMyNDR9.Wb5-Eph6n6MvzZ8ydyuUX8BStgHQXp9cK0ZDNOO_cZk",
    "token_type": "bearer",
    "expires_in_minutes": 60,
    "hint": "Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
}

# Dùng token để gọi API

{
    "question": "Explain JWT",
    "answer": "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
    "usage": {
        "requests_remaining": 99,
        "budget_remaining_usd": 1.9e-05
    }
}

```

### 4.3 Rate limiting

- Algorithm: Sliding Window Counter (dùng deque lưu timestamps, xoá request cũ theo window)
- Limit:
    - User: 10 requests/minute
    - Admin: 100 requests/minute
- Bypass cho admin: Không bypass hoàn toàn, mà dùng rate_limiter_admin với limit cao hơn (100 req/phút) thay vì limiter của user

```powershell
Invoke-RestMethod : {"detail":{"error":"Rate limit 
exceeded","limit":100,"window_seconds":60,"retry_after_seconds":12}}
...
```




### Exercise 4.4: Cost guard implementation
- Đây là budget-based control: giới hạn theo chi phí ($) thay vì số request
- 2 mức kiểm soát:
    - Global: hết ngân sách hệ thống → block tất cả (503)
    - User: hết quota cá nhân → block user đó (402)
- Có warning khi gần hết budget để theo dõi

- Mục tiêu: tránh tốn tiền LLM và kiểm soát usage công bằng

## Part 5: Scaling & Reliability

### 5.1 Health Checks

- Sử dụng endpoint `/health` để kiểm tra liveness và `/ready` để kiểm tra readiness của hệ thống.
- Thiết lập graceful shutdown bằng cách bắt tín hiệu `SIGTERM`, cho phép uvicorn xử lý xong các request đang chạy trước khi dừng hoàn toàn.
- **Test Output:**
```bash
curl http://localhost:8000/health
result: 200 OK


curl http://localhost:8000/ready
result: 200 OK
```

### 5.2 Graceful Shutdown

```powershell
curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d '{"question": "Long task"}' & sleep 1; kill -TERM 59709
result:
127.0.0.1:52074 - "POST /ask HTTP/1.1" 422 Unprocessable Entity
INFO:     Shutting down
INFO:     Waiting for application shutdown.
2026-04-17 17:21:56,344 INFO 🔄 Graceful shutdown initiated...
2026-04-17 17:21:56,344 INFO ✅ Shutdown complete
INFO:     Application shutdown complete.
INFO:     Finished server process [59709]
2026-04-17 17:21:56,344 INFO Received signal 15 — uvicorn will handle graceful shutdown
```

### 5.3 Stateless design

- Để có thể mở rộng ra nhiều instance mà không làm mất context (lịch sử chat) của người dùng, trạng thái ứng dụng (state) đã được tách khỏi bộ nhớ trong (in-memory) và chuyển sang lưu trữ tập trung trên Redis.

### 5.4 Load Balancing
- Nginx được sử dụng như một Load Balancer để phân phối đều lưu lượng truy cập (round-robin) tới các instance của agent.

```bash
for i in {1..10}; do    
 curl http://localhost:8080/chat -X POST \
   -H "Content-Type: application/json" \
   -d '{"question": "Request '$i'"}'
done

result:
agent-1  | INFO:     10.0.0.5:52314 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     10.0.0.5:52314 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     10.0.0.5:52314 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     10.0.0.5:52314 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:61230 - "POST /ask HTTP/1.1" 404 Not Found
agent-2  | INFO:     127.0.0.1:40122 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:53488 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:53488 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:53488 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:47810 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:38944 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:51276 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:60312 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:45628 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:54018 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:33290 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:61844 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:49902 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:42066 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:36570 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:58736 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:44982 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:52164 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     127.0.0.1:39218 - "GET /health HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:55840 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:55840 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     10.0.0.5:55840 - "POST /chat HTTP/1.1" 200 OK
```
### 5.5 Test Stateless

Thực thi lệnh `docker compose up --scale agent=3` và `python test_stateless.py`
- Kết quả:
```bash
❯ python test_stateless.py
============================================================
Stateless Scaling Demo
============================================================


Session ID: 7c2a1b8e-3d4f-4c91-9a7e-5b8d2f6c0e13


Request 1: [instance-b72c91]
 Q: What is Docker?
 A: Docker là nền tảng giúp đóng gói ứng dụng cùng môi trường để triển khai nhất quán trên nhiều hệ thống khác nhau...


Request 2: [instance-f18a3d]
 Q: Why do we need containers?
 A: Container giúp đảm bảo tính nhất quán giữa các môi trường và hỗ trợ triển khai nhanh chóng, dễ dàng mở rộng...


Request 3: [instance-4d9e2a]
 Q: What is Kubernetes?
 A: Kubernetes là hệ thống orchestration giúp tự động triển khai, scale và quản lý các container trong môi trường phân tán...


Request 4: [instance-b72c91]
 Q: How does load balancing work?
 A: Load balancing phân phối request đến nhiều instance khác nhau để tối ưu hiệu năng và tăng tính sẵn sàng của hệ thống...


Request 5: [instance-f18a3d]
 Q: What is Redis used for?
 A: Redis thường được sử dụng làm bộ nhớ cache hoặc lưu trữ session để tăng tốc truy xuất dữ liệu và hỗ trợ hệ thống phân tán...


------------------------------------------------------------
Total requests: 5
Instances used: {'instance-4d9e2a', 'instance-f18a3d', 'instance-b72c91'}
✅ All requests processed successfully across multiple instances!


--- Conversation History ---
Total messages: 10
 [user]: What is Docker?...
 [assistant]: Docker là nền tảng giúp đóng gói ứng dụng cùng môi trường để...
 [user]: Why do we need containers?...
 [assistant]: Container giúp đảm bảo tính nhất quán giữa các môi trường và...
 [user]: What is Kubernetes?...
 [assistant]: Kubernetes là hệ thống orchestration giúp tự động triển kha...
 [user]: How does load balancing work?...
 [assistant]: Load balancing phân phối request đến nhiều instance khác nha...
 [user]: What is Redis used for?...
 [assistant]: Redis thường được sử dụng làm bộ nhớ cache hoặc lưu trữ sess...


✅ Session history maintained consistently across all instances via Redis!
```
