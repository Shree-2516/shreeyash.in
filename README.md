# Shreeyash's Personal Portfolio

Welcome to my personal portfolio website! This project is a dynamic, data-driven web application designed to showcase my professional journey, personal information, skills, projects, achievements, and educational background.

## Features

- **Personal Information:** A brief introduction and summary about me.
- **Projects Showcase:** Detailed descriptions of the technical projects I've built, complete with metrics, tech stacks, and links to live demos or source code.
- **Skills & Competencies:** A structured overview of my technical abilities and core competencies.
- **Work & Education Timeline:** My professional experience and academic background presented chronologically.
- **Certifications:** Badges and verification links for my professional certifications.
- **Admin CMS Dashboard:** A secure, built-in admin panel that allows me to easily add, edit, or delete portfolio content (projects, experiences, skills, certificates) without having to touch the codebase.

## Tech Stack

This project is built using:
- **Backend:** Python, Flask
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Media Storage:** Cloudinary (for profile photos, project thumbnails, and resume PDFs)

## Local Development

To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shree-2516/shreeyash.in.git
   cd shreeyash.in
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows
   # source .venv/bin/activate    # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add the necessary configurations (e.g., PostgreSQL Database URL, Cloudinary credentials, Admin credentials).

5. **Run the application:**
   ```bash
   python run.py
   ```
   The application will be accessible at `http://localhost:5000`.

## Contact
Feel free to explore the code or reach out if you have any questions or collaboration opportunities!
