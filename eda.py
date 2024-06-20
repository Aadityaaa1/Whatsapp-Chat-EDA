import streamlit as st
from collections2 import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from whatstk import WhatsAppChat
from whatstk import FigureBuilder
import pandas as pd
import io


# Function to generate and save plots
def generate_plots(chat):
    # Create a folder to save the images
    import os
    if not os.path.exists('images'):
        os.makedirs('images')

    init_date = chat.df.date.min()
    end_date = chat.df.date.max()

    # Number of messages sent
    message_counts = chat.df.groupby('username').agg(num_messages=('message', 'count'))
    # Words to exclude from the top 20
    exclude_words = [':','am', '-', 'omitted>',  '<Media', 'and', 'a', 'you', 'I', 'to', 'the', 'i']

    # Top 10 most used words (excluding specific words)
    all_messages = ' '.join(chat.df['message'].dropna().astype(str))
    words_counter = Counter(all_messages.split())

    # Remove excluded words
    for word in exclude_words:
        if word in words_counter:
            del words_counter[word]

    top_15_words = dict(words_counter.most_common(15))

    # Plotting WordCloud for the top 10 words
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(top_15_words)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Top 15 Most Used Words')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="top_10_words.png", mime="image/png")
    buffer.close()

    # Additional code for user interventions count
    fb = FigureBuilder(chat=chat)
    fig = fb.user_interventions_count_linechart(cumulative=True, title='User Text Count')
    fig_data = fig.to_image(format="png")
    st.image(fig_data)
    st.download_button(label="Download", data=fig_data,
                       file_name="user_text_count_cumulative.png", mime="image/png")

    # Number of characters sent
    fig1 = fb.user_interventions_count_linechart(cumulative=True, msg_length=True,
                                                 title='Count of Sent Characters')
    fig1_data = fig1.to_image(format="png")
    st.image(fig1_data)
    st.download_button(label="Download", data=fig1_data,
                       file_name="user_text_count_cumulative_characters.png", mime="image/png")

    fig2 = fb.user_msg_length_boxplot()
    fig2_data = fig2.to_image(format="png")
    st.image(fig2_data)
    st.download_button(label="Download", data=fig2_data,
                       file_name="user_msg_length_boxplot.png", mime="image/png")

    labels = message_counts.index
    sizes = message_counts['num_messages']
    colors = plt.cm.Paired(range(len(labels)))

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title('Distribution of Texts Sent by Each Person')
    plt.tight_layout()  # Adjust layout
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="distribution_texts.png",
                       mime="image/png")
    buffer.close()

    # Extracting day of the week, month, and hour information
    chat.df['day_of_week'] = chat.df['date'].dt.day_name()
    chat.df['month'] = chat.df['date'].dt.month_name()

    # Bar chart for messages sent on different days of the week
    plt.figure(figsize=(12, 5))
    custom_day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week_counts = chat.df['day_of_week'].value_counts().sort_index()
    sorted_data1 = day_of_week_counts[custom_day_order]
    sorted_data1.plot(kind='bar', color='red')
    plt.title('Messages Sent on Different Days of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Messages')
    plt.xticks(rotation=45, ha='right')  # Rotate labels
    plt.tight_layout()  # Adjust layout
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="messages_per_day.png",
                       mime="image/png")
    buffer.close()

    # Extract month from the timestamp
    chat.df['month'] = chat.df['date'].dt.month_name()

    # Create a Categorical data type with custom order
    custom_month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October', 'November', 'December'][::-1]
    custom_month_cat = pd.Categorical(chat.df['month'], categories=custom_month_order, ordered=True)

    # Calculate the total number of messages sent in each month
    month_counts = custom_month_cat.value_counts().sort_index(ascending=False)

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    month_counts.plot(kind='bar', color='skyblue')
    plt.title('Total Messages Sent in Each Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Messages')
    plt.xticks(rotation=45, ha='right')  # Rotate labels
    plt.tight_layout()  # Adjust layout
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="messages_per_month.png",
                       mime="image/png")
    buffer.close()

    # Calculate the time difference between consecutive messages for each participant
    chat.df['time_diff'] = chat.df.groupby('username')['date'].diff()

    # Extract the response time in seconds
    chat.df['response_time_seconds'] = chat.df['time_diff'].dt.total_seconds()

    # Calculate the average response time for each participant
    average_response_time = chat.df.groupby('username')['response_time_seconds'].mean()

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    average_response_time.sort_values().plot(kind='bar', color='lightblue')
    plt.title('Average Response Time for Each Participant')
    plt.xlabel('Participant')
    plt.ylabel('Average Response Time (seconds)')
    plt.xticks(rotation=45, ha='right')  # Rotate labels
    plt.tight_layout()  # Adjust layout
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="avg_response_time.png",
                       mime="image/png")
    buffer.close()

    # Calculate the time difference between consecutive messages for each participant
    chat.df['time_diff'] = chat.df.groupby('username')['date'].diff()

    # Set a threshold for inactivity (e.g., 1 hour)
    inactivity_threshold = pd.Timedelta(hours=4)

    # Identify conversations started by each participant
    chat.df['conversation_started'] = (chat.df['time_diff'] > inactivity_threshold) | chat.df['time_diff'].isnull()

    # Count the number of conversations started by each participant
    conversations_started_count = chat.df.groupby('username')['conversation_started'].sum()

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    conversations_started_count.sort_values().plot(kind='bar', color='orange')
    plt.title('Number of Conversations Started by Each Participant')
    plt.xlabel('Participant')
    plt.ylabel('Number of Conversations Started')
    plt.xticks(rotation=45, ha='right')  # Rotate labels
    plt.tight_layout()  # Adjust layout
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.image(buffer)
    st.download_button(label="Download", data=buffer, file_name="conversations_started.png",
                       mime="image/png")
    buffer.close()

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
    }
    </style>
    <h1 class="centered-title">WhatsApp Chat Analysis</h1>
    """,
    unsafe_allow_html=True
)
# Tabs for navigation
tabs = st.tabs(["Instructions", "Analysis"])

with tabs[0]:
    st.header("Instructions on How to Get the WhatsApp Chat Text File")
    st.write("Follow the steps below to export your WhatsApp chat:")

    st.write("1. Open the WhatsApp chat you want to export.")

    st.write("2. Tap on the three dots at the top right corner and select 'More'.")

    st.write("3. Select 'Export Chat' from the menu.")

    st.write("4. Choose whether to include media or not, and select the method to share (e.g., email).")

    st.write("5. Save the exported chat file to your computer.")

    st.write("6. Upload the exported .txt file using the uploader below in the Analysis tab.")

with tabs[1]:
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Save uploaded file
        with open("uploaded_file.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load and process the chat
        chat = WhatsAppChat.from_source(filepath="uploaded_file.txt")
        generate_plots(chat)
