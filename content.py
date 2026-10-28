"""
Static content for AyurBot: prakriti descriptions, diet plans, the 15-question
quiz and the rule-based follow-up chatbot. (Unchanged from the original app.)
"""

# ─── Constants ────────────────────────────────────────────────────────────────
PRAKRITI_LABELS = ["Vata", "Pitta", "Kapha"]

PRAKRITI_INFO = {
    "Vata": {
        "emoji": "🌬️",
        "element": "Air & Space",
        "color": "#8B7FD4",
        "traits": "Creative, enthusiastic, quick-thinking, light, flexible",
        "qualities": "Dry, light, cold, rough, mobile, subtle",
        "description": (
            "Vata types are energetic and creative with quick minds. "
            "They tend to be slender, move fast, and think fast — but can become "
            "anxious or scattered when out of balance."
        ),
    },
    "Pitta": {
        "emoji": "🔥",
        "element": "Fire & Water",
        "color": "#E07B54",
        "traits": "Focused, determined, intelligent, organized, confident",
        "qualities": "Hot, sharp, light, oily, mobile, liquid",
        "description": (
            "Pitta types are natural leaders with sharp intellects and strong "
            "digestion. They are goal-oriented and passionate, but can become "
            "irritable or inflammatory when imbalanced."
        ),
    },
    "Kapha": {
        "emoji": "🌊",
        "element": "Earth & Water",
        "color": "#5B9E6E",
        "traits": "Calm, loving, patient, loyal, strong, nurturing",
        "qualities": "Heavy, slow, cold, oily, smooth, dense",
        "description": (
            "Kapha types are grounded, stable and nurturing with excellent stamina. "
            "They are loyal and compassionate, but can become lethargic or resistant "
            "to change when out of balance."
        ),
    },
}

DIET_SUGGESTIONS = {
    "Vata": {
        "principle": "Warm, moist, nourishing, and grounding foods",
        "favor": [
            "🍚 Warm cooked grains — rice, oatmeal, wheat",
            "🥣 Soups and stews with ghee or olive oil",
            "🧄 Root vegetables — carrots, beets, sweet potatoes",
            "🥛 Warm milk with turmeric and honey",
            "🫚 Healthy fats — avocado, sesame oil, ghee",
            "🍯 Sweet, sour, and salty tastes",
            "🌰 Soaked nuts — almonds, cashews, walnuts",
            "🍌 Sweet ripe fruits — bananas, mangoes, dates",
        ],
        "avoid": [
            "🧊 Cold, raw, or dry foods",
            "🥤 Carbonated and iced drinks",
            "🫘 Raw salads and beans (can cause gas)",
            "☕ Excess caffeine and alcohol",
            "🍿 Dry snacks — crackers, chips, popcorn",
        ],
        "meal_tips": [
            "🕗 Eat at regular, consistent times",
            "🍽️ Eat three warm meals a day",
            "🌡️ Favor warm beverages — herbal teas, warm water",
            "🧘 Eat in a calm, settled environment",
            "🥄 Add warming spices: ginger, cinnamon, cardamom, cumin",
        ],
        "herbs": "Ashwagandha, Shatavari, Triphala, Ginger, Licorice",
    },
    "Pitta": {
        "principle": "Cool, fresh, and moderately heavy foods",
        "favor": [
            "🥗 Fresh salads with cooling vegetables",
            "🥒 Cucumber, zucchini, leafy greens",
            "🍎 Sweet fruits — apples, pears, grapes, pomegranate",
            "🌾 Barley, oats, basmati rice",
            "🧀 Cooling dairy — milk, ghee, coconut milk",
            "🫛 Legumes — mung beans, lentils, chickpeas",
            "🌿 Sweet, bitter, and astringent tastes",
            "🥥 Coconut water and coconut oil",
        ],
        "avoid": [
            "🌶️ Spicy and pungent foods — chillies, hot peppers",
            "🍟 Fried and oily foods",
            "☕ Excess caffeine, alcohol, and sour drinks",
            "🍋 Fermented, sour foods — vinegar, pickles",
            "🍔 Red meat and heavy proteins",
        ],
        "meal_tips": [
            "🌙 Don't skip meals — Pitta hunger is intense",
            "❄️ Allow food to cool slightly before eating",
            "🌿 Add cooling herbs: coriander, fennel, mint, turmeric",
            "😌 Eat without rushing or multitasking",
            "🥤 Drink room-temperature or cool water, not ice cold",
        ],
        "herbs": "Brahmi, Amalaki, Neem, Coriander, Shatavari",
    },
    "Kapha": {
        "principle": "Light, warm, dry, and stimulating foods",
        "favor": [
            "🌶️ Spicy and pungent foods to stoke digestion",
            "🥬 Light leafy greens — spinach, kale, arugula",
            "🍎 Light fruits — apples, pears, pomegranate, berries",
            "🌾 Light grains — barley, millet, buckwheat, rye",
            "🫛 Legumes — all beans and lentils",
            "🧅 Pungent vegetables — onions, radishes, leeks",
            "🍯 Pungent, bitter, and astringent tastes",
            "☕ Warming herbal teas — ginger, black pepper, tulsi",
        ],
        "avoid": [
            "🍰 Heavy, sweet, and oily foods",
            "🥛 Excess dairy — cheese, yogurt, ice cream",
            "🍝 Refined carbs — white bread, pasta, pastries",
            "🍬 Sugar and sugary drinks",
            "🥩 Heavy meats and fatty foods",
        ],
        "meal_tips": [
            "🌅 Eat largest meal at midday when digestion is strongest",
            "🚶 Light exercise before meals to stimulate appetite",
            "🧂 Use pungent spices freely: black pepper, ginger, mustard",
            "🍽️ Eat two meals daily — avoid frequent snacking",
            "🌡️ Favor warm, lightly cooked, and dry preparations",
        ],
        "herbs": "Trikatu, Guggulu, Triphala, Punarnava, Tulsi",
    },
}

# ─── Questions ────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "key": "body_frame",
        "text": "🏃 How would you describe your body frame?",
        "options": [
            "Slim, light, hard to gain weight",
            "Medium, muscular, athletic build",
            "Large, heavy, easy to gain weight",
        ],
    },
    {
        "key": "skin_type",
        "text": "✋ What is your skin type like?",
        "options": [
            "Dry, rough, or flaky skin",
            "Oily, sensitive, prone to rashes or redness",
            "Thick, smooth, well-moisturized",
        ],
    },
    {
        "key": "hair_type",
        "text": "💇 How would you describe your hair?",
        "options": [
            "Dry, frizzy, thin, or coarse",
            "Fine, straight, early greying or thinning",
            "Thick, wavy, lustrous, and oily",
        ],
    },
    {
        "key": "appetite",
        "text": "🍽️ How is your appetite?",
        "options": [
            "Variable — sometimes hungry, sometimes not",
            "Strong and sharp — very irritable when hungry",
            "Slow and steady — can skip meals easily",
        ],
    },
    {
        "key": "digestion",
        "text": "🫃 How is your digestion typically?",
        "options": [
            "Irregular — prone to gas, bloating, constipation",
            "Quick and strong — prone to acidity or heartburn",
            "Slow and sluggish — feel heavy after meals",
        ],
    },
    {
        "key": "sleep_pattern",
        "text": "😴 Describe your typical sleep:",
        "options": [
            "Light, interrupted, hard to fall asleep (6–7 hrs)",
            "Moderate and sound (7–8 hrs)",
            "Deep, long, and heavy — hard to wake up (8–10 hrs)",
        ],
    },
    {
        "key": "energy_level",
        "text": "⚡ What is your energy level like?",
        "options": [
            "Comes in bursts — high then crashes",
            "Intense and focused but can burn out",
            "Steady and enduring through the day",
        ],
    },
    {
        "key": "temperament",
        "text": "🧠 How would you describe your temperament?",
        "options": [
            "Creative, enthusiastic, but anxious or scattered",
            "Ambitious, decisive, but can get irritable or critical",
            "Calm, patient, and loving but can be stubborn",
        ],
    },
    {
        "key": "memory",
        "text": "🧩 How is your memory?",
        "options": [
            "Quick to grasp but quick to forget",
            "Sharp, clear, and precise",
            "Slow to learn but retains for long",
        ],
    },
    {
        "key": "speech",
        "text": "💬 How do you typically speak?",
        "options": [
            "Fast, talkative, jump from topic to topic",
            "Precise, direct, sharp, and articulate",
            "Slow, measured, melodious, sometimes silent",
        ],
    },
    {
        "key": "weather_preference",
        "text": "🌤️ What weather do you prefer?",
        "options": [
            "Warm and humid — dislike cold and wind",
            "Cool — dislike heat, sun, and hot weather",
            "Warm and dry — dislike cold, damp, and cloudy days",
        ],
    },
    {
        "key": "thirst",
        "text": "💧 How is your thirst?",
        "options": [
            "Variable — sometimes forget to drink water",
            "Excessive — always thirsty",
            "Low — rarely feel thirsty",
        ],
    },
    {
        "key": "sweat",
        "text": " How much do you sweat?",
        "options": [
            "Minimal sweating",
            "Profuse sweating, often with strong odour",
            "Moderate sweating",
        ],
    },
    {
        "key": "joints",
        "text": "🦴 How are your joints?",
        "options": [
            "Prominent, cracking, or popping joints",
            "Flexible and medium-sized",
            "Large, well-padded, stable joints",
        ],
    },
    {
        "key": "weight_tendency",
        "text": "⚖️ What is your weight tendency ?",
        "options": [
            "Hard to gain weight, lose it quickly",
            "Moderate — gain and lose with relative ease",
            "Easy to gain weight, very hard to lose it",
        ],
    },
]


# ─── Simple rule-based chatbot ────────────────────────────────────────────────
def chatbot_respond(question, prakriti, info, diet):
    q = question.lower()

    if any(w in q for w in ["what is", "explain", "tell me", "about", "meaning", "prakriti"]):
        return (
            f"**{prakriti} Prakriti** is governed by the {info['element']} elements. 🌿\n\n"
            f"{info['description']}\n\n"
            f"**Key traits:** {info['traits']}"
        )
    elif any(w in q for w in ["eat", "food", "diet", "meal", "nutrition"]):
        favour_str = "\n".join(diet["favor"][:5])
        return (
            f"For **{prakriti}** types, the key principle is: *{diet['principle']}*\n\n"
            f"**Top foods to favour:**\n{favour_str}\n\n"
            f"Would you like tips on what to avoid or meal timing?"
        )
    elif any(w in q for w in ["avoid", "don't", "bad", "harmful", "wrong"]):
        avoid_str = "\n".join(diet["avoid"])
        return (
            f"**{prakriti}** types should try to avoid:\n\n{avoid_str}\n\n"
            f"These can aggravate your dosha and lead to imbalance. 🙏"
        )
    elif any(w in q for w in ["tip", "advice", "suggestion", "meal", "time", "when"]):
        tips_str = "\n".join(diet["meal_tips"])
        return f"**Meal tips for {prakriti}:**\n\n{tips_str}"
    elif any(w in q for w in ["herb", "supplement", "plant", "medicine"]):
        return (
            f"Recommended herbs for **{prakriti}** Prakriti:\n\n"
            f"🌿 **{diet['herbs']}**\n\n"
            f"These herbs help balance your dominant dosha. Always consult an Ayurvedic practitioner before starting any supplement."
        )
    elif any(w in q for w in ["vata", "pitta", "kapha", "dosha", "three"]):
        return (
            "The three Doshas in Ayurveda are:\n\n"
            "🌬️ Vata — Air & Space — governs movement and communication \n\n"
            "🔥 Pitta — Fire & Water — governs transformation and metabolism\n\n"
            "🌊 Kapha— Earth & Water — governs structure and lubrication\n\n"
            f"Your dominant dosha is **{prakriti}** {info['emoji']}"
        )
    elif any(w in q for w in ["balance", "imbalance", "fix", "heal", "help"]):
        return (
            f"To keep your **{prakriti}** dosha in balance:\n\n"
            f"• Follow the diet recommendations above\n"
            f"• Maintain regular daily routines (*Dinacharya*)\n"
            f"• Get adequate sleep and avoid stress\n"
            f"• Use the herbs: {diet['herbs']}\n"
            f"• Consider consulting an Ayurvedic practitioner for a personalised plan 🙏"
        )
    elif any(w in q for w in ["exercise", "workout", "yoga", "activity"]):
        ex = {
            "Vata": "Gentle, grounding exercises — yoga, walking, tai chi, swimming. Avoid exhausting high-intensity workouts.",
            "Pitta": "Moderate, cooling exercises — swimming, cycling, hiking in cool weather. Avoid overheating and excessive competition.",
            "Kapha": "Vigorous, stimulating exercises — running, aerobics, weight training, HIIT. Kapha benefits most from intense activity!",
        }
        return f"Exercise for {prakriti} Prakriti:\n\n🏃 {ex[prakriti]}"
    elif any(w in q for w in ["sleep", "rest", "bedtime", "wake"]):
        sl = {
            "Vata": "Aim for 7–8 hours. Go to bed by 10 PM. Create a calming bedtime routine — warm milk, light reading.",
            "Pitta": "Aim for 7–8 hours. Avoid working late. Cool the bedroom and avoid stimulating content before bed.",
            "Kapha": "Limit to 7–8 hours maximum. Avoid oversleeping — it increases Kapha. Wake up by 6 AM ideally.",
        }
        return f"Sleep tips for {prakriti}:\n\n😴 {sl[prakriti]}"
    else:
        return (
            f"Great question! As a **{prakriti}** type, everything in Ayurveda is personalised to your constitution.\n\n"
            f"You can ask me about:\n"
            f"• 🥗 Diet and foods to eat or avoid\n"
            f"• 🌿 Herbs and supplements\n"
            f"• 🏃 Best exercises for your type\n"
            f"• 😴 Sleep recommendations\n"
            f"• ⚖️ Balancing your dosha\n\n"
            f"What would you like to know? 🙏"
        )
