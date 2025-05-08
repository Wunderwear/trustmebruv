import time
import random
import os
from datetime import datetime
import schedule
from app import create_app
from app.models import db, Article
from app.utils import generate_article_with_claude

# Force environment to production
os.environ['FLASK_ENV'] = 'production'
print("ENFORCING PRODUCTION MODE IN AUTO GENERATOR")

# Base topics with "Trust Me Bro" vibes - perfect for presenting as dubious facts
TOPIC_TEMPLATES = {
    "Fake Health & Fitness Facts": [
        "Correlation between specific food and personality traits",
        "Common household items secretly causing health problems",
        "Unusual activity that burns more calories than actual exercise",
        "Bizarre new fitness trend that's 'scientifically proven' to work better than traditional methods",
        "Everyday habit that 'experts' claim is worse than smoking",
        "New diet where you just look at healthy food instead of eating it"
    ],
    "Tech & Social Media 'Science'": [
        "Study about how specific phone habits reveal deep personality flaws",
        "Research connecting specific apps to unlikely health benefits",
        "Experts warning about obscure feature on common devices causing problems",
        "New 'scientific' method to gain followers based on ridiculous criteria",
        "Strange correlation between browser choice and relationship success",
        "Study showing specific emoji usage linked to intelligence or success"
    ],
    "Relationship & Dating 'Research'": [
        "Scientists finding correlation between trivial habit and relationship success",
        "Research showing ridiculous factor predicting divorce with specific percentage",
        "Study claiming certain food preferences indicate cheating probability",
        "Experts confirming bizarre habit is actually attractive to potential partners",
        "Research showing exact text response time predicting relationship longevity",
        "Scientists discovering morning routine habit indicating compatibility"
    ],
    "Economic & Financial 'Insights'": [
        "Economists finding correlation between silly purchase and wealth accumulation",
        "Financial experts confirming bizarre daily habit leads to millionaire status",
        "Research showing specific non-financial behavior impacting credit score",
        "Banking experts revealing mundane habit common among the ultra-rich",
        "Study connecting unrelated daily choice to investment success",
        "Researchers discovering weird correlation between spending habits and success"
    ],
    "Workplace & Career 'Studies'": [
        "Research showing specific desk item secretly determining promotion chances",
        "HR experts confirming bizarre interview habit that guarantees job offers",
        "Study revealing email habit that colleagues secretly judge harshly",
        "Workplace researchers finding correlation between lunch choice and salary",
        "Business experts confirming specific meaningless habit of successful CEOs",
        "Scientists discovering exact meeting behavior that makes you seem smarter"
    ],
    "Everyday 'Science' Claims": [
        "Researchers confirming mundane household choice affecting intelligence",
        "Scientists discovering bizarre correlation between unrelated daily habits",
        "Study showing specific color choice revealing shocking personality traits",
        "Experts warning about common object placement affecting your wellbeing",
        "Research revealing specific music preference indicating hidden personality flaws",
        "Scientists confirming strange connection between weather and decision making"
    ],
    "Modern Life 'Expertise'": [
        "Experts confirming specific Netflix watching habit indicating psychopathy",
        "Study showing correlation between coffee preparation method and moral character",
        "Scientists discovering exact driving habit that reveals personality disorders",
        "Research connecting pet preference to deeply concerning character flaws",
        "Experts warning about household item arrangements revealing mental state",
        "Study proving specific grocery shopping behavior predicting life success"
    ],
    "Dubious Productivity 'Research'": [
        "Researchers proving bizarre morning ritual increases productivity by exact percentage",
        "Scientists discovering specific desk arrangement boosting brainpower",
        "Study confirming unusual break activity maximizing work efficiency",
        "Experts revealing counterintuitive habit of world's most productive people",
        "Research showing specific digital behavior secretly destroying productivity",
        "Scientists confirming exact room temperature for optimal brain function"
    ],
    "Questionable Food 'Science'": [
        "Study revealing bizarre food combination boosting specific brain function",
        "Nutritionists confirming unusual eating schedule extending lifespan",
        "Research showing specific food cravings revealing personality disorders",
        "Food scientists discovering strange correlation between taste preferences and success",
        "Experts confirming eating particular food at specific time enhances abilities",
        "Study showing exact meal timing affecting intelligence and decision making"
    ],
    "Suspicious Technology 'Findings'": [
        "Researchers confirming phone charging habits revealing personality disorders",
        "Scientists discovering correlation between app organization and mental health",
        "Study showing specific device usage patterns predicting relationship success",
        "Tech experts confirming bizarre correlation between browser tabs and intelligence",
        "Research revealing exact screen time amount affecting specific brain regions",
        "Scientists warning about common device settings secretly harming wellbeing"
    ]
}

# Track recent categories and templates to avoid repetition
RECENT_CATEGORIES = []
RECENT_TEMPLATES = []
MAX_RECENT_ITEMS = 5  # Keep track of last 5 to avoid repetition

def get_random_topic():
    """Get a random topic but avoid repeating recent categories or templates"""
    global RECENT_CATEGORIES, RECENT_TEMPLATES
    
    # Get all available categories, prioritizing ones not recently used
    available_categories = [cat for cat in TOPIC_TEMPLATES.keys() if cat not in RECENT_CATEGORIES]
    
    # If all categories were recently used, use all categories but prefer least recently used
    if not available_categories:
        available_categories = list(TOPIC_TEMPLATES.keys())
        # Prefer categories used least recently (further back in history)
        if RECENT_CATEGORIES:
            preferred_category = RECENT_CATEGORIES[0]  # Oldest used category
            available_categories.remove(preferred_category)
            available_categories.append(preferred_category)  # Add to end to prioritize
    
    # Select a random category with preference toward those not recently used
    weights = [1.5 if cat not in RECENT_CATEGORIES else 0.5 for cat in available_categories]
    selected_category = random.choices(available_categories, weights=weights, k=1)[0]
    
    # Update recent categories list
    RECENT_CATEGORIES.append(selected_category)
    if len(RECENT_CATEGORIES) > MAX_RECENT_ITEMS:
        RECENT_CATEGORIES.pop(0)  # Remove oldest
    
    # Get templates for selected category, avoiding recently used ones
    available_templates = [t for t in TOPIC_TEMPLATES[selected_category] if t not in RECENT_TEMPLATES]
    
    # If all templates were recently used, use any template from category
    if not available_templates:
        available_templates = TOPIC_TEMPLATES[selected_category]
    
    # Select template with preference toward those not recently used
    weights = [1.5 if t not in RECENT_TEMPLATES else 0.5 for t in available_templates]
    selected_template = random.choices(available_templates, weights=weights, k=1)[0]
    
    # Update recent templates list
    RECENT_TEMPLATES.append(selected_template)
    if len(RECENT_TEMPLATES) > MAX_RECENT_ITEMS:
        RECENT_TEMPLATES.pop(0)  # Remove oldest
    
    print(f"Selected category: {selected_category}")
    print(f"Selected template: {selected_template}")
    
    return selected_category, selected_template

def generate_random_article():
    print(f"\n[{datetime.now()}] Starting article generation...")
    
    try:
        app = create_app()
        with app.app_context():
            # Get random category and template but avoid recent repetition
            category, template = get_random_topic()
            
            # Generate article with edgier, funnier humor style
            result = generate_article_with_claude(
                topic=template,
                style="satirical, irreverent, edgy, absurdist, specific, culturally-aware",
                tone="mocking, deadpan, hyperbolic, provocative, slightly offensive"
            )
            
            if result['success']:
                print(f"Successfully generated article: {result['title']}")
                delay = random.randint(10, 120)
                print(f"Next article scheduled in {delay} minutes")
            else:
                print(f"Error generating article: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error in generate_random_article: {str(e)}")

def run_generator():
    print("Starting automatic article generator...")
    
    while True:
        try:
            # Generate first article immediately
            generate_random_article()
            
            # Random delay between 10-120 minutes
            delay = random.randint(10, 120)
            print(f"Waiting {delay} minutes until next article...")
            time.sleep(delay * 60)  # Convert minutes to seconds
            
        except KeyboardInterrupt:
            print("\nStopping article generator...")
            break
        except Exception as e:
            print(f"Error in run_generator: {str(e)}")
            # Wait 5 minutes before retrying on error
            time.sleep(300)

if __name__ == "__main__":
    run_generator() 