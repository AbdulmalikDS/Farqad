# Farqad: The Pioneer in Smart Financial Conversations

**A bilingual AI-powered financial chatbot and Retrieval Augmented Generation (RAG) application for intelligent document interaction and financial advice in Arabic and English.**

---

## 🌟 Features

- **Smart Financial Chatbot**
  - Personalized financial advice in Arabic and English
  - Friendly, conversational interface with chat and conversation history
  - AI-powered responses with context awareness
  - Source citation and verification  
  - ![image](https://github.com/user-attachments/assets/1999ab53-4aac-4e13-9881-c6d36faa5a59)


- **Document Management**
  - Upload and process PDF and text documents
  - Automatic document chunking and embedding for efficient retrieval
  - Document source verification  
  - ![image](https://github.com/user-attachments/assets/aab4f8d1-9cc7-437c-bf84-2f43a8fcc9f6)


- **Financial Data Visualization**
  - Dynamic chart generation from extracted financial data
  - Interactive data visualization for insights and recommendations  
  - ![image](https://github.com/user-attachments/assets/ac2987b1-57be-4230-8216-925ce8616166)


- **User & Admin Management**
  - Secure authentication system
  - User role management and session handling
  - Admin tools for monitoring users, managing data, and improving performance
  - ![image](https://github.com/user-attachments/assets/6edb54e3-4d3b-4176-8c5a-114bb06700e9)
  - ![image](https://github.com/user-attachments/assets/4f6f35ce-2117-4208-89ce-383827b7c643)


---

## 🛠️ Technical Stack

### Backend
- FastAPI for API endpoints
- MongoDB for document and user data storage
- Qdrant for vector database and document embeddings
- Pulling ALLaM with Ollama for LLM-powered chat and analytics
- PyMuPDF for PDF processing

### Frontend
- Modern, responsive web design
- Real-time chat interface
- Dynamic chart and dashboard generation
- Mobile-friendly experience

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MongoDB
- Ollama(ALLaM)
- Docker
- conda
- ubuntu

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/farqad/mini-rag-app.git
   cd mini-rag-app
   ```

2. Install dependencies:
   ```bash
   pip install -r src/requirement.txt
   pip install -r src/front-end/requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the application:
   ```bash
   # Start backend
   cd src
   python main.py

   # Start frontend (in a new terminal)
   cd src/front-end
   python main.py
   ```

### Docker Installation

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
mini-rag-app/
├── src/
│   ├── controllers/     # Business logic
│   ├── models/          # Data models
│   ├── routes/          # API endpoints
│   ├── stores/          # LLM and vector DB
│   ├── helpers/         # Utility functions
│   └── front-end/       # Frontend application
├── uploads/             # Document storage
└── qdrant_db/           # Vector database
```

---

## 🔧 Configuration

Key configuration options in `config.py`:
- MongoDB connection settings
- API configuration for local host to use the LLM locally
- Vector database settings
- Language detection settings

---

## 📝 API Documentation

### Main Endpoints

- `POST /api/upload` – Upload documents
- `POST /api/chat` – Chat with documents
- `GET /api/documents` – List documents
- `DELETE /api/documents/{id}` – Delete document

[Screenshot: API documentation interface]

---

## 🎓 Project Details

Farqad was developed as a graduation project to address the challenge of simplifying financial management and advice for Arabic and English speakers. It demonstrates:

- Advanced AI/ML concepts including NLP and RAG
- Full-stack development
- Database design and management
- API development and integration
- User interface and experience design
- Security best practices

The project offers a practical, user-friendly platform for managing budgets, analyzing financial statements, and making investment decisions, all supported by a robust, bilingual AI chatbot.

---

## 🤝 Contributing

Contributions and feedback are welcome:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## 👥 Author

- Abdulmalik Alquwayfili, Ziyad Aljenaidel
- Supervisor: Dr. Baudrulddin Khan

---

## 🙏 Acknowledgments

- Our academic supervisors for their guidance
- ALLaM for LLM capabilities
- FastAPI, MongoDB, Qdrant, and all open-source contributors

---

## 📞 Contact

For questions or support:
- GitHub: [farqad](https://github.com/farqad)
- Email: [af.alquwayfili@gmail.com]
- LinkedIn: [Abdulmalik-Alquwayfili]



> “We’re proud to have built a bilingual financial chatbot that analyzes statements and gives advice. The experience taught us teamwork, persistence, and real-world application of our studies.”
