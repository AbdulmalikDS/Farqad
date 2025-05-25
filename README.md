# Mini RAG Application - Graduation Project

A powerful Retrieval Augmented Generation (RAG) application developed as a graduation project by Farqad. This application enables intelligent document interaction through AI-powered chat, supporting both English and Arabic languages for enhanced versatility.

## 🌟 Features

- **Document Management**
  - Upload and process PDF and text documents
  - Automatic document chunking and embedding
  - Document source verification
  - [Screenshot: Document Upload Interface]

- **Intelligent Chat Interface**
  - AI-powered responses with context awareness
  - Source citation and verification
  - Support for both English and Arabic
  - [Screenshot: Chat Interface]

- **Financial Data Visualization**
  - Dynamic chart generation
  - Financial data extraction
  - Interactive data visualization
  - [Screenshot: Chart Generation]

- **User Management**
  - Secure authentication system
  - User role management
  - Session handling
  - [Screenshot: Login/Register Interface]

## 🛠️ Technical Stack

### Backend
- FastAPI for API endpoints
- MongoDB for document metadata storage
- Qdrant for vector database
- OpenAI integration for LLM
- PyMuPDF for PDF processing

### Frontend
- Modern responsive design
- Real-time chat interface
- Dynamic chart generation
- Mobile-friendly interface

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MongoDB
- OpenAI API key
- Docker (optional)

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

## 📁 Project Structure

```
mini-rag-app/
├── src/
│   ├── controllers/     # Business logic
│   ├── models/         # Data models
│   ├── routes/         # API endpoints
│   ├── stores/         # LLM and vector DB
│   ├── helpers/        # Utility functions
│   └── front-end/      # Frontend application
├── uploads/            # Document storage
└── qdrant_db/         # Vector database
```

## 🔧 Configuration

Key configuration options in `config.py`:
- MongoDB connection settings
- OpenAI API configuration
- Vector database settings
- Language detection settings

## 📝 API Documentation

### Main Endpoints

- `POST /api/upload` - Upload documents
- `POST /api/chat` - Chat with documents
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

[Add API documentation screenshot]

## 🎓 Project Details

This project was developed as part of my graduation requirements, demonstrating practical implementation of:
- Advanced AI/ML concepts
- Full-stack development
- Database design and management
- API development and integration
- User interface design
- Security best practices

## 🤝 Contributing

While this is a graduation project, contributions and feedback are welcome:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Author

- Farqad - Developer and Project Owner

## 🙏 Acknowledgments

- My academic supervisors for their guidance
- OpenAI for LLM capabilities
- FastAPI for the web framework
- MongoDB for database
- Qdrant for vector storage
- All open-source contributors whose work made this project possible

## 📞 Contact

For any questions or support regarding this graduation project:
- GitHub: [farqad](https://github.com/farqad)
- Email: [your-email@example.com]

---

[Screenshot: Application Overview/Dashboard]
