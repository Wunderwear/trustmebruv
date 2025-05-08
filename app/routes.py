from flask import Blueprint, render_template, request
from .models.article import Article

main_bp = Blueprint('main', __name__)

@main_bp.app_context_processor
def inject_top_headlines():
    # Get top articles for different categories
    tech_article = Article.query.filter(Article.title.ilike('%technology%') | Article.title.ilike('%tech%') | Article.title.ilike('%AI%')).order_by(Article.created_at.desc()).first()
    business_article = Article.query.filter(Article.title.ilike('%business%') | Article.title.ilike('%company%') | Article.title.ilike('%productivity%')).order_by(Article.created_at.desc()).first()
    world_article = Article.query.filter(Article.title.ilike('%world%') | Article.title.ilike('%global%') | Article.title.ilike('%coffee%')).order_by(Article.created_at.desc()).first()
    crypto_article = Article.query.filter(Article.title.ilike('%crypto%') | Article.title.ilike('%bitcoin%') | Article.title.ilike('%blockchain%')).order_by(Article.created_at.desc()).first()
    
    # If no articles are found for specific categories, get the latest ones
    if not tech_article:
        tech_article = Article.query.order_by(Article.created_at.desc()).first()
    if not business_article and Article.query.count() > 1:
        business_article = Article.query.order_by(Article.created_at.desc()).offset(1).first()
    if not world_article and Article.query.count() > 2:
        world_article = Article.query.order_by(Article.created_at.desc()).offset(2).first()
    if not crypto_article and Article.query.count() > 3:
        crypto_article = Article.query.order_by(Article.created_at.desc()).offset(3).first()
    
    return {
        'tech_headline': tech_article,
        'business_headline': business_article,
        'world_headline': world_article,
        'crypto_headline': crypto_article
    }

@main_bp.route('/')
def index():
    featured_article = Article.query.order_by(Article.created_at.desc()).first()
    
    # Get the 4 latest articles for the sidebar (excluding the featured one)
    sidebar_articles = Article.query.order_by(Article.created_at.desc()).offset(1).limit(4).all()
    
    # Get the next 10 articles for the news grid (avoiding duplicates with sidebar)
    news_grid_articles = Article.query.order_by(Article.created_at.desc()).offset(5).limit(10).all()
    
    return render_template('index.html', 
                          featured_article=featured_article, 
                          sidebar_articles=sidebar_articles,
                          news_grid_articles=news_grid_articles)

@main_bp.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    other_articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('article.html', 
                         article=article,
                         content=article.content,
                         other_articles=other_articles)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        # Search for articles that contain the query in their title or content
        articles = Article.query.filter(
            Article.title.ilike(f'%{query}%') | 
            Article.content.ilike(f'%{query}%')
        ).order_by(Article.created_at.desc()).all()
    else:
        articles = []
    
    return render_template('search_results.html', 
                          query=query,
                          articles=articles)

@main_bp.route('/newsletter')
def newsletter():
    return render_template('newsletter.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/cookies')
def cookies():
    return render_template('cookies.html')

@main_bp.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')