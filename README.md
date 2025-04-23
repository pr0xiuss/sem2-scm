# 📝 Blog Website

BlogView, a platform designed to provide users with an intuitive and seamless experience for reading, creating, and interacting with blog posts. The goal of this project is to build a user-friendly blog application that includes user authentication, a profile section, and an interactive commenting system. The SDLC process will guide the project from planning through to deployment, ensuring a well-executed and technically sound solution that caters to the needs of both content creators and readers.A blog post website where users can create, read, and share blogs in a beautifully designed and responsive interface. Built with Flask, MySQL, HTML, and CSS, this platform supports full CRUD (Create, Read, Update, Delete) operations for blog posts, user authentication, and dynamic user interactions.

## 🚀 Features

- User registration and login/logout system  
- Create, edit, and delete personal blog posts  
- Read and interact with posts from other users  
- Commenting system with nested replies (excluding user's own posts)  
- User profile with post history and profile editing  
- Responsive design for mobile and desktop views  
- Clean, minimal UI with high accessibility contrast  
- Structured folder hierarchy for easy scalability  
- Secure session and data management using Flask  
- GitHub Projects used for task tracking and collaboration  

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript  
- **Backend**: Python (Flask)  
- **Database**: MySQL (via SQLAlchemy)  
- **Tools**: VS Code, Git & GitHub, pip  

## 📁 Project Structure

```
blog-website/
├── static/          # CSS and image files
├── templates/       # HTML templates
├── app.py           # Main Flask application file
├── requirements.txt # List of Python dependencies
```

## 📷 UI Overview

- Home Page with blog feed in a card/grid layout  
- Navigation bar with links to Home, Profile, Create Post, and Logout  
- Profile page showing user details and blogs  
- Form pages for creating and editing blogs  
- Clean, accessible color scheme  
- Mobile-responsive layout  

*📌 Design screenshots can be added here once available.*

## ⚙️ How to Run Locally

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/blog-website.git
cd blog-website
```

2. **Set up a virtual environment and install dependencies:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask mysql-connector-python SQLAlchemy
```

3. **Update** `app.py` **with your MySQL database configuration.**

4. **Run the Flask app:**

```bash
flask run
```

5. **Open your browser and go to:**  
`http://127.0.0.1:5000/`

## 👥 Contributors

- Mohit Saklant  
- Mannan Kaushik  
- Nikhil Budhwar  
- Naman Singh  

---

> This project follows a structured SDLC approach to ensure clear planning, smooth execution, and collaborative development.
