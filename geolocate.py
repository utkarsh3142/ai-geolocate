import sys
import string
from itertools import groupby
from heapq import nlargest

# Trainer function to read the training file and calculate frequencies asscociated with each city and word

def trainer(file):
    # Dictionaries to store frequency of each city(city_freq) and frequency of each word by city(city_words).
    # city_words is a 2 level dictionary with structure { city : { word : frequeny } }
    city_words = {}
    city_freq = {}

    with open(train_file) as file:
        for line in file.readlines():

            # Initialize city_words to {} using setfefault function
            city_words.setdefault(line.split()[0],{})

            # Add 1 to the current frequency of a city, initialized to 0
            city_freq[line.split()[0]] = city_freq.setdefault(line.split()[0], 0) + 1

            for word in cleaner(line.split()[1:]):

                # Add 1 to the current frequency of a word in tweet associated with current city, initialized to 0
                city_words[line.split()[0]][word] = city_words[line.split()[0]].setdefault(word, 0) + 1

    return city_freq,city_words

# Function to set the frequency as global frequency for a word not present in the bag of words for a particular city
# This function didn't do well, so commented out

#def rare_word(word):
#     if word in all_words:
#       return float(all_words[word])/sum(all_words.values())
#     else:
#       return 0.000001

# Function to clean the text

def cleaner(word_list):

     # Create a string from input list, remove punctuations from the string, change the string to lowercase
     word_text = ' '.join(word_list)
     word_text = word_text.translate(None, string.punctuation)
     #word_text = word_text.translate(None,string.punctuation.replace('@','').replace('#','').replace('$',''))
     word_text = word_text.lower()

     # Read the stopwords file into stopwords list
     file = open(stopwords_file, 'r')
     stopwords = file.read().split(',')
     file.close()

     # Remove word if word is a stopword
     word_list = [ word for word in word_text.split() if word not in stopwords ]

     # Separate numbers from string
     word_list = [''.join(each) for word in word_list for _, each in groupby(word, str.isalpha)]

     # Stemming and Lemmenting didn't help, removed nltk packages and commented out below lines
     #word_list = [ LancasterStemmer().stem(word) for word in word_list ]
     #word_list = [ WordNetLemmatizer().lemmatize(word, pos='v') for word in word_list ]

     return word_list

# Function to calculate probability (Naive Bayes Classifier)

def classify(city_freq,city_words,test_word_list):

     # Get list of cities from city_words.keys
     city_list = set(city_words.keys())

     # Create a city probability dictionary
     prob_city = {}

     for city in city_list:

         # Calculate probability of each city based on the frequency of that city / total number of cities sum(city_freq.values()
         # Prior Probability - P(city)
         prob_city[city] = float(city_freq[city])/sum(city_freq.values())

         # Initialize likelihood to 1
         p = 1

         for word in test_word_list:
             if word in city_words[city]:

                 # Calculate likelihood of each word - P(word|city) and multiply to other likelihoods
                 p = p * (float(city_words[city][word])/sum(city_words[city].values()))#/float(prob_city[city])
             else:
                # If the word is not present list of words for that city, initialize to 0.0000001 (lowest values)
                p = p * 0.0000001 #rare_word(word)#0.0000001

         # Multiply likelihood with prior and store as posterior
         # P(city|word1,word2..wordn) = P(word1|city)*P(word2|city)*..*P(wordn|city) * P(city)
         prob_city[city] =  p * prob_city[city]

     return max(prob_city, key=prob_city.get)


# Function to test the model

def tester(city_freq,city_words):

     # List of cities from testing file
     check_list_cities = []
     # List of cities from classification result
     result_list_cities = []

     with open(test_file) as file:
        for line in file.readlines():
             original_city = line.split()[0]
             check_list_cities.append(line.split()[0])
             # Store result from classificaiton and add to result_list_cities
             result = classify(city_freq,city_words,cleaner(line.split()[1:]))
             result_list_cities.append(result)
             with open(output_file,"a") as out_file:
                # Write output to output file
                out_file.write(result + " "  + original_city + " " +  line.split(' ', 1)[1])

     return check_list_cities,result_list_cities

# Function to calculate efficiency

def stats(check_list_cities,result_list_cities):
        right = 0
        wrong = 0
        for i in range(0,len(result_list_cities)):
                if check_list_cities[i] == result_list_cities[i]:
                        right += 1
                else:
                        wrong += 1
        return "Efficiency : " + str((float(right)/float(right+wrong))*100) + " %"


# Get inputs: 1.training file, 2.testing file, 3.output file
train_file = str(sys.argv[1])
test_file = str(sys.argv[2])
output_file = str(sys.argv[3])

# Choose list of stopwords to be used for cleaning data
stopwords_file = 'stopwords.large'   #takes around 18 seconds, efficiency 66.6%
#stopwords_file = 'stopwords.small'   #takes around 18 seconds, efficiency 66%
#stopwords_file = 'stopwords.xlarge'  #takes around 20.5 seconds , efficiency 66.4%
#stopwords_file = 'stopwords.xxlarge' #takes around 20.5 seconds, efficiency 66.2%
#test_file = str(sys.argv[2])


# Train the model
city_freq,city_words = trainer(train_file)

# Test the model
check_list_cities,result_list_cities = tester(city_freq,city_words)

# Calculate statistics
sol = stats(check_list_cities,result_list_cities)

# Print solution and top 5 words per city
print sol
#print city_freq
print "Top 5 words per city"
for city in set(city_words.keys()):
     print city," : ",nlargest(5, city_words[city], key=city_words[city].get)
