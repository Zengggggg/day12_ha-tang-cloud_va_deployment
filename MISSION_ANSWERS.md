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
1. Base image: [Your answer]
2. Working directory: [Your answer]
...

### Exercise 2.3: Image size comparison
- Develop: [X] MB
- Production: [Y] MB
- Difference: [Z]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]