# Nittany Connect — Campus Discovery Prototype

Nittany Connect is a Penn State-inspired, **offline-ready classroom design prototype** for discovering campus student organizations and events, making friends, and exploring clubs' social content.

## Run it

Download **index.html** and open it directly in Chrome. There are no servers, APIs, subscriptions, or build steps.

## Features

- Original navy-and-white design and desktop/mobile navigation
- Personalized For You feed and searchable Explore directory
- **My Schedule:** One shared Save action for clubs and events. Saved clubs appear as recurring meetings; saved future events appear on their actual date (or a clearly labeled fictional date for demo-only samples). If published times are missing, estimated demonstration times are labeled as such. Overlap warnings work for club/club, event/event, and club/event conflicts. Past events remain saved but are archived off the upcoming calendar.
- A 10-question onboarding survey plus adaptive follow-up questions about sports, music, arts, gaming/technology, outdoor interests, **food and culture**
- Rule-based match scores using broad and specific interests, goals, schedule preferences, event preferences, social comfort, and academic interests
- **Club Posts:** fictional Instagram-style concept feed with stories, likes, comments, and a demonstration post composer
- Add your own local photo or short video to a demo club post. Media is kept in the current browser's IndexedDB when supported; caption-only posts still work otherwise
- **Save** organizations or events, open details, and view fictional student connection requests. Previous favorites and interested-list choices migrate into Saved.
- Profile editing and a reset button for live demonstrations

## About the catalog

Includes **163 entries**: **127 organization listings and 36 event listings**. The total retains the original 112 records (80 requested clubs, 20 requested events, and 12 original samples), plus 41 additional organizations and 10 additional events linked to Penn State Discover where available.

Individual Penn State Discover pages were used for sourced entries. Unverified schedules and prices are labeled as such. Archived event dates are excluded from the Upcoming Events filter. This is a static snapshot, not a real-time listing service. Always check the official event or organization page before attending.

Club media feed posts and student profiles are fictional demo content and are not actual communications from Penn State organizations. Demo posts, reactions, survey answers and bookmarks stay in your browser.

## Class presentation walkthrough

1. Open the HTML file in Chrome.
2. Complete the onboarding survey, selecting Sports & Fitness and Music & Arts to see conditional follow-up questions.
3. Open **For You**, inspect calculated matches, and explore club details.
4. Save **Anime Organization** and **Gamers for Charity**, then open **Schedule**. Their fictional Thursday meeting times overlap and trigger an immediate conflict warning. Change one time to demonstrate resolution.
5. Open **Club Posts**, like/comment on a concept post, and click **Create demo post** to upload a photo or short video locally.
6. Browse **Explore** and use filters.
7. Go to **Profile** to edit preferences or **Reset demo**.

## No live AI backend

Event Radar and its scheduled AI research system have been intentionally removed. The envisioned automatic discovery/update process remains **a future concept only**.

This project is an educational, non-official prototype and is not affiliated with Penn State.
