from flask import current_app
# Replace anthropic import with the appropriate Grok 3 import
# import anthropic
import requests
import json
import base64
import random
import urllib.parse
from ..models import db, Article
from .twitter import post_to_twitter
import os
import re
from datetime import datetime, timedelta

# Create debug_images directory
debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_images")
os.makedirs(debug_dir, exist_ok=True)

# Check if stability_sdk is available
STABILITY_SDK_AVAILABLE = False
try:
    import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
    from stability_sdk import client
    STABILITY_SDK_AVAILABLE = True
    print("Stability SDK imported successfully")
except ImportError:
    print("Note: stability_sdk not found. Using placeholder images from Unsplash and Lorem Picsum instead.")

# Keep track of recent headlines to avoid repetition
RECENT_HEADLINES = []
MAX_HEADLINE_HISTORY = 10

def generate_mock_image(prompt):
    """
    Generate a mock image using Lorem Picsum or Unsplash for testing purposes
    when stability_sdk is not available
    """
    try:
        # Get a random seed based on the prompt
        seed = sum(ord(c) for c in prompt) % 1000
        random.seed(seed)
        
        # Choose between different placeholder services
        image_service = random.choice([
            # Lorem Picsum
            f"https://picsum.photos/seed/{seed}/768/512",
            # Unsplash Source with keyword
            f"https://source.unsplash.com/768x512/?{urllib.parse.quote(prompt.split()[0])}"
        ])
        
        print(f"Using mock image from: {image_service}")
        
        # Return the URL directly
        return {
            'success': True,
            'url': image_service
        }
    except Exception as e:
        print(f"Mock image generator error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def generate_image_with_stability(prompt):
    # If stability_sdk is not available, use our mock image generator
    if not STABILITY_SDK_AVAILABLE:
        print("Using mock image generator since stability_sdk is not available")
        return generate_mock_image(prompt)
    
    try:
        print("Starting Stability AI image generation...")
        print(f"Using prompt: {prompt}")
        
        # Check if API key is available
        stability_key = current_app.config.get('STABILITY_KEY')
        if not stability_key:
            print("ERROR: No Stability API key found!")
            return {'success': False, 'error': 'No Stability API key provided'}
        
        print(f"Using Stability API key: {stability_key[:5]}...{stability_key[-5:]}")
        
        # Try different engine IDs
        engine_ids = [
            None,  # Default
            "stable-diffusion-xl-1024-v1-0",
            "stable-diffusion-v1",
            "stable-diffusion-512-v2-1",
            "stable-diffusion-768-v2-1"
        ]
        
        last_error = None
        
        for engine_id in engine_ids:
            try:
                print(f"Trying engine ID: {engine_id if engine_id else 'default'}")
                
                if engine_id:
                    stability_api = client.StabilityInference(
                        key=stability_key,
                        verbose=True,
                        engine=engine_id
                    )
                else:
                    stability_api = client.StabilityInference(
                        key=stability_key,
                        verbose=True
                    )
                
                # Print available constants for debugging
                print("Available constants in generation module:")
                for item in dir(generation):
                    if not item.startswith('__') and item.startswith('SAMPLER_'):
                        print(f"  - {item}")
                
                print("Starting image generation...")
                
                # Try to find an appropriate sampler
                samplers = [
                    None,  # Default
                    generation.SAMPLER_K_EULER,
                    generation.SAMPLER_K_LMS,
                    generation.SAMPLER_DDIM,
                    generation.SAMPLER_DDPM
                ]
                
                for sampler in samplers:
                    try:
                        print(f"Trying sampler: {sampler}")
                        
                        # Build generate params
                        params = {
                            "prompt": prompt,
                            "seed": 992446758,
                            "steps": 30,
                            "cfg_scale": 8.0,
                            "width": 768,
                            "height": 512,
                            "samples": 1
                        }
                        
                        # Add sampler if specified
                        if sampler:
                            params["sampler"] = sampler
                        
                        answers = stability_api.generate(**params)
                        
                        print("Generation completed, processing results...")
                        result_count = 0
                        
                        for resp in answers:
                            result_count += 1
                            print(f"Processing result {result_count}")
                            for artifact in resp.artifacts:
                                print(f"  Artifact type: {artifact.type}, finish reason: {artifact.finish_reason}")
                                if artifact.finish_reason == generation.FILTER:
                                    print("  NSFW content detected")
                                    return {
                                        'success': False,
                                        'error': 'NSFW content detected'
                                    }
                                if artifact.type == generation.ARTIFACT_IMAGE:
                                    print("  Found image artifact")
                                    img_data = artifact.binary
                                    img_base64 = base64.b64encode(img_data).decode()
                                    
                                    # Save debug image to disk
                                    save_debug_image(img_base64, "stability_generated")
                                    
                                    image_url = f"data:image/png;base64,{img_base64}"
                                    print(f"  Image URL length: {len(image_url)}")
                                    print("  Image generation successful")
                                    
                                    return {
                                        'success': True,
                                        'url': image_url
                                    }
                        
                        # If we get here, no artifacts were found
                        print(f"No image artifacts found in {result_count} results")
                        
                    except Exception as sampler_error:
                        print(f"Error with sampler {sampler}: {str(sampler_error)}")
                        last_error = sampler_error
                        continue  # Try next sampler
                
            except Exception as engine_error:
                print(f"Error with engine {engine_id}: {str(engine_error)}")
                last_error = engine_error
                continue  # Try next engine
        
        # If we get here, all engines and samplers failed
        print("All engines and samplers failed")
        if last_error:
            print(f"Last error: {str(last_error)}")
        
        # Fall back to mock image generator
        print("Falling back to mock image generator")
        return generate_mock_image(prompt)
        
    except Exception as e:
        print(f"Stability AI error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fall back to mock image generator
        print("Falling back to mock image generator after error")
        return generate_mock_image(prompt)

def generate_image_with_stability_rest(prompt):
    """
    Generate an image using Stability AI's REST API instead of the gRPC SDK
    """
    try:
        print("Starting Stability AI REST API image generation...")
        print(f"Using prompt: {prompt}")
        
        # Check if API key is available
        stability_key = current_app.config.get('STABILITY_KEY')
        if not stability_key:
            print("ERROR: No Stability API key found!")
            return {'success': False, 'error': 'No Stability API key provided'}
        
        print(f"Using Stability API key: {stability_key[:5]}...{stability_key[-5:]}")
        
        # Try different API endpoints
        endpoints = [
            "https://api.stability.ai/v2beta/stable-image/generate/ultra",
            "https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image",
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"Trying REST API endpoint: {endpoint}")
                
                # Set up headers and parameters based on the endpoint
                if "v2beta" in endpoint:
                    # v2 API
                    headers = {
                        "Authorization": f"Bearer {stability_key}",
                        "Accept": "image/*"
                    }
                    payload = {
                        "prompt": prompt,
                        "output_format": "webp",
                    }
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        files={"none": ''},
                        data=payload
                    )
                else:
                    # v1 API
                    headers = {
                        "Authorization": f"Bearer {stability_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    payload = {
                        "text_prompts": [
                            {
                                "text": prompt,
                                "weight": 1.0
                            }
                        ],
                        "cfg_scale": 7,
                        "height": 512,
                        "width": 768,
                        "samples": 1,
                        "steps": 30
                    }
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=payload
                    )
                
                print(f"API response status code: {response.status_code}")
                
                if response.status_code == 200:
                    print("Image generation successful")
                    
                    if "v2beta" in endpoint:
                        # For v2 API, the response is the image content directly
                        img_data = response.content
                        img_base64 = base64.b64encode(img_data).decode()
                        
                        # Save debug image to disk
                        image_filename = "stability_rest_generated.webp"
                        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_images", image_filename), "wb") as f:
                            f.write(img_data)
                        
                        print(f"Debug image saved to {image_filename}")
                        
                        # Return as base64 data URL
                        image_url = f"data:image/webp;base64,{img_base64}"
                        print(f"Image URL length: {len(image_url)}")
                        
                        return {
                            'success': True,
                            'url': image_url
                        }
                    else:
                        # For v1 API, parse the JSON response
                        result = response.json()
                        if "artifacts" in result and len(result["artifacts"]) > 0:
                            img_base64 = result["artifacts"][0]["base64"]
                            
                            # Save debug image to disk
                            save_debug_image(img_base64, "stability_rest_generated")
                            
                            # Return as base64 data URL
                            image_url = f"data:image/png;base64,{img_base64}"
                            print(f"Image URL length: {len(image_url)}")
                            
                            return {
                                'success': True,
                                'url': image_url
                            }
                        else:
                            print(f"No artifacts found in response: {result}")
                else:
                    print(f"API error, status code: {response.status_code}")
                    print(f"Response: {response.text}")
            
            except Exception as endpoint_error:
                print(f"Error with endpoint {endpoint}: {str(endpoint_error)}")
                import traceback
                traceback.print_exc()
                continue  # Try next endpoint
        
        # If we get here, all endpoints failed
        print("All REST API endpoints failed")
        # Fall back to mock image generator
        print("Falling back to mock image generator")
        return generate_mock_image(prompt)
        
    except Exception as e:
        print(f"Stability AI REST API error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fall back to mock image generator
        print("Falling back to mock image generator after error")
        return generate_mock_image(prompt)

def generate_article_with_grok(topic, style, tone):
    global RECENT_HEADLINES
    
    try:
        # Use GROK_API_KEY
        api_key = current_app.config['GROK_API_KEY']
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Correct API endpoint for x.ai
        api_url = "https://api.x.ai/v1/chat/completions"
        
        # Print debug info
        print(f"Using Grok API key: {api_key[:5]}...{api_key[-5:]}")
        print(f"API endpoint: {api_url}")
        
        # Extract common terms from recent headlines to avoid repetition
        avoid_patterns = []
        if RECENT_HEADLINES:
            # Extract potential repetitive phrases from recent headlines
            common_words = []
            for headline in RECENT_HEADLINES:
                # Extract key terms (typically nouns and topics)
                words = re.findall(r'\b(?:Crypto|Bitcoin|NFT|Tech|Cat|Dog|Couple|Date|Avocado|Toast|Therapist|Billionaire|Gym|Fitness|Coffee|Instagram)\w*\b', headline, re.IGNORECASE)
                common_words.extend(words)
            
            # Count occurrences and identify overused terms
            from collections import Counter
            word_counts = Counter(common_words)
            
            # Add patterns to avoid for frequently used terms
            for word, count in word_counts.items():
                if count >= 2:  # If used twice or more recently
                    avoid_patterns.append(word)
        
        # Add extra avoidance rules based on recent headlines
        avoid_rules = ""
        if avoid_patterns:
            avoid_rules = "- ADDITIONALLY, AVOID these overused terms in your headline: " + ", ".join(avoid_patterns) + "\n"
        
        prompt = f"""You are writing a SHORT, FUNNY, SATIRICAL article for "Trust Me Bruvv" - a site that makes absurd claims with complete confidence.

        YOUR TASK:
        Create a BRIEF satirical news article (300-400 words) that presents ONE ridiculous claim with complete confidence.
        
        Topic to satirize: "{topic}"
        
        The "Trust Me Bruvv" Style:
        - Present ONE obviously false claim that's relatable and easy to understand
        - Keep it SIMPLE and FOCUSED on a single absurd idea readers can immediately grasp
        - Use made-up evidence, outlandish conclusions, or ridiculous "facts"
        - Quote ONE fake expert with a silly name
        - Use confident language like "studies confirm," "experts agree," "science proves"
        - Write SHORT paragraphs (2-3 sentences maximum)
        - Make references to everyday life that readers can relate to
        
        HEADLINE GUIDELINES:
        - Create a SINGLE headline that makes ONE outrageous claim
        - Keep it under 15 words
        - Focus on everyday activities or common behaviors
        
        Examples of GOOD headlines:
        - "Scientists Confirm Scrolling Instagram in Bed Increases Lifespan"
        - "Study Finds People Who Can't Park Are More Likely to Be CEO Material"
        - "Research Proves Telling Your Partner 'I'm Fine' Extends Arguments"
        
        ARTICLE STRUCTURE:
        1. Start with a short headline making ONE clearly ridiculous claim (NO "Headline:" prefix)
        2. First paragraph (2-3 sentences): Start DIRECTLY with the absurd claim - NO introductory phrases like "Hold onto your hats" or "Prepare to have your mind blown"
        3. Second paragraph: Include ONE ridiculous "fact" or piece of "evidence"
        4. Third paragraph: Add ONE quote from a fake expert with a silly name
        5. Fourth paragraph: Connect to a relatable everyday situation
        6. Final paragraph: Briefly offer some ridiculous advice based on the "findings"
        
        CRITICAL RULES:
        - Keep the article SHORT (300-400 words)
        - Focus on ONE main absurd claim - don't ramble or add unrelated claims
        - Use SIMPLE language - avoid overly complicated sentences
        - Keep paragraphs SHORT (2-3 sentences maximum)
        - Make the humor CLEAR and RELATABLE to everyday life
        - NO "Headline:" prefix before your headline
        - ABSOLUTELY NO opening phrases like "Hold onto your earplugs, folks" or "Brace yourself" or "Prepare to have your mind blown"
        - START DIRECTLY with the absurd claim in a straightforward, news-like manner
        """
        
        # Prepare the request payload for Grok 3
        payload = {
            "model": "grok-3",  # Adjust model name as needed
            "messages": [
                {"role": "system", "content": "You are a hilarious satirical news writer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 3000
        }
        
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        result = response.json()
        print(f"Grok API Response: {result}")  # Debug print to see the structure
        
        # Try to extract content based on different possible response formats
        content = None
        
        # Check for OpenAI-like format
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                content = result["choices"][0]["message"]["content"]
        
        # Check for possible alternative Grok format
        if content is None and "response" in result:
            content = result["response"]
        
        # Check for more possible formats
        if content is None and "text" in result:
            content = result["text"]
            
        if content is None and "content" in result:
            content = result["content"]
            
        # If we still don't have content, raise an error
        if content is None:
            raise ValueError(f"Could not extract content from API response: {result}")
            
        # Parse the content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Find the headline and clean up content
        title = None
        body_lines = []
        content_started = False
        
        for line in lines:
            # Skip HTML-like content and metadata
            if any(x in line.lower() for x in ['<div', '<h1', '</div', '</h1', 'class=', '08:58', 'entertainment']):
                continue
            
            # Handle cases where 'Headline:' appears
            if line.startswith('Headline:'):
                title = line.replace('Headline:', '').strip()
                content_started = True
            elif not title and line:
                title = line
                content_started = True
            elif content_started:
                body_lines.append(line)
        
        # Clean up title and body
        title = title.strip().replace('<h1>', '').replace('</h1>', '')
        # Remove any markdown formatting from the title
        title = title.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
        # Remove any HTML tags that might be in the title
        title = title.replace('<b>', '').replace('</b>', '').replace('<strong>', '').replace('</strong>', '')
        
        # Add the title to recent headlines to avoid repetition
        RECENT_HEADLINES.append(title)
        if len(RECENT_HEADLINES) > MAX_HEADLINE_HISTORY:
            RECENT_HEADLINES.pop(0)  # Remove oldest headline
        
        # Improve paragraph detection for better readability
        paragraphs = []
        
        # Join all body lines into a single text
        body_text = ' '.join(body_lines)
        
        # Split by double newlines if they exist (these are intentional paragraph breaks)
        if '\n\n' in body_text:
            raw_paragraphs = body_text.split('\n\n')
        else:
            # Split text into proper sentences for better paragraph formation
            sentences = []
            current_sentence = []
            
            # Better sentence detection algorithm
            i = 0
            while i < len(body_text):
                char = body_text[i]
                current_sentence.append(char)
                
                # Detect end of sentence (period, exclamation, question mark followed by space or end)
                if char in ['.', '!', '?'] and len(current_sentence) > 10:
                    # Look ahead to see if this is truly the end of a sentence
                    if i + 1 >= len(body_text) or body_text[i + 1].isspace():
                        sentences.append(''.join(current_sentence).strip())
                        current_sentence = []
                i += 1
            
            # Add any remaining text as the final sentence
            if current_sentence:
                sentences.append(''.join(current_sentence).strip())
            
            # Group sentences into paragraphs (2-3 sentences per paragraph)
            raw_paragraphs = []
            paragraph = []
            for i, sentence in enumerate(sentences):
                paragraph.append(sentence)
                
                # Create a new paragraph every 2-3 sentences or if quote detected
                quote_detected = '"' in sentence and (sentence.count('"') % 2 == 1)  # Check for quotes
                if (i + 1) % 3 == 0 or quote_detected or i == len(sentences) - 1:
                    raw_paragraphs.append(' '.join(paragraph))
                    paragraph = []
        
        # Process paragraphs and detect quotes
        formatted_paragraphs = []
        formatted_paragraphs.append('<div class="article-content">')
        
        for paragraph in raw_paragraphs:
            paragraph = paragraph.strip()
            
            # Skip empty paragraphs
            if not paragraph:
                continue
            
            # Determine if this paragraph contains a quote with attribution
            quote_start = paragraph.find('"')
            if quote_start != -1:
                quote_end = paragraph.find('"', quote_start + 1)
                if quote_end != -1 and "Dr." in paragraph:
                    # Extract the quote and format it appropriately
                    formatted_paragraphs.append(f'<blockquote class="article-quote">{paragraph}</blockquote>')
                    continue
            
            # Regular paragraph - ensure it's properly formatted with no unwanted line breaks
            clean_paragraph = ' '.join(paragraph.split())  # Normalize whitespace
            formatted_paragraphs.append(f'<p>{clean_paragraph}</p>')
        
        formatted_paragraphs.append('</div>')
        
        # Join all paragraph elements
        formatted_body = ''.join(formatted_paragraphs)
        
        # Generate image with more specific prompt
        image_url = None
        print("\n=== Image Generation ===")
        
        image_prompt = f"""Create a photorealistic news photograph about: {title}
        Style: Professional photojournalism
        Requirements:
        - High resolution
        - Clear focus
        - Realistic lighting
        - News photography style
        - Associated Press or Reuters style
        - No text or watermarks
        - Dramatic composition
        """
        
        print(f"Generating image with prompt: {image_prompt}")
        
        # First try with the new REST API method
        try:
            print("Attempting image generation with Stability REST API...")
            image_result = generate_image_with_stability_rest(image_prompt)
            
            if image_result.get('success'):
                image_url = image_result.get('url')
                print(f"Successfully generated image with REST API, URL length: {len(image_url) if image_url else 0}")
                
                # Try to save the image to a file for debugging
                if image_url and (image_url.startswith('data:image/png') or image_url.startswith('data:image/webp')):
                    base64_part = image_url.split(',')[1] if ',' in image_url else image_url
                    save_debug_image(base64_part, title)
            else:
                print(f"REST API image generation failed: {image_result.get('error')}")
                print("Falling back to other methods...")
                
                # Fall back to the SDK method if REST API fails
                if STABILITY_SDK_AVAILABLE:
                    try:
                        print("Trying with Stability SDK...")
                        image_result = generate_image_with_stability(image_prompt)
                        print(f"SDK Image generation result: {image_result}")
                        
                        if image_result.get('success'):
                            image_url = image_result.get('url')
                            print(f"Successfully generated image with SDK, URL length: {len(image_url) if image_url else 0}")
                        else:
                            print(f"SDK Image generation failed: {image_result.get('error')}")
                            print("Using mock image generator as last resort")
                            image_result = generate_mock_image(image_prompt)
                            image_url = image_result.get('url') if image_result.get('success') else None
                    except Exception as sdk_error:
                        print(f"SDK Image generation error: {str(sdk_error)}")
                        print("Using mock image generator as last resort")
                        image_result = generate_mock_image(image_prompt)
                        image_url = image_result.get('url') if image_result.get('success') else None
                else:
                    print("Stability SDK not available, using mock image generator")
                    image_result = generate_mock_image(image_prompt)
                    image_url = image_result.get('url') if image_result.get('success') else None
        except Exception as img_error:
            print(f"Image generation error: {str(img_error)}")
            import traceback
            traceback.print_exc()
            
            # Fall back to mock image generator
            print("Using mock image generator due to error")
            image_result = generate_mock_image(image_prompt)
            image_url = image_result.get('url') if image_result.get('success') else None
        
        print(f"Final image URL to save: {image_url}")
        print("=== End Image Generation ===\n")
        
        # Create the article in database
        article = Article(
            title=title,
            content=formatted_body,
            image_url=image_url
        )
        db.session.add(article)
        db.session.commit()
        
        # Post to Twitter
        twitter_result = post_to_twitter(title, article.id, image_url=image_url)
        if not twitter_result['success']:
            print(f"Failed to post to Twitter: {twitter_result.get('error')}")
        
        return {
            'success': True,
            'title': title,
            'content': formatted_body,
            'image_url': image_url
        }
            
    except Exception as e:
        print(f"Article generation error: {str(e)}")
        
        # Fallback to mock article if API fails
        print("API failed, using mock article as fallback...")
        import random
        headlines = [
            "Local Man Discovers His Cat Is Actually Russian Spy, 'Explains The Accent'",
            "Bitcoin Maximalist Shocked to Discover Money Can't Buy Love, Only Lambos",
            "Elon Musk Announces Plan to Launch Twitter Into Space: 'It'll Be Less Toxic in Zero Gravity'",
            "Study Finds 99% of Conspiracy Theories Started by People Who 'Just Want to Feel Special'",
            "New Diet Trend: Eating Only Foods You Can't Pronounce, Nutritionists Baffled"
        ]
        
        bodies = [
            "<p>In a shocking revelation that has rocked the cybersecurity world, a local tech company discovered that their entire codebase had been secretly replaced with pictures of cats.</p><p>The breach was only discovered when a junior developer tried to deploy an update and received an error message that simply read 'Meow'.</p><div class=\"quote\"><strong>\"We should have been suspicious when our servers started demanding tuna instead of electricity,\"</strong></div><p>said CTO Mark Williams, who admitted he'd been too distracted by the 'adorable error messages' to notice anything wrong.</p>",
            
            "<p>Wall Street was thrown into chaos yesterday when a group of kindergartners trading Pokémon cards outperformed the S&P 500 by 87%.</p><p>Financial experts are scrambling to understand how the 5-year-olds' strategy of 'only picking the shiniest ones' resulted in returns that have professional fund managers questioning their entire careers.</p><div class=\"quote\"><strong>\"My son traded a holographic Charizard for 50 different cards, and now he's worth more than my 401(k),\"</strong></div><p>said parent and former hedge fund manager Sarah Johnson.</p>",
            
            "<p>A recent study from the Institute of Obvious Results has confirmed what many have long suspected: 99% of people who say 'I did my own research' actually just watched a 15-minute YouTube video.</p><p>The groundbreaking study followed 1,000 self-proclaimed 'researchers' and found that their methodology primarily consisted of reading article headlines and nodding thoughtfully.</p><div class=\"quote\"><strong>\"It's actually quite impressive how confident people can be after scrolling through social media for 10 minutes,\"</strong></div><p>said lead researcher Dr. Emma Thompson.</p>"
        ]
        
        title = random.choice(headlines)
        formatted_body = random.choice(bodies)
        
        # Create the article in database with correct parameters (removed style parameter)
        article = Article(
            title=title,
            content=formatted_body,
            image_url=None
        )
        db.session.add(article)
        db.session.commit()
        
        # Post to Twitter
        twitter_result = post_to_twitter(title, article.id)
        if not twitter_result['success']:
            print(f"Failed to post to Twitter: {twitter_result.get('error')}")
        
        return {
            'success': True,
            'title': title,
            'content': formatted_body,
            'image_url': None
        }

# Rename the function to make it clear we're using Grok now
generate_article_with_claude = generate_article_with_grok

def save_debug_image(img_base64, title):
    """Save a base64 encoded image to disk for debugging"""
    try:
        # Remove data:image/png;base64, prefix if present
        if "," in img_base64:
            img_base64 = img_base64.split(",")[1]
            
        # Create debug directory if it doesn't exist
        debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_images")
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save the image
        img_data = base64.b64decode(img_base64)
        sanitized_title = "".join(c for c in title if c.isalnum() or c.isspace()).strip()
        sanitized_title = sanitized_title[:50]  # Limit title length
        filename = os.path.join(debug_dir, f"{sanitized_title}.png")
        
        with open(filename, "wb") as f:
            f.write(img_data)
            
        print(f"Debug image saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving debug image: {str(e)}")
        return False