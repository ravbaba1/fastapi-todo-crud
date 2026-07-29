# FastAPI To-Do CRUD API 🛠️🔒

A lightweight, learning-focused backend CRUD API built during my internship at **Flyrank**. This project focuses on building foundational backend pathways while maintaining a sharp focus on input validation and security.

## 🚀 Features Built
- **Create (`POST`)**: Allows users to add tasks safely.
- **Read (`GET`)**: Fetches all tasks or targets a specific task by its ID.
- **Update (`PUT`)**: Modifies titles and completion status.
- **Delete (`DELETE`)**: Removes tasks cleanly from application memory.

## 🛡️ Offensive Security Takeaways
During this build, I explored data injection vulnerabilities:
- Implemented strict **Pydantic schema validation** to enforce type safety.
- Blocked malicious string payloads (`422 Unprocessable Content`) that could break data pipeline integrity or lead to data poisoning.
- Explored API structures using the interactive **Swagger UI** mapping tool.

## 💻 Tech Stack
- Python 3.13
- FastAPI
- Pydantic
