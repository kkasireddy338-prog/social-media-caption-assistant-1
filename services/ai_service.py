import random
import re
from config import Config

# Try to import Gemini; fall back gracefully if unavailable or key missing
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

DEMO_MODE = not Config.GEMINI_API_KEY or not GEMINI_AVAILABLE

if not DEMO_MODE:
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Demo caption templates (clearly labeled as sample / demo content)
# These are shown ONLY when no Gemini API key is configured.
# ---------------------------------------------------------------------------
DEMO_CAPTIONS = {
    "Instagram": {
        "Travel": [
            "Wandering where the WiFi is weak and the sunsets are strong Every destination tells a story — this one stole my heart completely.",
            "Not all those who wander are lost... but I definitely need GPS Adventure is calling and I must go! Drop a globe if you love to travel!",
            "Chasing horizons one city at a time Life is short, the world is wide — keep exploring! Save this for your next trip inspo"
        ],
        "Food": [
            "Eating my way through life one delicious bite at a time Food is not just fuel — it's a love language. Tag your foodie bestie below!",
            "Good food + good company = the perfect recipe for happiness What's your all-time favorite comfort food? Tell me in the comments!",
            "Life is uncertain, eat dessert first This plate just made my whole week better. Would you try this?"
        ],
        "Fitness": [
            "No shortcuts, just hard work and sweat Every rep counts, every drop of sweat is progress. Keep pushing — you're closer than you think!",
            "Your only competition is who you were yesterday Small steps lead to giant leaps. What's your fitness goal this week?",
            "Strong is not just a body shape — it's a mindset Embrace the grind, celebrate the gains. Tag someone who needs this motivation!"
        ],
        "Technology": [
            "The future is already here — it's just not evenly distributed yet Embracing innovation one line of code at a time.",
            "Building tomorrow's solutions with today's curiosity Tech is not just a career, it's a superpower. What tech trend excites you most?",
            "Code is poetry, data is the new oil Staying ahead of the curve in this ever-evolving digital world."
        ],
        "Motivation": [
            "Your setbacks are just setups for your greatest comebacks Believe in the magic of new beginnings. Keep going — the best is yet to come!",
            "Dream big. Work hard. Stay humble. Success is not given, it's earned one day at a time. What's driving you today?",
            "You are one decision away from a completely different life Make it count. Are you ready to level up?"
        ],
        "Business": [
            "Great businesses start with a single bold idea — yours could be next. Take the leap, trust the process, and embrace every challenge.",
            "Consistency is the secret ingredient no one talks about. Show up every day, deliver value, and watch your brand grow stronger.",
            "Your brand is not what you sell — it's how you make people feel. Focus on the experience and the revenue will follow."
        ],
        "Fashion": [
            "Style is a way of saying who you are without having to speak. Today's look is all about confidence and bold choices.",
            "Fashion is not about following trends — it's about setting them. This outfit is pure expression, no apologies.",
            "Life is too short to wear boring clothes. Every day is a runway — walk it like you own it."
        ],
        "Lifestyle": [
            "Slow mornings, good coffee, and a heart full of gratitude. This is the life I choose every single day.",
            "Balance is not something you find — it's something you create. Building a life I love, one intentional day at a time.",
            "Surround yourself with people who inspire you, places that fill you, and moments that remind you why it's all worth it."
        ],
        "Entertainment": [
            "Life is better with a little drama — on screen, at least! Currently obsessed with this show and I have zero regrets.",
            "Some nights are made for laughing so hard your stomach hurts. Making memories that will last long after the credits roll.",
            "The best stories aren't just told — they're lived. Currently writing the most exciting chapter of mine."
        ],
        "Education": [
            "Every expert was once a beginner. Keep learning, keep growing — knowledge is the one thing no one can take from you.",
            "The mind is a muscle. The more you train it, the stronger it gets. What are you learning today?",
            "Education is not preparation for life — education is life itself. Never stop being a student of the world."
        ]
    },
    "LinkedIn": {
        "Business": [
            "In business, your network is your net worth. Invest in relationships, not just revenue. The connections you build today shape tomorrow's opportunities.",
            "Great companies aren't built by individuals — they're built by teams with shared vision. Culture eats strategy for breakfast. What's your team's superpower?",
            "Failure is not the opposite of success — it's a stepping stone to it. Every setback carries a lesson worth more than any MBA course."
        ],
        "Technology": [
            "AI is not replacing human intelligence — it's amplifying it. The professionals who thrive will learn to collaborate with AI, not compete against it.",
            "Digital transformation is not about technology — it's about people. The best tech stack means nothing without the right team behind it.",
            "Cybersecurity is no longer an IT issue — it's a business imperative. Every leader needs to understand the digital threat landscape."
        ],
        "Motivation": [
            "Success is not about the destination — it's about who you become on the journey. Keep showing up, keep growing, keep leading.",
            "Your career is not a sprint — it's a marathon. The habits you build today will compound into the results of tomorrow.",
            "The most successful people I know have one thing in common: they never stopped being students. Commit to lifelong learning."
        ],
        "Education": [
            "The investment with the highest return is always the one you make in yourself. Upskilling today keeps you irreplaceable tomorrow.",
            "Mentorship accelerates growth in ways that no textbook can replicate. Find your mentor, be a mentor — the cycle pays forward.",
            "Knowledge shared is knowledge multiplied. When we elevate each other, we all rise together. What's one thing you learned this week?"
        ],
        "Lifestyle": [
            "Work-life integration, not balance — because the best version of you at work is the same person who shows up at home.",
            "Boundaries are not walls — they're the foundation of sustainable success. Protect your energy so you can give your best, every day.",
            "Your well-being is your competitive advantage. Invest in sleep, relationships, and rest — they fuel everything else."
        ],
        "Travel": [
            "Every business trip is a masterclass in adaptability. New city, new challenges, new perspectives — that's where growth happens.",
            "The world's best boardroom has no walls. Some of my greatest ideas came from stepping away and exploring something new.",
            "Traveling for work, growing for life. Every new destination teaches me something I could never learn in a conference room."
        ],
        "Fashion": [
            "Your wardrobe is your personal brand. Dress not for the job you have, but for the confidence you want to carry.",
            "Professional style is not about expensive clothes — it's about intentional choices that communicate your values without a word.",
            "In a world of noise, a well-put-together appearance is still one of the most powerful first impressions you can make."
        ],
        "Food": [
            "Great meals bring great minds together. Some of the best business conversations I've had happened over shared food and genuine connection.",
            "Nurturing your body is non-negotiable. What you eat fuels how you think, lead, and perform.",
            "Team lunches are underrated. Breaking bread together builds trust that no team-building exercise can manufacture."
        ],
        "Fitness": [
            "My morning workout is my leadership training. Discipline, consistency, and resilience — the gym teaches it all.",
            "CEOs who exercise regularly share one thing: they treat their health as a business asset, not an afterthought.",
            "Physical fitness is a mirror for professional fitness. The same habits that build a strong body build a strong career."
        ],
        "Entertainment": [
            "Creativity is a muscle, and entertainment is one of its best trainers. The stories we consume shape the leaders we become.",
            "Great storytelling is the most underrated business skill. Study what captivates an audience — it applies everywhere.",
            "Inspiration doesn't always come from industry reports. Sometimes the best ideas come from stepping away and enjoying something purely for fun."
        ]
    },
    "Facebook": {
        "Lifestyle": [
            "Life is not measured by the number of breaths we take, but by the moments that take our breath away Cherishing every beautiful moment. What made you smile today?",
            "Surround yourself with people who make you laugh louder, live a little wilder, and love a little deeper Grateful for my amazing circle! Tag your people!",
            "The little things in life often turn out to be the biggest things Slow down, look around — there's beauty everywhere if you choose to see it."
        ],
        "Travel": [
            "Adventure found me and I didn't even resist! Sharing this beautiful journey with the people I love most. Where should we go next?",
            "Home is wherever the heart is — and right now, my heart is here soaking up every beautiful moment of this trip!",
            "Some places change you in the best way possible. This destination will forever hold a special place in my heart."
        ],
        "Food": [
            "Sunday cooking is my love language! Made this from scratch and I cannot wait to share it with the family. Recipe in comments!",
            "Food tastes better when you share it. Gathered around the table with the people I love — this is what happiness looks like.",
            "Tried this amazing new restaurant in town and WOW. If you haven't been, you absolutely need to go. Drop a heart if you want the details!"
        ],
        "Fitness": [
            "Starting this fitness journey was the best decision I ever made! Sharing my progress to keep myself accountable. Who else is on this journey?",
            "Rest days are part of the process too! Recovery is where the real magic happens. Take care of your body — it's the only one you've got.",
            "Signed up for my first 5K and I could not be more excited! Training starts today. Wish me luck and cheer me on!"
        ],
        "Motivation": [
            "Monday reminder: You are capable of more than you realize. This week, choose courage over comfort and watch what happens.",
            "If you're going through a tough time right now, hang in there. The storm always passes, and what comes after is worth the wait.",
            "Life does not always go as planned — and that's okay. Sometimes the unexpected detours lead to the most beautiful destinations."
        ],
        "Technology": [
            "Technology is changing everything so fast! Just discovered this amazing tool and I am genuinely blown away. Have you tried it yet?",
            "Spent the afternoon learning something new about AI and my mind is officially expanded. The future is wild and I am here for it!",
            "Gadget review time! Just picked up something new and I have THOUGHTS. Drop a comment if you want the full honest review."
        ],
        "Business": [
            "Small business update: We just hit a major milestone and I am so grateful for every single one of you who made this possible!",
            "Starting a business is the hardest and most rewarding thing I've ever done. Here's what I wish someone had told me on day one...",
            "To every small business owner out there: Keep going. The grind is real, but so is the reward. You've got this!"
        ],
        "Fashion": [
            "New outfit alert! This look came together so perfectly and I am obsessed. Would you wear this? Tell me in the comments!",
            "Thrift store haul! You would not believe how much I saved and how amazing these finds are. Sustainable fashion for the win!",
            "Confidence is the best accessory you can wear. Today I chose to dress for myself and it felt incredible. You should try it!"
        ],
        "Education": [
            "Currently reading the most eye-opening book and I genuinely cannot put it down. What's the last book that changed your perspective?",
            "Finished an online course today and I feel like a whole new person! Never stop learning, friends. The world has so much to teach us.",
            "Teachers are heroes and they don't get nearly enough credit. If a teacher changed your life, tag them today and let them know!"
        ],
        "Entertainment": [
            "Just finished that show everyone has been talking about and I have so many FEELINGS right now. No spoilers — but wow.",
            "Movie night! Grabbed the popcorn, turned off my phone, and had the most relaxing evening I've had in weeks. We all need this.",
            "Currently obsessed with this song on repeat all day. Drop your favorite track in the comments and let's build a playlist together!"
        ]
    },
    "X (Twitter)": {
        "Technology": [
            "Hot take: The best productivity tool is still a good night's sleep. No app can replace rest.",
            "AI won't take your job. Someone using AI better than you will. Time to level up.",
            "The best code is code you don't have to write. Keep it simple."
        ],
        "Motivation": [
            "You don't have to be great to start, but you have to start to be great. Go.",
            "Stop waiting for the perfect moment. The perfect moment is the one you create right now.",
            "Hard days build strong people. Keep going. The view from the top is worth every climb."
        ],
        "Business": [
            "Your brand is not what you say it is. It's what your customers say it is. Listen carefully.",
            "The best marketing is a product so good people tell their friends. Build that first.",
            "Discipline beats motivation every single time. Motivation fades. Discipline compounds."
        ],
        "Lifestyle": [
            "Protect your peace like it's the most valuable thing you own. Because it is.",
            "You are allowed to outgrow people, places, and old versions of yourself. That's growth.",
            "Comparison is the thief of joy. Run your own race at your own pace."
        ],
        "Travel": [
            "New city, new perspective. Travel really does rewire your brain in the best way.",
            "Reminder: Flights are cheaper than therapy and twice as effective. Book the trip.",
            "Every passport stamp is a chapter in a story worth telling. Keep collecting them."
        ],
        "Food": [
            "Food is culture. Food is memory. Food is love. Never underestimate a good meal.",
            "Whoever invented meal prep on Sundays is a genius and an absolute hero.",
            "The best conversations happen over food. Fact. Fight me."
        ],
        "Fitness": [
            "No one ever regretted a workout they actually did. Get moving.",
            "Your body keeps score. Take care of it like it's the only one you've got — because it is.",
            "Consistency over intensity. Every single time."
        ],
        "Fashion": [
            "Dress how you want to be addressed. First impressions still matter.",
            "Style is not about price tags. It's about knowing who you are.",
            "Confidence is the most timeless outfit. Never goes out of style."
        ],
        "Education": [
            "The more you learn, the more you earn — and the more you appreciate everything around you.",
            "Read for 30 minutes a day. In a year, that's 180+ hours of compounding knowledge.",
            "Curiosity is a superpower. Never let the world educate it out of you."
        ],
        "Entertainment": [
            "Current mood: main character energy. The plot is finally getting good.",
            "That mid-episode cliffhanger was absolutely criminal and I am not okay.",
            "Sometimes the greatest productivity hack is a 2-hour movie and a full reset."
        ]
    },
    "YouTube": {
        "Education": [
            "In this video I'm breaking down everything you need to know in the most straightforward way possible. No fluff, just pure value. Let's go!",
            "Whether you're a complete beginner or a seasoned pro, this tutorial has something for you. Drop your questions in the comments and I'll reply to every one!",
            "Today we're diving deep into something that changed my entire perspective — and I think it'll change yours too. Hit that subscribe button so you never miss an upload!"
        ],
        "Technology": [
            "I tested this for 30 days so you don't have to. Here's my honest, unbiased review — the good, the bad, and everything in between.",
            "This tool completely changed my workflow and I cannot stop talking about it. Watch till the end for an exclusive tip I haven't shared anywhere else.",
            "Deep dive time! I spent weeks researching this topic so I could bring you the most comprehensive breakdown on YouTube. Worth every minute."
        ],
        "Motivation": [
            "This video might be exactly what you needed to hear today. I'm sharing my raw, honest journey — the struggles, the wins, and everything that changed me.",
            "If you've been feeling stuck lately, this is your sign to watch this video all the way through. Something here will click.",
            "Real talk. No filters. Just me, the camera, and the truth about what it actually takes to build the life you want."
        ],
        "Travel": [
            "I traveled to this destination with no plan, no guide, and barely any budget — here's what actually happened. Spoiler: it was incredible.",
            "Complete travel guide to this city — where to eat, what to see, and what to absolutely avoid. Everything I wish I knew before I went.",
            "Vlog time! Join me for 24 hours exploring this stunning destination. This place completely exceeded every expectation I had."
        ],
        "Food": [
            "I tried making this viral recipe and the results were NOT what I expected. Watch the full reaction — this was a rollercoaster.",
            "Restaurant tour! I visited the most talked-about spots in this city to give you the definitive guide on where to actually eat.",
            "Cooking from scratch, no shortcuts, no cheats. This recipe is pure love and I'm walking you through every single step today."
        ],
        "Fitness": [
            "I followed this exact workout routine for 90 days and the transformation genuinely shocked me. Full breakdown with before and after in this video.",
            "No gym? No problem. This full-body home workout takes 20 minutes and will absolutely challenge you. No equipment needed — let's go!",
            "Fitness myths I believed for years — finally debunked. This video could save you months of wasted effort. Watch before your next workout."
        ],
        "Lifestyle": [
            "Morning routine reset! I completely overhauled my mornings and the difference in my productivity and energy has been life-changing. Here's exactly what I do.",
            "Minimalism changed my life and in this video I'm showing you exactly how I did it — practical steps, not just aesthetic goals.",
            "My honest monthly review. What worked, what didn't, and what I'm changing going forward. Full transparency — come along for the ride."
        ],
        "Business": [
            "From zero to my first $1,000 online — the complete honest story, including every mistake I made along the way. This video could save you months.",
            "I interviewed 10 successful entrepreneurs and asked them one question: what do you know now that you wish you knew at the start? The answers were gold.",
            "Business strategy breakdown! I'm walking through the exact framework I used to grow my brand, step by step. Take notes — this one's packed."
        ],
        "Fashion": [
            "Full wardrobe refresh under $100! I'll show you exactly how to build a stylish, versatile wardrobe without spending a fortune. Shop along with me!",
            "Get ready with me for the biggest event of the year! Full glam, outfit details, and all the behind-the-scenes chaos. It's giving main character energy.",
            "Style tips that will immediately elevate any outfit — zero effort, maximum impact. These are the game-changers I wish I knew sooner."
        ],
        "Entertainment": [
            "Okay, we need to talk about this. I just finished watching it and I have SO many thoughts. Full breakdown and reaction — buckle up.",
            "Top 10 list you didn't know you needed! I ranked them, I debated them, and I'm ready to defend every single choice. Fight me in the comments.",
            "Reacting to the most iconic moments of the year. My genuine, unscripted reactions — this one was an emotional rollercoaster from start to finish."
        ]
    }
}

DEMO_HASHTAGS = {
    "popular": ["#viral", "#trending", "#explore", "#foryou", "#fyp", "#instagood", "#love", "#follow"],
    "niche": {
        "Travel": ["#travelblogger", "#wanderlust", "#travelgram", "#backpacker", "#solotravel", "#travelphoto"],
        "Food": ["#foodie", "#foodphotography", "#instafood", "#foodlover", "#yummy", "#homecooking"],
        "Fitness": ["#fitnessmotivation", "#gym", "#workout", "#healthylifestyle", "#fitnessjourney", "#fitlife"],
        "Technology": ["#techlife", "#coding", "#developer", "#startup", "#innovation", "#ai"],
        "Business": ["#entrepreneur", "#smallbusiness", "#hustle", "#success", "#mindset", "#growthmindset"],
        "Motivation": ["#motivationalquotes", "#inspiration", "#mindset", "#positivity", "#goals", "#dailymotivation"],
        "Lifestyle": ["#lifestyle", "#dailylife", "#selfcare", "#wellness", "#gratitude", "#mindfulness"],
        "Fashion": ["#fashion", "#ootd", "#style", "#fashionista", "#outfitoftheday", "#streetstyle"],
        "Entertainment": ["#entertainment", "#fun", "#funny", "#comedy", "#viral", "#pop culture"],
        "Education": ["#education", "#learning", "#study", "#knowledge", "#teacher", "#elearning"],
        "General": ["#content", "#socialmedia", "#digital", "#creative", "#online", "#community"]
    },
    "general": ["#amazing", "#beautiful", "#happy", "#life", "#photooftheday", "#instagood", "#art", "#nature"]
}

LENGTH_INSTRUCTIONS = {
    "short": "Keep the caption very brief — under 100 characters, punchy and direct.",
    "medium": "Write a medium-length caption — around 150-200 characters, engaging and complete.",
    "long": "Write a detailed caption — 250-400 characters with storytelling, emojis, and a call to action."
}

# Hashtags to append to demo captions by category
CATEGORY_HASHTAGS = {
    "Travel": "#travel #wanderlust #adventure #explore #travelgram",
    "Food": "#food #foodie #instafood #yummy #homecooking",
    "Fitness": "#fitness #gym #workout #fitlife #healthylifestyle",
    "Technology": "#tech #technology #innovation #digital #coding",
    "Business": "#business #entrepreneur #success #hustle #leadership",
    "Motivation": "#motivation #inspiration #mindset #goals #positivity",
    "Lifestyle": "#lifestyle #selfcare #wellness #dailylife #gratitude",
    "Fashion": "#fashion #ootd #style #fashionista #outfitoftheday",
    "Entertainment": "#entertainment #fun #viral #trending #comedy",
    "Education": "#education #learning #knowledge #study #growth"
}


def generate_captions_ai(topic, platform, category, tone, length, keywords=""):
    """Generate 3 captions using Google Gemini API."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    length_instruction = LENGTH_INSTRUCTIONS.get(length, LENGTH_INSTRUCTIONS["medium"])
    keywords_part = f"Include these keywords naturally: {keywords}." if keywords else ""

    prompt = f"""You are an expert social media copywriter. Generate exactly 3 different and creative social media captions for the following request.

Platform: {platform}
Topic/Description: {topic}
Content Category: {category}
Tone: {tone}
{length_instruction}
{keywords_part}

Rules:
- Each caption must be unique in style and angle
- Include relevant emojis
- Each caption should end with 5-8 relevant hashtags
- Format your response EXACTLY as shown below, with no extra text:

CAPTION_1:
[caption text with emojis and hashtags]

CAPTION_2:
[caption text with emojis and hashtags]

CAPTION_3:
[caption text with emojis and hashtags]"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    return _parse_ai_captions(raw)


def _parse_ai_captions(raw_text):
    """Parse the AI response into a list of caption dicts."""
    captions = []
    pattern = r'CAPTION_\d+:\s*([\s\S]*?)(?=CAPTION_\d+:|$)'
    matches = re.findall(pattern, raw_text)

    for match in matches:
        text = match.strip()
        if text:
            hashtag_pattern = r'(#\w+)'
            hashtags = re.findall(hashtag_pattern, text)
            caption_text = re.sub(r'\s*#\w+', '', text).strip()
            captions.append({
                "text": caption_text,
                "hashtags": " ".join(hashtags)
            })

    while len(captions) < 3:
        captions.append({"text": raw_text.strip(), "hashtags": "#content #social"})

    return captions[:3]


def generate_captions_demo(topic, platform, category, tone, length):
    """Generate demo captions from templates — clearly labeled as sample content."""
    platform_captions = DEMO_CAPTIONS.get(platform, DEMO_CAPTIONS["Instagram"])
    category_captions = platform_captions.get(category, None)

    if category_captions is None:
        # Fallback: use Instagram captions for the category, then general pool
        ig_captions = DEMO_CAPTIONS["Instagram"].get(category, None)
        if ig_captions:
            category_captions = ig_captions
        else:
            all_caps = []
            for cats in DEMO_CAPTIONS["Instagram"].values():
                all_caps.extend(cats)
            category_captions = all_caps

    if len(category_captions) >= 3:
        selected = random.sample(category_captions, 3)
    else:
        selected = (category_captions * 3)[:3]

    tone_prefix = {
        "Funny": "😂 ",
        "Professional": "📌 ",
        "Inspirational": "✨ ",
        "Emotional": "💙 ",
        "Promotional": "🔥 ",
        "Educational": "📚 ",
        "Creative": "🎨 ",
        "Casual": "👋 "
    }.get(tone, "")

    default_hashtags = CATEGORY_HASHTAGS.get(category, "#content #socialmedia #digital")
    platform_tag = "#" + platform.lower().replace(" ", "").replace("(", "").replace(")", "")

    result = []
    for cap in selected:
        result.append({
            "text": tone_prefix + cap.strip(),
            "hashtags": default_hashtags + " " + platform_tag
        })

    return result


def generate_captions(topic, platform, category, tone, length, keywords=""):
    """Main entry point: use AI if available, else demo mode."""
    is_demo = DEMO_MODE
    try:
        if not is_demo:
            captions = generate_captions_ai(topic, platform, category, tone, length, keywords)
        else:
            captions = generate_captions_demo(topic, platform, category, tone, length)
    except Exception as e:
        print(f"AI generation failed: {e} - falling back to demo mode")
        captions = generate_captions_demo(topic, platform, category, tone, length)
        is_demo = True

    return captions, is_demo


def generate_hashtags(topic, category="General"):
    """Generate categorized hashtags for a topic."""
    is_demo = DEMO_MODE
    try:
        if not is_demo:
            hashtags = _generate_hashtags_ai(topic, category)
        else:
            hashtags = _generate_hashtags_demo(topic, category)
    except Exception as e:
        print(f"Hashtag AI generation failed: {e} - falling back to demo")
        hashtags = _generate_hashtags_demo(topic, category)
        is_demo = True

    return hashtags, is_demo


def _generate_hashtags_ai(topic, category):
    """Generate hashtags using Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""Generate hashtags for the following topic for social media use.

Topic: {topic}
Category: {category}

Provide hashtags in three tiers. Format EXACTLY as:

POPULAR:
#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5

NICHE:
#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5

GENERAL:
#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    return _parse_hashtag_response(raw)


def _parse_hashtag_response(raw):
    """Parse AI hashtag response."""
    result = {"popular": [], "niche": [], "general": []}
    sections = {"POPULAR": "popular", "NICHE": "niche", "GENERAL": "general"}

    for section_name, key in sections.items():
        pattern = rf'{section_name}:\s*([\s\S]*?)(?=POPULAR:|NICHE:|GENERAL:|$)'
        match = re.search(pattern, raw)
        if match:
            tags = re.findall(r'#\w+', match.group(1))
            result[key] = list(set(tags))

    return result


def _generate_hashtags_demo(topic, category):
    """Generate demo hashtags."""
    topic_words = topic.lower().split()[:3]
    custom_tags = [f"#{word}" for word in topic_words if len(word) > 2]

    niche_key = category if category in DEMO_HASHTAGS["niche"] else "General"
    niche_tags = DEMO_HASHTAGS["niche"][niche_key]
    general_tags = DEMO_HASHTAGS["general"]
    popular_tags = DEMO_HASHTAGS["popular"]

    return {
        "popular": list(set(popular_tags[:6] + custom_tags[:2])),
        "niche": list(set(niche_tags + custom_tags)),
        "general": list(set(general_tags[:6]))
    }
