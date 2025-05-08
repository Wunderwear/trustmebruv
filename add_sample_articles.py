import os
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Article

# Sample content for the different category articles
SAMPLE_ARTICLES = [
    {
        "title": "Technology: Latest Innovations in AI Development Changing How We Work",
        "content": """
        <p>The field of artificial intelligence has experienced remarkable growth in recent years, with new innovations continually pushing the boundaries of what machines can accomplish. From advanced neural networks to sophisticated machine learning algorithms, these technologies are fundamentally changing how we work and interact with digital systems.</p>
        
        <p>Recent breakthroughs in natural language processing have enabled AI systems to understand and generate human-like text with unprecedented accuracy. This has led to the development of powerful tools that can assist with everything from content creation to code generation, making previously complex tasks accessible to a wider audience.</p>
        
        <p>Industry experts predict that as these technologies continue to evolve, we'll see even more transformative applications across various sectors, including healthcare, finance, and education. The integration of AI into everyday workflows is expected to boost productivity while enabling professionals to focus on more creative and strategic aspects of their roles.</p>
        
        <p>However, the rapid advancement of AI technology also raises important questions about ethics, privacy, and the future of work. As these systems become more capable, ensuring they're developed and deployed responsibly remains a critical challenge for technologists and policymakers alike.</p>
        """
    },
    {
        "title": "Business: Global Companies Embracing Remote Work Policies Permanently",
        "content": """
        <p>In a significant shift from traditional workplace models, many global companies are now embracing remote work policies on a permanent basis. This transition, initially accelerated by the pandemic, has evolved into a strategic business decision as organizations recognize the benefits of flexible work arrangements.</p>
        
        <p>Major corporations across various sectors have reported increased productivity, reduced operational costs, and improved employee satisfaction since implementing these policies. By eliminating geographical constraints, companies have also gained access to a broader talent pool, enhancing their ability to recruit skilled professionals regardless of location.</p>
        
        <p>"The traditional nine-to-five office model is becoming increasingly obsolete," notes industry analyst Sarah Chen. "Companies that adapt to this new paradigm will likely have a competitive advantage in attracting and retaining top talent."</p>
        
        <p>Despite these advantages, the shift presents unique challenges for businesses, including maintaining company culture, ensuring effective collaboration, and addressing potential burnout from blurred work-life boundaries. Many organizations are investing in digital tools and developing new management practices to address these concerns while maximizing the benefits of remote work.</p>
        """
    },
    {
        "title": "World: International Climate Summit Yields Unprecedented Agreement Among Nations",
        "content": """
        <p>In a historic development for global climate action, representatives from 195 countries have reached an unprecedented agreement at the latest international climate summit. The landmark accord establishes more ambitious targets for reducing greenhouse gas emissions and includes concrete commitments from both developed and developing nations.</p>
        
        <p>The agreement, which comes after two weeks of intense negotiations, features a comprehensive framework for transitioning to renewable energy sources, protecting vulnerable ecosystems, and providing financial support to countries most affected by climate change. Experts are hailing it as the most significant climate pact since the Paris Agreement.</p>
        
        <p>"This represents a crucial turning point in our collective response to the climate crisis," said UN Secretary-General in a statement following the summit's conclusion. "For the first time, we're seeing truly universal commitment to decisive action."</p>
        
        <p>Implementation of the agreement will begin immediately, with countries required to submit detailed action plans within six months. A newly established international monitoring body will track progress and ensure accountability, addressing one of the main criticisms of previous climate accords.</p>
        """
    },
    {
        "title": "Markets: Global Stock Indexes Reach Record Highs Amid Economic Recovery",
        "content": """
        <p>Global stock markets have surged to unprecedented levels as strong economic recovery signals boost investor confidence worldwide. Major indexes across North America, Europe, and Asia have posted record highs, reflecting optimism about sustained growth following recent economic challenges.</p>
        
        <p>The rally has been particularly pronounced in technology, healthcare, and renewable energy sectors, which have outperformed broader market benchmarks. Analysts attribute this performance to a combination of robust corporate earnings, supportive monetary policies, and increasing consumer spending.</p>
        
        <p>"We're witnessing a remarkable convergence of positive economic indicators," explains financial strategist Michael Rodriguez. "The current market dynamics suggest investors are pricing in continued expansion rather than reacting to short-term developments."</p>
        
        <p>While market sentiment remains predominantly bullish, some experts caution that high valuations could increase vulnerability to corrections if economic data underperforms expectations. Central banks worldwide are carefully monitoring the situation, balancing the need to support recovery while preventing potential overheating in financial markets.</p>
        """
    },
    {
        "title": "Technology: Revolutionary Quantum Computing Breakthrough Solves Complex Problems in Seconds",
        "content": """
        <p>Scientists at the Quantum Research Institute have achieved a significant breakthrough in quantum computing technology, developing a system capable of solving complex problems in seconds that would take traditional supercomputers thousands of years to complete. This advancement represents a milestone in the quest for quantum supremacy and practical quantum computing applications.</p>
        
        <p>The new quantum processor, utilizing over 1,000 qubits, demonstrated unprecedented stability and error correction capabilities, overcoming major hurdles that have limited quantum computing's practical applications. In tests, the system successfully factored large prime numbers and simulated complex molecular structures with implications for cryptography and drug development respectively.</p>
        
        <p>"This breakthrough fundamentally changes what's computationally possible," said Dr. Elena Verity, lead quantum physicist on the project. "Problems previously considered intractable are now within reach, opening new frontiers across multiple scientific disciplines."</p>
        
        <p>Industry observers note that while widespread commercial applications remain several years away, the demonstration marks a critical inflection point in quantum computing development. Major technology companies and government research agencies are already exploring potential applications in areas ranging from artificial intelligence to climate modeling and financial analysis.</p>
        """
    },
    {
        "title": "Business: Startup Revolutionizes Retail with AI-Powered Shopping Experience",
        "content": """
        <p>E-commerce startup RetailX is transforming the online shopping landscape with an innovative AI-powered platform that creates hyper-personalized shopping experiences. The company's technology combines advanced machine learning algorithms with behavioral analysis to predict consumer preferences with remarkable accuracy.</p>
        
        <p>The platform dynamically adjusts product recommendations, interface layouts, and even pricing strategies based on individual user behavior, resulting in conversion rates significantly higher than industry averages. Major retailers have taken notice, with several Fortune 500 companies already implementing RetailX's technology through partnership agreements.</p>
        
        <p>"We're moving beyond simple product recommendations into truly adaptive retail environments," explains RetailX founder and CEO Maya Johnson. "Our system learns continuously from each interaction, creating increasingly personalized experiences that benefit both shoppers and retailers."</p>
        
        <p>The company recently secured $120 million in Series C funding, achieving unicorn status with a valuation exceeding $1 billion. Industry analysts project that AI-driven personalization technologies could reshape the $4.9 trillion global e-commerce market, with RetailX positioned as an early leader in this emerging space.</p>
        """
    },
    {
        "title": "World: Archaeological Discovery Reveals Advanced Ancient Civilization Previously Unknown",
        "content": """
        <p>Archaeologists have unearthed evidence of a previously unknown advanced civilization that existed approximately 5,000 years ago in a remote region between Eastern Europe and Western Asia. The discovery challenges existing narratives about technological development in ancient societies and suggests cultural complexity far beyond what was previously understood for that era.</p>
        
        <p>The excavation site has yielded remarkably sophisticated artifacts, including precision-engineered astronomical instruments, evidence of advanced metallurgical techniques, and fragments of texts in an undeciphered writing system. Preliminary analyses indicate the civilization maintained extensive trade networks spanning thousands of miles and possessed mathematical knowledge not seen elsewhere until millennia later.</p>
        
        <p>"This discovery fundamentally alters our understanding of ancient technological development," stated Dr. Sophia Patel, lead archaeologist on the international research team. "The evidence suggests this society had capabilities we previously associated only with much later historical periods."</p>
        
        <p>Researchers are particularly intrigued by apparent cultural influences visible in artifacts from other known ancient civilizations, suggesting this newly discovered society may have been a previously missing link in the cultural development of the ancient world. Extensive analysis and excavation work continues at the site, with major museums already planning exhibitions of the findings.</p>
        """
    },
    {
        "title": "Markets: Cryptocurrency Regulation Framework Adopted by Major Global Economies",
        "content": """
        <p>In a coordinated effort to bring stability and legitimacy to digital asset markets, seven of the world's largest economies have simultaneously announced the adoption of a comprehensive cryptocurrency regulation framework. The landmark policy initiative establishes clear guidelines for cryptocurrency exchanges, stablecoin issuers, and decentralized finance platforms operating within these jurisdictions.</p>
        
        <p>The framework introduces standardized licensing requirements, consumer protection measures, and anti-money laundering protocols while creating regulatory clarity that has long been sought by institutional investors. Markets responded positively to the announcement, with major cryptocurrencies experiencing significant price increases and reduced volatility.</p>
        
        <p>"This represents the maturation of cryptocurrency from a speculative fringe asset to an established component of the global financial ecosystem," commented financial policy expert Richard Nomura. "The framework strikes a balance between enabling innovation and ensuring market integrity."</p>
        
        <p>Banking institutions that had previously avoided involvement in digital assets are now reportedly developing cryptocurrency custody and trading services in response to the regulatory clarity. Analysts project that the coordinated approach could accelerate institutional adoption and potentially bring trillions of dollars of new capital into cryptocurrency markets over the next decade.</p>
        """
    }
]

def add_sample_articles():
    """Add sample articles to the database"""
    app = create_app()
    
    with app.app_context():
        print("Adding sample articles to the database...")
        
        # Delete any existing articles
        Article.query.delete()
        db.session.commit()
        
        # Add the sample articles
        for i, article_data in enumerate(SAMPLE_ARTICLES):
            # Create article with creation date staggered back in time
            article = Article(
                title=article_data["title"],
                content=article_data["content"],
                created_at=datetime.now() - timedelta(days=i),
                image_url=None  # No image for these sample articles
            )
            db.session.add(article)
        
        db.session.commit()
        print(f"Successfully added {len(SAMPLE_ARTICLES)} sample articles.")

if __name__ == "__main__":
    add_sample_articles() 