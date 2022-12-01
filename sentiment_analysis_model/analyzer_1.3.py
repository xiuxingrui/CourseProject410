# Description: Function used to running sentiment analysis for new reviews
# Created by Rui Mao at 2022-11-29
# Reference: https://www.nltk.org ;https://www.cs.cornell.edu/people/pabo/movie-review-data/ ;
# https://medium.com/@joel_34096/sentiment-analysis-of-movie-reviews-in-nltk-python-4af4b76a6f3 ;
# https://joblib.readthedocs.io/en/latest/


import nltk
import joblib
import ast
from nltk.sentiment import SentimentIntensityAnalyzer


def analyzer(threshold):
    """
    The analyzer used to perform sentiment analysis.

    :param threshold: reviews longer than threshold will be processed by pretrained bigram model, otherwise by NLTK VADER
    :Output: Review Statistics
    """

    vader = SentimentIntensityAnalyzer()
    short_review_list = []
    reviews_list = []  # [['This','is','review','one'],['This','is','review','two']]
    review_threshold = threshold
    vader_pos_counter = 0
    vader_neg_counter = 0
    max_pos_score = 0
    max_neg_score = 0
    neu = 0

    stopwords = nltk.corpus.stopwords.words("english")
    stopwords.extend([word.lower() for word in nltk.corpus.names.words()])

    print("Start Sentiment Analysis...")
    try:
        with open("MNB_Bigram_features.txt","r") as feature_file:
            content = feature_file.read().splitlines()
    except:
        print("Can't find the file.")


    features = ast.literal_eval(content[0])

    try:
        reviews_file = open("reviews.txt", 'r')
        fetched_reviews = reviews_file.readlines()
    except:
        print("fetching reviews, please wait")


    for review in fetched_reviews:
        res = review.split()
        if len(res) < review_threshold:
            short_review_list.append(res)
            score = vader.polarity_scores(' '.join(res))

            if score['pos'] > max_pos_score:
                max_pos_score = score['pos']
                most_pos_short_review = ' '.join(res)
            if score['neg'] > max_neg_score:
                max_neg_score = score['neg']
                most_neg_short_review = ' '.join(res)

            if score['pos'] == score['neg']:
                vader_pos_counter += 0
                vader_neg_counter += 0
                neu += 1
            elif score['pos'] > score['neg']:
                vader_pos_counter += 1
            else:
                vader_neg_counter += 1

        else:
            reviews_list.append(res)


    try:  # creating feature map for all reviews
        all_feature_map = []
        for review in reviews_list:


            bigram = nltk.collocations.BigramCollocationFinder.from_words(word for word in review if word not in stopwords)
            feature_map = {}
            for feature in features:
                label = feature in bigram.ngram_fd  # label is either True or False
                feature_map[feature] = label
            all_feature_map.append(feature_map)

        print("Feature map created successfully.")
    except:
        print("Failed to create feature map")

    model = joblib.load('MultinomialNB.pkl')

    # make mass predictions
    prediction = model.classify_many(all_feature_map)
    bi_pos_counter = prediction.count('pos')
    bi_neg_counter = prediction.count('neg')

    total_pos = vader_pos_counter + bi_pos_counter
    total_neg = vader_neg_counter + bi_neg_counter
    total = total_neg + total_pos

    print("Finish Sentiment Analysis.")
    print("Total Anylyzed Reviews:", total + neu,
          "Positive Reviews:", total_pos,
          "Negative Reviews:", total_neg, sep='\n')

    if total_pos > total_neg:
        print("Overall: Positive")
    else:
        print("Overall: Negtive")

    print("Max Positive Score:", max_pos_score,
            "Most Positive Short Reviews: ", most_pos_short_review,
            "Max Negtive Score:", max_neg_score,
            "Most Negative Short Reviews: ", most_neg_short_review, sep="\n")


if __name__ == "__main__":
    review_threshold = 200 # reviews longer than 200 words will be processed by bigram model, otherwise by vader
    analyzer(review_threshold)


