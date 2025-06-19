# Trust Me Bruvv

A satirical news website that generates humorous fake news articles with absurd claims presented with complete confidence.

## Overview

"Trust Me Bruvv" is a web application that generates satirical news articles using AI. The site presents ridiculous claims as if they were legitimate news, complete with fake experts, made-up evidence, and confident language - all in good humor.

## Features

- **AI-Generated Content**: Automatically creates satirical news articles using the Grok API
- **Image Generation**: Pairs articles with AI-generated images using Stability AI
- **Category Navigation**: Browse articles by categories like Crypto, Health, Tech, and more
- **Social Media Integration**: Automatic posting to Twitter when new articles are generated

## Stack

- **Backend**: Python with Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **AI Integration**: Grok 3 API for content generation
- **Image Generation**: Stability AI API
- **Frontend**: HTML/CSS/JavaScript

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/Wunderwear/trustmebruv
   cd trustmebruv
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - `GROK_API_KEY`: Your Grok API key
   - `STABILITY_KEY`: Your Stability AI API key
   - Twitter API credentials (if using Twitter integration)

4. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the development server:
   ```
   flask run
   ```

## Content Generation

The site generates satirical news articles with:
- Absurd claims presented with journalistic confidence
- Made-up evidence and ridiculous "facts"
- Quotes from fictional experts with silly names
- Relatable references to everyday life
- Simple, focused, and humorous content


## Disclaimer

This is a satirical website. All articles are fictional and created for entertainment purposes only. Any resemblance to real news is coincidental and not intended to mislead readers.
