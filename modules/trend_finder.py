"""
Trend Finder Module
Pinterest trending topics + Google Trends se popular recipe topics dhundta hai
"""

import json
import time
import random
import requests
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from bs4 import BeautifulSoup


class TrendFinder:
    def __init__(self, config: dict, context: dict):
        self.config = config
        self.context = context
        self.niche = config.get("niche", "Recipes & Meal Planning")
        
        self.used_topics = []
        if self.context and "published_posts" in self.context:
            self.used_topics = [post.get("topic", "") for post in self.context["published_posts"].values()]

        # Recipe niche ke liye seed keywords
        self.seed_keywords = [
            "easy weeknight dinners",
            "meal prep ideas for the week",
            "healthy breakfast recipes",
            "quick air fryer recipes",
            "one pan dinner ideas",
            "vegetarian dinner recipes",
            "high protein meals",
            "easy dessert recipes 5 ingredients",
            "summer appetizer boards",
            "comfort food recipes",
            "keto dinner ideas",
            "gluten free baking recipes",
            "best pasta recipes",
            "slow cooker dump meals",
            "kid friendly dinner ideas"
        ]

    def get_google_trends(self, num_topics=20) -> list:
        """Google Trends se trending recipe topics fetch karo"""
        print("📊 Google Trends se topics fetch kar raha hoon...")
        trending_topics = []

        try:
            pytrends = TrendReq(hl='en-US', tz=360)

            # Daily trending searches fetch karo
            try:
                trending_searches = pytrends.trending_searches(pn='united_states')
                daily_trends = trending_searches[0].tolist()[:10]
                trending_topics.extend(daily_trends)
                print(f"   ✅ Google daily trends: {len(daily_trends)} topics mila")
            except Exception as e:
                print(f"   ⚠️ Daily trends error: {e}")

            # Recipe related interest over time check karo
            recipe_related = []
            for keyword in random.sample(self.seed_keywords, min(5, len(self.seed_keywords))):
                try:
                    pytrends.build_payload([keyword], cat=71, timeframe='now 7-d', geo='US') # cat=71 is Food & Drink
                    related = pytrends.related_queries()
                    if keyword in related and related[keyword]['top'] is not None:
                        top_queries = related[keyword]['top']['query'].tolist()[:5]
                        recipe_related.extend(top_queries)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"   ⚠️ Related queries error for '{keyword}': {e}")
                    continue

            trending_topics.extend(recipe_related)
            print(f"   ✅ Google related queries: {len(recipe_related)} topics mila")

        except Exception as e:
            print(f"   ❌ Google Trends error: {e}")

        # Fallback: pre-defined high-traffic topics
        fallback_topics = self._get_fallback_topics()
        trending_topics.extend(fallback_topics)

        # Filter aur deduplicate
        unique_topics = list(set([t.strip().lower() for t in trending_topics if len(t) > 3]))
        print(f"   ✅ Total unique topics: {len(unique_topics)}")

        return unique_topics[:num_topics]

    def get_pinterest_trending_categories(self) -> list:
        """Pinterest ke popular recipe categories scrape karo"""
        print("📌 Pinterest se trending categories fetch kar raha hoon...")
        topics = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # Pinterest trending URLs for recipe/food category
        pinterest_urls = [
            "https://www.pinterest.com/ideas/food-and-drink/918530398158/",
            "https://www.pinterest.com/ideas/dinner-recipes/928091702434/",
        ]

        for url in pinterest_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')

                    # Title tags se topics extract karo
                    titles = soup.find_all(['h1', 'h2', 'h3', 'h4'], limit=30)
                    for title in titles:
                        text = title.get_text(strip=True)
                        if 5 < len(text) < 100:
                            topics.append(text)

                    print(f"   ✅ Pinterest se {len(topics)} topics mila")
                else:
                    print(f"   ⚠️ Pinterest status: {response.status_code}")
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ Pinterest scraping error: {e}")

        return topics

    def _get_fallback_topics(self) -> list:
        """Agar APIs fail ho jain toh yeh evergreen topics use karo"""
        evergreen_recipe_topics = [
            "15 Easy Weeknight Dinners Ready in 30 Minutes",
            "The Ultimate Sunday Meal Prep Guide for Beginners",
            "10 High-Protein Breakfast Ideas to Keep You Full",
            "The Best Crispy Air Fryer Chicken Recipe",
            "One-Pan Lemon Butter Garlic Salmon",
            "Comforting Homemade Chicken Noodle Soup",
            "5-Ingredient No-Bake Peanut Butter Desserts",
            "How to Build the Perfect Summer Charcuterie Board",
            "Delicious Vegetarian Dinners Even Meat Eaters Will Love",
            "The Secret to the Fluffiest Pancakes Every Time",
            "Slow Cooker Beef Stew for Cold Winter Nights",
            "Keto-Friendly Cauliflower Crust Pizza",
            "10 Easy Pasta Recipes for Busy Evenings",
            "Healthy Smoothie Recipes for Glowing Skin",
            "Kid-Approved Macaroni and Cheese From Scratch"
        ]
        return evergreen_recipe_topics

    def select_best_topic(self, num_topics=2) -> list:
        """
        Sab sources se topics collect karo aur best select karo
        Already used topics exclude karo
        """
        print("\n🔍 Best topics select kar raha hoon...")

        all_topics = []

        # Google Trends se
        google_topics = self.get_google_trends()
        all_topics.extend(google_topics)

        # Pinterest se
        pinterest_topics = self.get_pinterest_trending_categories()
        all_topics.extend(pinterest_topics)

        # Fallback topics
        fallback = self._get_fallback_topics()
        all_topics.extend(fallback)

        # Already published topics remove karo
        fresh_topics = []
        for topic in all_topics:
            topic_lower = topic.lower()
            already_used = any(
                used.lower() in topic_lower or topic_lower in used.lower()
                for used in self.used_topics
            )
            if not already_used and len(topic) > 10:
                fresh_topics.append(topic)

        if not fresh_topics:
            print("   ⚠️ Saare topics use ho gaye, fallback use kar raha hoon")
            fresh_topics = self._get_fallback_topics()

        # Random shuffle aur select karo
        random.shuffle(fresh_topics)
        selected = fresh_topics[:num_topics]

        print(f"   ✅ Selected topics: {selected}")
        return selected


if __name__ == "__main__":
    # Test karo
    with open("config.json") as f:
        config = json.load(f)
    with open("project_context.json") as f:
        context = json.load(f)

    finder = TrendFinder(config, context)
    topics = finder.select_best_topic(2)
    print(f"\n🎯 Final Topics:\n{topics}")
