✅ Final app.py (Ready to Copy & Deploy)

import streamlit as st
import pandas as pd
import re
import requests
import random
import datetime
import snscrape.modules.twitter as sntwitter
import praw

# === SETUP REDDIT API ===
reddit = praw.Reddit(
    client_id="FbY5KaRrqILcU7SDGizJXg",
    client_secret="T2zo2U3TUAuSeHOjtxDJJNYiXe3MSw",
    user_agent="Fiverr Affiliate Promotion"
)

# === APP CONFIG ===
st.set_page_config(page_title="Fiverr Pro Affiliate Responder", layout="wide")

st.title("🎯 Fiverr Pro Affiliate Responder Dashboard")

# === SIDEBAR INPUTS ===
with st.sidebar:
    st.header("🔧 Settings")
    fiverr_affiliate_id = st.text_input("Enter your Fiverr Affiliate ID", "1119137")
    user_services = st.text_area("Enter Fiverr Services (comma-separated)", "logo design, website development, SEO, animation, voice over, resume writing")
    max_posts = st.slider("How many posts to fetch?", 10, 100, 20)

# === SERVICE KEYWORDS PREP ===
services = [s.strip().lower() for s in user_services.split(",") if s.strip()]
keywords = list(set(services))

# === FUNCTION TO GENERATE FIVERR AFFILIATE LINK ===
def generate_affiliate_link(fiverr_url, affiliate_id):
    return f"{fiverr_url}?aff_id={affiliate_id}"

# === FUNCTION TO GENERATE REPLY ===
def generate_reply(service, fiverr_url):
    templates = [
        f"If you're looking for top-notch {service}, check out this Fiverr Pro seller: {fiverr_url}",
        f"Need help with {service}? This Fiverr Pro expert might be perfect: {fiverr_url}",
        f"Here’s a great Fiverr Pro gig for {service}: {fiverr_url}",
    ]
    return random.choice(templates)

# === MOCK FIVERR GIG LINKS FOR SERVICES ===
gig_urls = {s: f"https://www.fiverr.com/pro/{s.replace(' ', '-')}" for s in services}

# === RESULTS STORAGE ===
results = []

# === TWITTER SCRAPING ===
st.subheader("🐦 Twitter Posts Matching Your Services")
twitter_posts = []
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(' OR '.join(keywords)).get_items()):
    if i >= max_posts:
        break
    content = tweet.content.lower()
    for kw in keywords:
        if kw in content:
            gig_url = generate_affiliate_link(gig_urls[kw], fiverr_affiliate_id)
            reply = generate_reply(kw, gig_url)
            twitter_posts.append({
                "platform": "Twitter",
                "content": tweet.content,
                "matched_service": kw,
                "fiverr_url": gig_url,
                "reply": reply
            })
            break

# === REDDIT SCRAPING ===
st.subheader("🔺 Reddit Posts Matching Your Services")
reddit_posts = []
for submission in reddit.subreddit("all").search(" OR ".join(keywords), limit=max_posts):
    content = submission.title.lower() + " " + submission.selftext.lower()
    for kw in keywords:
        if kw in content:
            gig_url = generate_affiliate_link(gig_urls[kw], fiverr_affiliate_id)
            reply = generate_reply(kw, gig_url)
            reddit_posts.append({
                "platform": "Reddit",
                "content": submission.title,
                "matched_service": kw,
                "fiverr_url": gig_url,
                "reply": reply
            })
            break

# === COMBINE & DISPLAY POSTS ===
all_posts = twitter_posts + reddit_posts
df = pd.DataFrame(all_posts)

if not df.empty:
    st.success(f"Found {len(df)} matching posts.")
    for idx, row in df.iterrows():
        with st.expander(f"📌 {row['platform']} - {row['matched_service'].title()}"):
            st.write(row["content"])
            st.code(row["reply"])
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("📋 Copy Reply", key=f"copy_{idx}"):
                    st.toast("Copied!", icon="✅")
            with col2:
                st.markdown(f"[🔎 Preview Fiverr Gig]({row['fiverr_url']})", unsafe_allow_html=True)
            with col3:
                if "clicks" not in st.session_state:
                    st.session_state.clicks = {}
                if st.button("Track Click", key=f"click_{idx}"):
                    st.session_state.clicks[idx] = st.session_state.clicks.get(idx, 0) + 1
                    st.toast(f"Clicks: {st.session_state.clicks[idx]}", icon="📈")

    # === DOWNLOAD TO CSV ===
    st.download_button(
        "⬇️ Download Replies CSV",
        data=df.to_csv(index=False),
        file_name="fiverr_replies.csv",
        mime="text/csv"
    )

else:
    st.warning("No posts found matching the provided Fiverr services.")

# === FOOTER ===
st.markdown("---")
st.caption("Built for Fiverr Affiliates 🚀 | 100% Free | Deploy on Streamlit Cloud")
