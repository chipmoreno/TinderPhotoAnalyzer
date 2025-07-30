Tinder Photo Analysis with AI
📸 Get Your Tinder Photos Expertly Analyzed by AI!
This web application provides an in-depth, AI-powered analysis of your Tinder profile photos, offering insights and actionable tips to improve your dating app success. Leveraging the power of Google's Gemini AI, it evaluates your photos based on proven strategies for male dating profiles, covering technical quality, composition, lifestyle indicators, and more.

Whether you're looking for hookups or relationships, this tool helps you optimize your visual presentation to stand out from the crowd.

✨ Features
Multi-Photo Upload: Analyze up to 9 photos at once, mirroring a typical Tinder profile.

AI-Powered Expert Analysis: Each photo is assessed against a comprehensive framework, including:

Technical Quality: Lighting, focus, resolution, background cleanliness.

Photo Composition: Facial expression, posture, eye contact, framing.

Critical Requirements: Flags for common pitfalls like mirror selfies, old photos, hats, etc.

Sequence Strategy: Recommendations for optimal photo order (e.g., "Hook" photo, body shot, social proof).

Lifestyle & Context: Identifies high-value indicators like travel, social activities, and professional settings.

Clothing & Presentation: Advice on attire, grooming, and physique display.

Target Audience Optimization: Tailored tips for hookup vs. relationship goals, and age-based targeting.

Detailed Feedback: Receive a comprehensive analysis for each image, including specific "Tips for Improvement."

Image Preview: See your uploaded photo alongside its analysis for easy comparison.

User-Friendly Interface: A clean and responsive design built with Tailwind CSS.

🚀 Technologies Used
Backend: Flask (Python web framework)

AI Model: Google Gemini 1.5 Flash (for multi-modal image and text understanding)

Frontend: HTML, CSS (Tailwind CSS)

Dependency Management: pip and requirements.txt

Environment Variables: python-dotenv for secure API key management

💻 Local Setup Instructions
Follow these steps to get the project running on your local machine:

Prerequisites
Python 3.8+

pip (Python package installer)

A Google Gemini API Key (you can get one from Google AI Studio)

Important: Enable the Gemini API for your Google Cloud Project.

1. Clone the Repository
git clone https://github.com/yourusername/tinder-photo-analysis.git
cd tinder-photo-analysis

(Replace yourusername/tinder-photo-analysis.git with the actual path to your repository if you've forked it or renamed it.)

2. Create and Activate a Virtual Environment
It's best practice to use a virtual environment to manage project dependencies.

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install Dependencies
Install all required Python packages:

pip install -r requirements.txt

4. Configure Your API Key
To keep your API key secure and out of version control, use a .env file:

Create a file named .env in the root directory of your project (the same directory as app.py).

Add your Google Gemini API key to this file:

GOOGLE_API_KEY=your_actual_google_gemini_api_key_here

(Replace your_actual_google_gemini_api_key_here with your actual key.)

Crucially, ensure .env is in your .gitignore file. If you don't have a .gitignore file, create one in your project root and add /.env to it. This prevents your API key from being accidentally committed to Git.

5. Run the Application
flask run

The application should now be running locally, typically at http://127.0.0.1:5000/.

🌐 Deployment (PythonAnywhere Guidance)
This application can be deployed to cloud platforms like PythonAnywhere to make it accessible online.

Key considerations for deployment:

API Key Security: On PythonAnywhere, it's recommended to set your GOOGLE_API_KEY as an environment variable directly through their web interface (Web tab -> Environment variables section) rather than uploading the .env file.

Rate Limiting: To prevent abuse and manage your AI API costs, implement rate limiting. A library like Flask-Limiter is highly recommended.

Google Cloud Quotas: Set spending limits and quotas for the Gemini API in your Google Cloud Console to prevent unexpected charges.

Free Tier Limitations: Be aware that free tiers on hosting platforms often have limitations (e.g., your app might "sleep" after inactivity).

💡 Usage
Upload Photos: On the home page, select one or more photos (up to 9) from your device.

Analyze: Click the "Analyze Photos" button.

View Results: The application will process your images using the AI model and display a detailed analysis for each photo, along with improvement tips.

Analyze More: Use the "Analyze More Photos" button to return to the upload page.

🤝 Contributing
Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please:

Fork the repository.

Create a new branch (git checkout -b feature/your-feature-name).

Make your changes.

Commit your changes (git commit -m 'Add new feature').

Push to the branch (git push origin feature/your-feature-name).

Open a Pull Request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.# TinderPhotoAnalyzer
