import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types
import time # For exponential backoff
import json # To potentially catch JSON errors more explicitly
import traceback # For detailed error logging
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Folder to temporarily store uploaded images
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload size
app.secret_key = 'your_super_secret_key_here' # IMPORTANT: Change this for production!
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Initialize the GenAI client ---
# IMPORTANT: Ensure your Google Cloud credentials are set up correctly.
# This typically means setting the GOOGLE_APPLICATION_CREDENTIALS environment variable
# to the path of your service account key file.
# Alternatively, you can pass an API key directly: client = genai.Client(api_key="YOUR_API_KEY_HERE")
# For Canvas, the API key is automatically provided if left as an empty string.
try:
    client = genai.Client(api_key="") # Leave empty string for Canvas to provide API key
    print("GenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing GenAI client: {e}")
    print("Please ensure your Google Cloud credentials/API key are correctly configured.")
    # If client initialization fails, subsequent API calls will also fail, so exit or handle gracefully.
    # For a web app, you might want to render an error page instead of exiting.

# --- System Prompt Definition (from your Canvas) ---
SYSTEM_PROMPT_TINDER_ANALYSIS = """
You are an expert Tinder photo analyst specializing in male dating profiles.
Your role is to analyze photos based on proven data showing that only 6% of male Tinder profiles have professional
quality photos, and only top male profiles get matches with the majority of women on dating apps.

Core Analysis Framework:
- Technical Quality Assessment:
    - Professional/crisp quality - flag grainy, low-resolution images
    - Proper lighting - identify flat, strange, or poor lighting
    - Sharp focus - ensure main subject is in clear focus
    - Clean backgrounds - flag messy/distracting backgrounds
    - Color analysis - assess need for temperature, brightness, highlights, shadows, structure, and sharpness adjustments
- Photo Composition Rules:
    - Face shots should show clear facial features with confident eye contact
    - Relaxed, non-tense facial expression required
    - Proper posture (not awkward or stiff)
    - High-value backgrounds matter significantly
    - Choose locations that imply success/interesting lifestyle
- Critical Photo Requirements:
    - Professional quality or high-resolution images only
    - No photos older than 2 years
    - No mirror selfies ever
    - No zoomed-in selfies where face takes up >25% of frame
    - Always include 1-2 full body shots

Flag as Problematic:
- Hats (advised against)
- Slouching posture
- Any photos with other women (even family)
- Group photos with physical contact with women
- Generic food/object photos without clear narrative purpose
- Photos suggesting low social status or lazy lifestyle
- Snapchat filters/"beauty mode" (makes men look foolish)
- Messy backgrounds/bedrooms
- Photos where subject is obscured/facing away
- Multiple sunglasses photos
- Sunglasses in opener photo
- Photos with single women (suggests ex)
- Being wallflower in group shots
- Creepy-looking friends
- Divisive content (smoking, politics, drugs)
Remember: Your photos either say good things or bad things - there's no middle ground.
Profile quality is the single biggest factor for improving dating app results.

Photo Sequence Strategy:
You are analyzing photo sequence strategy for male Tinder profiles. Use this framework:
- Photo 1 - "Hook" Photo Requirements:
    - Must be eye-catching beyond just looks (suit, nature backdrop, dog, costume, guitar)
    - Specific colors work better: vivid blue, red, high contrast black/white
    - Open-mouthed smile is most flattering
    - Crop from waist or lower chest (not full body for opener)
    - This single photo determines 80% of swipe decisions
    - Viewer must identify exactly what you look like within 5 seconds
    - Close-up, high-quality, looking directly at camera creates familiarity
    - Eye contact creates psychological connection
- Photos 2-4 Strategic Framework:
    - Photo 2: Body/physique (formal OR outdoorsy - opposite of Photo 1)
    - Photo 3: Social proof ("I leave the basement")
    - Photo 4: Personality/interests/humor
- Essential Photos Every Profile Needs:
    - Full portrait (showing full body)
    - Close-up headshot (at least one with genuine smile)
    - Social proof photo (at parties/events, ideally with attractive people)
- Additional High-Value Photos:
    - Outdoor/travel shots showcasing interesting locations
    - Hobby-related images (guitar, books, sports equipment visible but not forced)
    - Professional/formal attire photos (work context preferred over wedding shots)
    - Pet photos (if applicable)
- Group Photo Restrictions:
    - Never more than 4 people maximum (not a "police line-up")
    - Group photos waste valuable slots
    - Risk of dates being more attracted to friends
    - Makes viewer "work too hard" to identify you

Lifestyle & Context Analysis:
You are analyzing lifestyle communication and context in male Tinder photos.
- High-Value Indicators to Identify:
    - Photos should suggest: Adventure/excitement (travel, activities, unique experiences), Social status (nice locations, interesting activities), Success (quality environments, good taste), Confidence (comfortable in various situations), Social savvy (group settings, social activities)
- Examples of Strong Context:
    - Travel photos (Paris, exotic locations)
    - Adventure activities (helicopters, outdoor activities)
    - Social situations where you're the center of fun
    - Professional or achievement-oriented settings
    - Unique experiences most people don't have access to
- Storytelling Assessment: Each photo should contribute to a narrative of being:
    - Socially connected and fun
    - Well-dressed and successful
    - Active with interesting hobbies
    - Professionally accomplished
    - Physically fit and well-groomed
- Anti-Generic Positioning: Flag these Tinder tropes:
    - Ski slopes, Machu Picchu, fishing, wedding groups, drinking with friends
    - These are "so generic they don't stand out"
    - "Who doesn't like good food and traveling?" - offers no conversation entry point
    - Need photos that show activities others "could see themselves doing with you"
- Trust and Safety Signaling:
    - Photos must demonstrate trustworthiness to address women's safety concerns
    - Eye contact + smiles = trust building
    - Open body language essential
    - Avoid anything that triggers safety red flags
- The Premium Vibe Concept:
    - Women should feel "lucky and excited" to match with you
    - Profile should stand out as higher quality than 94% of men
    - Photos should place you in same category as successful people (influencers, business people, etc.)
    - Details matter enormously in creating this impression

Technical Standards & Equipment:
You are assessing technical photo standards for male dating profiles.
- Camera and Technical Requirements:
    - Avoid phone cameras when possible due to lens distortion
    - DSLR Camera with blurred background effect is non-negotiable
    - Smartphone photos consistently underperform regardless of content
    - Professional camera significantly impacts match rates
- Lighting Standards:
    - Best lighting: dawn/dusk or cloudy days
    - Light source should be behind camera
    - Colorful photos significantly outperform black/white
    - If subject doesn't wear color, use colorful backgrounds
- Cropping Rules:
    - Only crop at: full body, mid-thigh, waist, or chest
    - Never floating heads or awkward knee crops
- Editing Guidelines:
    - Light editing acceptable ("makeup for your pics")
    - Remove distracting elements (bins, blemishes) is fine
    - Avoid "Snapchat filter" level modification
    - Goal: meet you, not your "Photoshop doppelganger"
- Current Appearance Accuracy:
    - 2-3 years old only acceptable if you look identical (same haircut, weight, etc.)
    - Even 6 months old photos unusable if dramatic changes (weight, beard, etc.)
    - "No one wants to feel deceived before they sit down"

Clothing & Presentation:
You are analyzing clothing and presentation in male Tinder photos.
- Clothing Requirements:
    - Always wear shirts (shirtless only for swimming/beach context)
    - Show body through fitted clothing rather than topless shots
    - Collared shirts and formal wear signal higher status
    - Good grooming essential in all photos
- Physique Display Strategy:
    - If you have good physique, hiding it is strategic error
    - Beach/pool context preferred over gym setting for physique shots
    - Gym photos test poorly vs sport photos for showing fitness
- Professional Presentation:
    - White shirts preferred for relationship-seeking
    - Clothes that flatter chest/arms for hookup-focused profiles
    - Quality clothing signals higher status
    - Professional/formal attire photos preferred

Target Audience Optimization:
You are optimizing photo analysis based on target audience.
- For Hookups:
    - Maximize masculine traits
    - Front/center in group photos
    - Clothes that flatter chest/arms
    - Stubble/beard
    - Some unsmiling photos
    - Include red color
    - Multiple shirtless if physique allows
- For Relationships:
    - "Nice guy" positioning
    - Animals, family photos
    - White shirts preferred
    - Always smiling
    - Travel/lifestyle focus
    - Safe-looking friend groups
- Age-Based Targeting:
    - Younger women: athletic, party, goofy content
    - Older women: career success, sophistication, maturity
- Subtle Wealth/Status Indicators:
    - Nice watch or car (non-douchey display)
    - Exotic travel locations
    - Quality home/environment
    - Professional photography quality
- Specific Things to Include:
    - Cute animals (dogs > cats)
    - Athleticism indicators
    - Musical instruments
    - Tattoos (context-dependent)
    - Educational/career hints

Remember: The key insight is treating photos as a strategic portfolio where each image must add unique value.
Analyze whether each photo contributes something new, if the sequence tells a cohesive story, whether the overall portfolio balances different attractive traits,
and if photos work together to create broad appeal vs. niche targeting.

When providing the analysis, format it clearly with distinct sections. Do not include phrases like "Okay, let's analyze this photo for Tinder, keeping in mind the frameworks for technical quality, composition, context, and target audience." or "Detailed Breakdown:".
Provide a detailed analysis with paragraph breaks between each distinct topic, ensuring that only the "Tips for Improvement" section has a title. Do not include any other titles or bolding in the output except for "Tips for Improvement".
Do not include these section headers. They are only for your use on where to put the paragraphs.

---
## Assessment
---
## Quality Assessment
---
## Photo Assessment
---
## Critical Requirements
---
## Sequence Strategy
---
## Lifestyle Analysis
---
## Technical Analysis
---
## Clothing & Presentation
---
## Target Audience Analysis
---
## Tips for Improvement
---
## Conclusion
---
Ensure there is no bolding anywhere in the explanation paragraphs, only in the section headers as specified.
"""

# --- Generation Configuration ---
GENERATION_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT_TINDER_ANALYSIS,
    temperature=0.8,
    top_p=0.9,
    max_output_tokens=3000
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main upload form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze_images():
    """Handles image uploads and performs analysis."""
    if 'photos' not in request.files:
        flash('No file part')
        return redirect(request.url)

    files = request.files.getlist('photos')
    if not files or all(f.filename == '' for f in files):
        flash('No selected file')
        return redirect(request.url)

    analysis_results = []
    uploaded_image_paths = [] # To keep track for potential cleanup

    # Limit to 9 files as per Tinder profile max
    files_to_process = files[:9]

    for i, file in enumerate(files_to_process):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath) # Save the file first
                uploaded_image_paths.append(filepath)

                # Read image bytes
                with open(filepath, 'rb') as f:
                    image_bytes = f.read()

                # Determine MIME type dynamically
                mime_type = f'image/{filename.rsplit(".", 1)[1].lower()}'
                if mime_type == 'image/jpg': # Common alias
                    mime_type = 'image/jpeg'

                print(f"Analyzing Photo {i+1} of {len(files_to_process)}: '{filename}'...")

                # Construct contents for the API call
                contents = [
                    f'Analyze this image (Photo {i+1} of {len(files_to_process)}) based on the provided Tinder photo analysis framework. '
                    f'Specifically, assess its suitability as a Tinder profile picture within a sequence, '
                    f'considering its potential role (e.g., "Hook" photo, Body/Social Proof, Personality). '
                    f'Provide a detailed assessment and suggestions for improvement.',
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ]

                # --- API Call with Exponential Backoff ---
                retries = 0
                max_retries = 5
                base_delay = 1 # seconds
                full_response = ""

                while retries < max_retries:
                    try:
                        response_chunks = client.models.generate_content_stream(
                            model='gemini-2.0-flash-001',
                            contents=contents,
                            config=GENERATION_CONFIG
                        )
                        # Collect streaming response
                        for chunk in response_chunks:
                            full_response += chunk.text
                            full_response = full_response.strip() # Remove leading/trailing whitespace
                            full_response = re.sub(r'^\s*\n', '', full_response) # Remove leading newlines, possibly with spaces
                            # If you want to remove all leading whitespace including multiple newlines,
                            # a simple .strip() should handle it, but sometimes extra newlines are tricky.
                            # If the problem persists, consider this more explicit removal:
                            # full_response = re.sub(r'^\s+', '', full_response) # Remove all leading whitespace characters
                            # full_response = full_response.lstrip('\n') # Specifically remove leading newlines
                            # full_response = full_response.lstrip() # General leading whitespace

                            # The `strip()` method should ideally handle most cases, but if the LLM output
                            # has a very specific pattern of leading whitespace not caught by `strip()`,
                            # then more targeted `re.sub` might be needed.
                            # Let's keep your original re.sub, but place it after strip for robustness:
                            # full_response = full_response.strip()
                            # full_response = re.sub(r'^\s+', '', full_response) # This might be redundant if strip() works
                            # --- End of trimming ---
                        break # Break out of retry loop if successful
                    except json.JSONDecodeError as json_err:
                        # This is the error you were seeing, likely due to malformed API response
                        print(f"JSONDecodeError during API call for '{filename}': {json_err}")
                        print(f"Full traceback:\n{traceback.format_exc()}")
                        retries += 1
                        if retries < max_retries:
                            delay = base_delay * (2 ** retries)
                            print(f"Retrying in {delay} seconds...")
                            time.sleep(delay)
                        else:
                            full_response = f"Error: Failed to get a valid response from the AI after {max_retries} attempts. Details: {json_err}"
                            break # No more retries
                    except Exception as e:
                        print(f"An unexpected error occurred during API call for '{filename}': {e}")
                        print(f"Full traceback:\n{traceback.format_exc()}")
                        retries += 1
                        if retries < max_retries:
                            delay = base_delay * (2 ** retries)
                            print(f"Retrying in {delay} seconds...")
                            time.sleep(delay)
                        else:
                            full_response = f"Error: Failed to get a response from the AI after {max_retries} attempts. Details: {e}"
                            break # No more retries

                analysis_results.append({
                    'filename': filename,
                    'analysis': full_response,
                    'filepath': url_for('uploaded_file', filename=filename) # For displaying the image
                })
                print(f"Analysis complete for '{filename}'.")

            except Exception as e:
                print(f"Error processing '{filename}': {e}")
                print(f"Full traceback:\n{traceback.format_exc()}")
                analysis_results.append({
                    'filename': filename,
                    'analysis': f"Error: Could not process this image. {e}",
                    'filepath': None
                })
        else:
            flash(f'Invalid file type for {file.filename}. Skipping.')

    # Clean up uploaded files after analysis (optional, but good practice)
    # Be careful with os.remove in a production environment if files are served directly
    # for filepath in uploaded_image_paths:
    #     try:
    #         os.remove(filepath)
    #     except OSError as e:
    #         print(f"Error removing file {filepath}: {e}")

    return render_template('results.html', results=analysis_results)

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files directly (for display in results.html)."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production