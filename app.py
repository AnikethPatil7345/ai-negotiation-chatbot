import streamlit as st
import ollama

# Product details
PRODUCT = {
    "name": "Quantum Leap Laptop X1",
    "base_price": 2000.00,
    "features": ["16-inch Mini-LED Display", "64GB RAM", "2TB SSD Gen4", "Next-Gen CPU", "Advanced Cooling"],
    "min_discount": 0.05,
    "max_discount": 0.18,
    "max_rounds": 8
}

class NegotiationChatbot:
    def __init__(self):
        self.base_price = PRODUCT["base_price"]
        self.min_price = self.base_price * (1 - PRODUCT["max_discount"])
        self.current_offer = self.base_price
        self.rounds_left = PRODUCT["max_rounds"]
        self.history = []

    def generate_response(self, user_input):
        """Handles user negotiation inputs."""
        
        if self.rounds_left <= 0:
            return "I've made my final offer. No further negotiations."

        if user_input.isdigit():
            user_offer = float(user_input)

            if user_offer >= self.current_offer:
                return "Great! You've got a deal. We'll finalize your purchase now."

            if user_offer < self.min_price:
                return "Sorry, I can't go that low. Our lowest acceptable price is above that range."

            self.current_offer = (self.current_offer + user_offer) / 2
            self.rounds_left -= 1

            return f"I appreciate your offer! I can lower the price to ${self.current_offer:.2f}. What do you think?"

        else:
            return self.ask_llm(user_input)

    def ask_llm(self, message):
        """Sends structured negotiation history to the AI for a coherent response."""
        
        chat_history = [
            {"role": "system", "content": f"""
            You are an AI salesperson negotiating the price of {PRODUCT['name']}.
            - **Base Price:** ${PRODUCT['base_price']:.2f}
            - **Minimum Acceptable Price:** ${self.min_price:.2f}
            - **Current Offer:** ${self.current_offer:.2f}
            - **Max Discount:** {PRODUCT['max_discount']*100}%
            - **Rounds Left:** {self.rounds_left}

            **Negotiation Rules:**
            - Accept if the customer offers **>= current offer**.
            - Reject if the offer is **< minimum price**.
            - Otherwise, counter-offer closer to the user's price.
            - If no rounds left, state final price and refuse further negotiation.

            Stay professional, persuasive, and on-topic.
            """},
            {"role": "user", "content": message}
        ]

        response = ollama.chat(model="llama3", messages=chat_history)  # Use a structured LLM
        return response['message']['content']

bot = NegotiationChatbot()

# Streamlit UI
st.title("💬 AI-Powered Negotiation Chatbot")
st.sidebar.write(f"**Product:** {PRODUCT['name']}")
st.sidebar.write(f"**Base Price:** ${PRODUCT['base_price']:.2f}")
st.sidebar.write(f"**Max Discount:** {PRODUCT['max_discount']*100}%")
st.sidebar.write(f"**Minimum Price:** ${bot.min_price:.2f}")
st.sidebar.write(f"**Rounds Remaining:** {bot.rounds_left}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    st.write(chat)

user_input = st.text_input("Enter your negotiation offer or question:")

if user_input:
    response = bot.generate_response(user_input)
    st.session_state.chat_history.append(f"You: {user_input}")
    st.session_state.chat_history.append(f"AI: {response}")
    st.write(f"AI: {response}") 
